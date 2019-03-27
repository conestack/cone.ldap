from cone.app.browser.ajax import AjaxAction
from cone.app.browser.ajax import ajax_continue
from cone.app.browser.ajax import ajax_message
from cone.app.browser.form import Form
from cone.app.browser.form import YAMLForm
from cone.app.browser.layout import ProtectedContentTile
from cone.app.browser.settings import SettingsBehavior
from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.tile import Tile
from cone.tile import tile
from cone.ldap.model.settings import GroupsSettings
from cone.ldap.model.settings import RolesSettings
from cone.ldap.model.settings import ServerSettings
from cone.ldap.model.settings import UsersSettings
from ldap.functions import explode_dn
from node.ext.ldap import BASE
from node.ext.ldap import LDAPNode
from node.ext.ldap import ONELEVEL
from node.ext.ldap import SUBTREE
from odict import odict
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
from yafowil.base import ExtractionError
from yafowil.base import UNSET


_ = TranslationStringFactory('cone.ldap')


class VocabMixin(object):
    scope_vocab = [
        (str(BASE), 'BASE'),
        (str(ONELEVEL), 'ONELEVEL'),
        (str(SUBTREE), 'SUBTREE'),
    ]


def encode_dn(dn):
    return dn.replace('=', '%%')


def decode_dn(dn):
    return dn.replace('%%', '=')


class CreateContainerTrigger(Tile):

    @property
    def creation_dn(self):
        raise NotImplementedError(u"Abstract ``CreateContainerTrigger`` "
                                  u"does not implement ``creation_dn``")

    @property
    def creation_target(self):
        dn = encode_dn(self.creation_dn)
        query = make_query(dn=dn)
        return make_url(self.request, node=self.model, query=query)

    @property
    def ldap_connectivity(self):
        return self.model.parent['ldap_server'].ldap_connectivity


class CreateContainerAction(Tile):

    @property
    def continuation(self):
        raise NotImplementedError(u"Abstract ``CreateContainerAction`` "
                                  u"does not implement ``continuation``")

    def render(self):
        try:
            message = self.create_container()
            ajax_message(self.request, message, 'info')
            continuation = self.continuation
            ajax_continue(self.request, continuation)
        except Exception, e:
            localizer = get_localizer(self.request)
            message = localizer.translate(_(
                'cannot_create_container',
                default="Can't create container: ${error}",
                mapping={'error': str(e)}
            ))
            ajax_message(self.request, message, 'error')
        return u''

    def create_container(self):
        dn = decode_dn(self.request.params.get('dn', ''))
        localizer = get_localizer(self.request)
        if not dn:
            message = localizer.translate(_(
                'no_container_dn_defined',
                default='No container DN defined.'
            ))
            raise Exception(message)
        if not dn.startswith('ou='):
            message = localizer.translate(_(
                'expected_ou_as_rdn',
                default="Expected 'ou' as RDN Attribute."
            ))
            raise Exception(message)
        props = self.model.parent['ldap_server'].ldap_props
        try:
            parent_dn = ','.join(explode_dn(dn)[1:])
        except Exception:
            message = localizer.translate(_(
                'invalid_dn',
                default='Invalid DN.'
            ))
            raise Exception(message)
        rdn = explode_dn(dn)[0]
        node = LDAPNode(parent_dn, props)
        if node is None:
            message = localizer.translate(_(
                'parent_not_found',
                default="Parent not found. Can't continue."
            ))
            raise Exception(message)
        node[rdn] = LDAPNode()
        node[rdn].attrs['objectClass'] = ['organizationalUnit']
        node()
        self.model.invalidate()
        message = localizer.translate(_(
            'created_principal_container',
            default="Created ${rdn}",
            mapping={'rdn': rdn}
        ))
        return message


@tile(
    name='content',
    path='templates/server_settings.pt',
    interface=ServerSettings,
    permission='manage')
class ServerSettingsTile(ProtectedContentTile):

    @property
    def ldap_status(self):
        if self.model.ldap_connectivity:
            return 'OK'
        return _('server_down', default='Down')


@tile(name='editform', interface=ServerSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class ServerSettingsForm(Form):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/server_settings.yaml'

    @property
    def message_factory(self):
        return _

    def save(self, widget, data):
        model = self.model
        for attr_name in ['uri', 'user']:
            val = data.fetch('ldap_server_settings.%s' % attr_name).extracted
            setattr(model.attrs, attr_name, val)
        cache = data.fetch('ldap_server_settings.cache').extracted
        cache = str(int(cache))
        setattr(model.attrs, 'cache', cache)
        password = data.fetch('ldap_server_settings.password').extracted
        if password is not UNSET:
            setattr(model.attrs, 'password', password)
        model()
        model.invalidate()


@tile(
    name='content',
    path='templates/users_settings.pt',
    interface=UsersSettings,
    permission='manage')
class UsersSettingsTile(ProtectedContentTile, CreateContainerTrigger):

    @property
    def creation_dn(self):
        return self.model.attrs.users_dn

    @property
    def ldap_users(self):
        if self.model.ldap_users_container_valid:
            return 'OK'
        return _('inexistent', default='Inexistent')


@tile(name='create_container', interface=UsersSettings, permission='manage')
class UsersCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ldap_users')


@tile(name='editform', interface=UsersSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class UsersSettingsForm(Form, VocabMixin):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/users_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def users_aliases_attrmap(self):
        attrs = self.model.attrs
        users_aliases_attrmap = odict()
        users_aliases_attrmap['rdn'] = attrs.users_aliases_attrmap.get('rdn')
        users_aliases_attrmap['id'] = attrs.users_aliases_attrmap.get('id')
        users_aliases_attrmap['login'] = \
            attrs.users_aliases_attrmap.get('login')
        return users_aliases_attrmap

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'users_dn',
            'users_scope',
            'users_query',
            'users_object_classes',
            'users_aliases_attrmap',
            'users_form_attrmap',
            'users_listing_columns',
            'users_listing_default_column',
            'users_exposed_attributes'
        ]:
            val = data.fetch('ldap_users_settings.%s' % attr_name).extracted
            if attr_name == 'users_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()


@tile(
    name='content',
    path='templates/groups_settings.pt',
    interface=GroupsSettings,
    permission='manage')
class GroupsSettingsTile(ProtectedContentTile, CreateContainerTrigger):

    @property
    def creation_dn(self):
        return self.model.attrs.groups_dn

    @property
    def ldap_groups(self):
        if self.model.ldap_groups_container_valid:
            return 'OK'
        return _('inexistent', default='Inexistent')


@tile(name='create_container', interface=GroupsSettings, permission='manage')
class GroupsCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ldap_groups')


@tile(name='editform', interface=GroupsSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class GroupsSettingsForm(Form, VocabMixin):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/groups_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def groups_aliases_attrmap(self):
        attrs = self.model.attrs
        groups_aliases_attrmap = odict()
        groups_aliases_attrmap['rdn'] = attrs.groups_aliases_attrmap.get('rdn')
        groups_aliases_attrmap['id'] = attrs.groups_aliases_attrmap.get('id')
        return groups_aliases_attrmap

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'groups_dn',
            'groups_scope',
            'groups_query',
            'groups_object_classes',
            'groups_aliases_attrmap',
            'groups_form_attrmap',
            # 'groups_relation',
            'groups_listing_columns',
            'groups_listing_default_column'
        ]:
            val = data.fetch('ldap_groups_settings.%s' % attr_name).extracted
            if attr_name == 'groups_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()


@tile(
    name='content',
    path='templates/roles_settings.pt',
    interface=RolesSettings,
    permission='manage')
class RolesSettingsTile(ProtectedContentTile, CreateContainerTrigger):

    @property
    def creation_dn(self):
        return self.model.attrs.roles_dn

    @property
    def ldap_roles(self):
        if self.model.ldap_roles_container_valid:
            return 'OK'
        return _('inexistent', default='Inexistent')


@tile(name='create_container', interface=RolesSettings, permission='manage')
class RolesCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ldap_roles')


@tile(name='editform', interface=RolesSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class RolesSettingsForm(Form, VocabMixin):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/roles_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def roles_aliases_attrmap(self):
        attrs = self.model.attrs
        roles_aliases_attrmap = odict()
        roles_aliases_attrmap['rdn'] = attrs.roles_aliases_attrmap.get('rdn')
        roles_aliases_attrmap['id'] = attrs.roles_aliases_attrmap.get('id')
        return roles_aliases_attrmap

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'roles_dn',
            'roles_scope',
            'roles_query',
            'roles_object_classes',
            'roles_aliases_attrmap',
            'roles_form_attrmap',
            # 'roles_relation',
        ]:
            val = data.fetch('ldap_roles_settings.%s' % attr_name).extracted
            if attr_name == 'roles_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()

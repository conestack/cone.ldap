from cone.app.browser.ajax import ajax_continue
from cone.app.browser.ajax import ajax_message
from cone.app.browser.ajax import AjaxAction
from cone.app.browser.form import Form
from cone.app.browser.form import YAMLForm
from cone.app.browser.layout import ProtectedContentTile
from cone.app.browser.settings import SettingsBehavior
from cone.app.browser.utils import make_url
from cone.app.ugm import ugm_backend
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from cone.tile import Tile
from cone.tile import tile
from node.ext.ldap import BASE
from node.ext.ldap import ONELEVEL
from node.ext.ldap import SUBTREE
from node.utils import UNSET
from odict import odict
from plumber import plumbing
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('cone.ldap')


def initialize_ugm_backend():
    if ugm_backend.name == 'ldap':
        ugm_backend.initialize()


class ScopeVocabMixin(object):
    scope_vocab = [
        (str(BASE), 'BASE'),
        (str(ONELEVEL), 'ONELEVEL'),
        (str(SUBTREE), 'SUBTREE'),
    ]


class CreateContainerTrigger(Tile):

    @property
    def creation_target(self):
        return make_url(self.request, node=self.model)

    @property
    def ldap_connectivity(self):
        return self.model.parent['ldap_server'].ldap_connectivity


class CreateContainerAction(Tile):

    @property
    def continuation(self):
        raise NotImplementedError(
            'Abstract ``CreateContainerAction`` '
            'does not implement ``continuation``'
        )

    def render(self):
        try:
            message = self.model.create_container()
            ajax_message(self.request, message, 'info')
            continuation = self.continuation
            ajax_continue(self.request, continuation)
        except Exception as e:
            localizer = get_localizer(self.request)
            message = localizer.translate(_(
                'cannot_create_container',
                default="Cannot create container: ${error}",
                mapping={'error': localizer.translate(e.error_message)}
            ))
            ajax_message(self.request, message, 'error')
        # XXX: initialize UGM backend?
        return u''


@tile(
    name='content',
    path='templates/server_settings.pt',
    interface=LDAPServerSettings,
    permission='manage')
class ServerSettingsTile(ProtectedContentTile):

    @property
    def ldap_status(self):
        if self.model.ldap_connectivity:
            return 'OK'
        return _('server_down', default='Down')


@tile(name='editform', interface=LDAPServerSettings, permission='manage')
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
        initialize_ugm_backend()


@tile(
    name='content',
    path='templates/users_settings.pt',
    interface=LDAPUsersSettings,
    permission='manage')
class UsersSettingsTile(ProtectedContentTile, CreateContainerTrigger):

    @property
    def ldap_users(self):
        if self.model.container_exists:
            return 'OK'
        return _('inexistent', default='Inexistent')


@tile(name='create_container', interface=LDAPUsersSettings, permission='manage')
class UsersCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ldap_users')


@tile(name='editform', interface=LDAPUsersSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class UsersSettingsForm(Form, ScopeVocabMixin):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/users_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def users_aliases_attrmap(self):
        attrs = self.model.attrs
        users_aliases_attrmap = odict()
        for attr_name in ['rdn', 'id', 'password']:
            value = attrs.users_aliases_attrmap.get(attr_name)
            users_aliases_attrmap[attr_name] = value
        return users_aliases_attrmap

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'users_dn',
            'users_scope',
            'users_query',
            'users_object_classes',
            'users_aliases_attrmap'
        ]:
            val = data.fetch('ldap_users_settings.%s' % attr_name).extracted
            if attr_name == 'users_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()
        initialize_ugm_backend()


@tile(
    name='content',
    path='templates/groups_settings.pt',
    interface=LDAPGroupsSettings,
    permission='manage')
class GroupsSettingsTile(ProtectedContentTile, CreateContainerTrigger):

    @property
    def ldap_groups(self):
        if self.model.container_exists:
            return 'OK'
        return _('inexistent', default='Inexistent')


@tile(name='create_container', interface=LDAPGroupsSettings, permission='manage')
class GroupsCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ldap_groups')


@tile(name='editform', interface=LDAPGroupsSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class GroupsSettingsForm(Form, ScopeVocabMixin):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/groups_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def groups_aliases_attrmap(self):
        attrs = self.model.attrs
        groups_aliases_attrmap = odict()
        for attr_name in ['rdn', 'id']:
            value = attrs.groups_aliases_attrmap.get(attr_name)
            groups_aliases_attrmap[attr_name] = value
        return groups_aliases_attrmap

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'groups_dn',
            'groups_scope',
            'groups_query',
            'groups_object_classes',
            'groups_aliases_attrmap'
            # 'groups_relation'
        ]:
            val = data.fetch('ldap_groups_settings.%s' % attr_name).extracted
            if attr_name == 'groups_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()
        initialize_ugm_backend()


@tile(
    name='content',
    path='templates/roles_settings.pt',
    interface=LDAPRolesSettings,
    permission='manage')
class RolesSettingsTile(ProtectedContentTile, CreateContainerTrigger):

    @property
    def ldap_roles(self):
        if self.model.container_exists:
            return 'OK'
        return _('inexistent', default='Inexistent')


@tile(name='create_container', interface=LDAPRolesSettings, permission='manage')
class RolesCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ldap_roles')


@tile(name='editform', interface=LDAPRolesSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class RolesSettingsForm(Form, ScopeVocabMixin):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/roles_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def roles_aliases_attrmap(self):
        attrs = self.model.attrs
        roles_aliases_attrmap = odict()
        for attr_name in ['rdn', 'id']:
            value = attrs.roles_aliases_attrmap.get(attr_name)
            roles_aliases_attrmap[attr_name] = value
        return roles_aliases_attrmap

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'roles_dn',
            'roles_scope',
            'roles_query',
            'roles_object_classes',
            'roles_aliases_attrmap'
            # 'roles_relation',
        ]:
            val = data.fetch('ldap_roles_settings.%s' % attr_name).extracted
            if attr_name == 'roles_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()
        initialize_ugm_backend()

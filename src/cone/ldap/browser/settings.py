from cone.app.browser.ajax import AjaxEvent
from cone.app.browser.ajax import ajax_continue
from cone.app.browser.ajax import ajax_message
from cone.app.browser.form import Form
from cone.app.browser.form import YAMLForm
from cone.app.browser.settings import SettingsForm
from cone.app.browser.settings import settings_form
from cone.app.browser.utils import make_url
from cone.app.ugm import ugm_backend
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from cone.tile import Tile
from cone.tile import tile
from cone.ugm.utils import general_settings
from node.ext.ldap import BASE
from node.ext.ldap import ONELEVEL
from node.ext.ldap import SUBTREE
from node.utils import UNSET
from odict import odict
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from yafowil.base import ExtractionError


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


@tile(name='create_container', interface=LDAPUsersSettings, permission='manage')
@tile(name='create_container', interface=LDAPGroupsSettings, permission='manage')
@tile(name='create_container', interface=LDAPRolesSettings, permission='manage')
class CreateContainerAction(Tile):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxEvent(url, 'contextchanged', '#layout')

    def render(self):
        localizer = get_localizer(self.request)
        try:
            message = localizer.translate(self.model.create_container())
            ajax_message(self.request, message, 'info')
            continuation = self.continuation
            ajax_continue(self.request, continuation)
        except Exception as e:
            message = localizer.translate(_(
                'cannot_create_container',
                default="Cannot create container: ${error}",
                mapping={'error': localizer.translate(e.error_message)}
            ))
            ajax_message(self.request, message, 'error')
        # XXX: initialize UGM backend?
        return u''


class AliasesMixin(object):
    reserved_alias_names = []
    aliases_attribute = ''

    @property
    def reserved_aliases_value(self):
        attrs = self.model.attrs
        value = getattr(attrs, self.aliases_attribute)
        reserved_aliases = odict()
        for attr_name in self.reserved_alias_names:
            reserved_aliases[attr_name] = value.get(attr_name)
        return reserved_aliases

    @property
    def additional_aliases_value(self):
        attrs = self.model.attrs
        value = getattr(attrs, self.aliases_attribute)
        additional_aliases = odict()
        for attr_name in value.keys():
            if attr_name in self.reserved_alias_names:
                continue
            additional_aliases[attr_name] = value.get(attr_name)
        return additional_aliases

    def additional_aliases_extractor(self, widget, data):
        extracted = data.extracted
        if extracted is UNSET:
            return extracted
        for val in extracted.values():
            if not val.strip():
                raise ExtractionError(_(
                    'additional_aliases_empty_string',
                    default='Additional aliases must not be empty'
                ))
        return extracted


@settings_form(
    interface=LDAPServerSettings,
    path='cone.ldap.browser:templates/server_settings.pt')
@plumbing(SettingsForm, YAMLForm)
class ServerSettingsForm(Form):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/server_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def ldap_status(self):
        if self.model.ldap_connectivity:
            return 'OK'
        return _('server_down', default='Down')

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


@settings_form(
    interface=LDAPUsersSettings,
    path='cone.ldap.browser:templates/users_settings.pt')
@plumbing(SettingsForm, YAMLForm)
class UsersSettingsForm(Form, ScopeVocabMixin, AliasesMixin, CreateContainerTrigger):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/users_settings.yaml'
    reserved_alias_names = ['rdn', 'id', 'password']
    aliases_attribute = 'users_aliases_attrmap'

    @property
    def message_factory(self):
        return _

    @property
    def ldap_users(self):
        if self.model.container_exists:
            return 'OK'
        return _('inexistent', default='Inexistent')

    def required_if_users_account_expiration(self, widget, data):
        extracted = data.extracted
        if extracted is UNSET:
            return extracted
        settings = general_settings(self.model)
        if settings.attrs.users_account_expiration == 'True' and not extracted:
            raise ExtractionError(_(
                'required_if_users_account_expiration',
                default='Value is required if account expiration is enabled'
            ))
        return extracted

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'users_dn',
            'users_scope',
            'users_query',
            'users_object_classes',
            'users_expires_attr',
            'users_expires_unit'
        ]:
            val = data.fetch('ldap_users_settings.%s' % attr_name).extracted
            if attr_name == 'users_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        attr_map = data.fetch('ldap_users_settings.users_additional_aliases').extracted
        attr_map.update(data.fetch('ldap_users_settings.users_reserved_aliases').extracted)
        model.attrs.users_aliases_attrmap = attr_map
        model()
        model.invalidate()
        initialize_ugm_backend()


@settings_form(
    interface=LDAPGroupsSettings,
    path='cone.ldap.browser:templates/groups_settings.pt')
@plumbing(SettingsForm, YAMLForm)
class GroupsSettingsForm(Form, ScopeVocabMixin, AliasesMixin, CreateContainerTrigger):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/groups_settings.yaml'
    reserved_alias_names = ['rdn', 'id']
    aliases_attribute = 'groups_aliases_attrmap'

    @property
    def message_factory(self):
        return _

    @property
    def ldap_groups(self):
        if self.model.container_exists:
            return 'OK'
        return _('inexistent', default='Inexistent')

    def save(self, widget, data):
        model = self.model
        for attr_name in [
            'groups_dn',
            'groups_scope',
            'groups_query',
            'groups_object_classes'
            # 'groups_relation'
        ]:
            val = data.fetch('ldap_groups_settings.%s' % attr_name).extracted
            if attr_name == 'groups_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        attr_map = data.fetch('ldap_groups_settings.groups_additional_aliases').extracted
        attr_map.update(data.fetch('ldap_groups_settings.groups_reserved_aliases').extracted)
        model.attrs.groups_aliases_attrmap = attr_map
        model()
        model.invalidate()
        initialize_ugm_backend()


@settings_form(
    interface=LDAPRolesSettings,
    path='cone.ldap.browser:templates/roles_settings.pt')
@plumbing(SettingsForm, YAMLForm)
class RolesSettingsForm(Form, ScopeVocabMixin, CreateContainerTrigger):
    action_resource = u'edit'
    form_template = 'cone.ldap.browser:forms/roles_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def ldap_roles(self):
        if self.model.container_exists:
            return 'OK'
        return _('inexistent', default='Inexistent')

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

from cone.app.model import BaseNode
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.app.model import XMLProperties
from cone.ugm.model import factory_defaults
from node.ext.ldap import LDAPNode
from node.ext.ldap import LDAPProps
from node.ext.ldap import testLDAPConnectivity
from node.ext.ldap.ugm import GroupsConfig
from node.ext.ldap.ugm import RolesConfig
from node.ext.ldap.ugm import UsersConfig
from node.ext.ldap.ugm._api import EXPIRATION_DAYS
from node.utils import instance_property
from pyramid.i18n import TranslationStringFactory
import ldap
import os


_ = TranslationStringFactory('cone.ldap')


# settings config
ldap_cfg = Properties()

# gets set by main hook
ldap_cfg.server_config = ''
ldap_cfg.users_config = ''
ldap_cfg.groups_config = ''
ldap_cfg.roles_config = ''


class XMLSettings(BaseNode):
    config_file = None

    def __call__(self):
        self.attrs()

    @instance_property
    def attrs(self):
        config_file = self.config_file
        if not os.path.isfile(config_file):
            msg = 'LDAP configuration {} does not exist.'.format(config_file)
            raise ValueError(msg)
        return XMLProperties(config_file)

    def invalidate(self, attrs=[]):
        attrs.append('attrs')
        for attr in attrs:
            _attr = '_{}'.format(attr)
            if hasattr(self, _attr):
                delattr(self, _attr)


########################
# XXX: move to cone.ugm

# users_aliases_attrmap user.py

ugm_cfg = Properties()
ugm_cfg.ugm_settings = ''


class UGMGeneralSettings(XMLSettings):

    @property
    def config_file(self):
        return ugm_cfg.ugm_settings

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'ugm_settings_node',
            default='UGM Settings')
        metadata.description = _(
            'ugm_settings_node_description',
            default='General user and group management settings'
        )
        return metadata
# XXX: end move to cone.ugm
###########################


class LDAPServerSettings(XMLSettings):

    @property
    def config_file(self):
        return ldap_cfg.server_config

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'server_settings_node',
            default='LDAP Server'
        )
        metadata.description = _(
            'server_settings_node_description',
            default='General LDAP Server Settings'
        )
        return metadata

    @property
    def ldap_connectivity(self):
        try:
            props = self.ldap_props
        except ValueError:
            return False
        return testLDAPConnectivity(props=props) == 'success'

    @instance_property
    def ldap_props(self):
        config = self.attrs
        return LDAPProps(
            uri=config.uri,
            user=config.user,
            password=config.password,
            cache=int(config.cache)
        )

    def invalidate(self):
        super(LDAPServerSettings, self).invalidate(attrs=['ldap_props'])


class LDAPUsersSettings(XMLSettings):

    @property
    def config_file(self):
        return ldap_cfg.users_config

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'user_settings_node',
            default='LDAP Users'
        )
        metadata.description = _(
            'user_settings_node_description',
            default='User specific LDAP Settings'
        )
        return metadata

    @property
    def ldap_users_container_valid(self):
        try:
            return LDAPNode(
                self.attrs.users_dn,
                self.parent['ugm_server'].ldap_props
            ).exists
        except ldap.LDAPError:
            return False

    @instance_property
    def ldap_ucfg(self):
        config = self.attrs
        map = dict()
        for key in config.users_aliases_attrmap.keys():
            map[key] = config.users_aliases_attrmap[key]
        for key in config.users_form_attrmap.keys():
            if key in ['id', 'login']:
                continue
            map[key] = key
        if config.users_exposed_attributes:
            for key in config.users_exposed_attributes:
                map[key] = key
        expiresAttr = None
        expiresUnit = EXPIRATION_DAYS
        # from general settings. be aware that all config options are
        # currently available on ``self.attrs``. This might change in
        # future and below settings must be read from general settings
        # then.
        if config.users_account_expiration == 'True':
            expiresAttr = config.users_expires_attr
            expiresUnit = int(config.users_expires_unit)
            map[expiresAttr] = expiresAttr
        if config.users_portrait == 'True':
            imageAttr = config.users_portrait_attr
            map[imageAttr] = imageAttr
        return UsersConfig(
            baseDN=config.users_dn,
            attrmap=map,
            scope=int(config.users_scope),
            queryFilter=config.users_query,
            objectClasses=config.users_object_classes,
            defaults=factory_defaults.user,
            expiresAttr=expiresAttr,
            expiresUnit=expiresUnit
        )

    def invalidate(self):
        super(LDAPUsersSettings, self).invalidate(attrs=['ldap_ucfg'])


class LDAPGroupsSettings(XMLSettings):

    @property
    def config_file(self):
        return ldap_cfg.groups_config

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'group_settings_node',
            default='LDAP Groups')
        metadata.description = _(
            'group_settings_node_description',
            default='Group specific LDAP Settings'
        )
        return metadata

    @property
    def ldap_groups_container_valid(self):
        try:
            return LDAPNode(
                self.attrs.groups_dn,
                self.parent['ugm_server'].ldap_props
            ).exists
        except ldap.LDAPError:
            return False

    @property
    def ldap_gcfg(self):
        config = self.attrs
        map = dict()
        for key in config.groups_aliases_attrmap.keys():
            map[key] = config.groups_aliases_attrmap[key]
        for key in config.groups_form_attrmap.keys():
            if key in ['id']:
                continue
            map[key] = key
        return GroupsConfig(
            baseDN=config.groups_dn,
            attrmap=map,
            scope=int(config.groups_scope),
            queryFilter=config.groups_query,
            objectClasses=config.groups_object_classes,
            # member_relation=config.groups_relation,
            defaults=factory_defaults.group
        )

    def invalidate(self):
        super(LDAPGroupsSettings, self).invalidate(attrs=['ldap_gcfg'])


class LDAPRolesSettings(XMLSettings):

    @property
    def config_file(self):
        return ldap_cfg.roles_config

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'role_settings_node',
            default='LDAP Roles')
        metadata.description = _(
            'role_settings_node_description',
            default='Role specific LDAP Settings'
        )
        return metadata

    @property
    def ldap_roles_container_valid(self):
        try:
            return LDAPNode(
                self.attrs.roles_dn,
                self.parent['ugm_server'].ldap_props
            ).exists
        except ldap.LDAPError:
            return False

    @property
    def ldap_rcfg(self):
        config = self.attrs
        map = dict()
        for key in config.roles_aliases_attrmap.keys():
            map[key] = config.roles_aliases_attrmap[key]
        for key in config.roles_form_attrmap.keys():
            if key in ['id']:
                continue
            map[key] = key
        self._ldap_rcfg = RolesConfig(
            baseDN=config.roles_dn,
            attrmap=map,
            scope=int(config.roles_scope),
            queryFilter=config.roles_query,
            objectClasses=config.roles_object_classes,
            # member_relation=config.roles_relation,
            defaults=factory_defaults.role
        )

    def invalidate(self):
        super(LDAPRolesSettings, self).invalidate(attrs=['ldap_rcfg'])

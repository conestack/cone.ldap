from cone.app.model import Metadata
from cone.app.model import Properties
from cone.app.utils import format_traceback
from cone.ugm.settings import UGMSettings
from cone.ugm.utils import general_settings
from ldap.functions import explode_dn
from node.ext.ldap import LDAPNode
from node.ext.ldap import LDAPProps
from node.ext.ldap import testLDAPConnectivity
from node.ext.ldap.ugm import GroupsConfig
from node.ext.ldap.ugm import RolesConfig
from node.ext.ldap.ugm import UsersConfig
from node.ext.ldap.ugm._api import EXPIRATION_DAYS
from node.utils import instance_property
from odict import odict
from pyramid.i18n import TranslationStringFactory
import logging


logger = logging.getLogger('cone.ldap')
_ = TranslationStringFactory('cone.ldap')


# settings config
ldap_cfg = Properties()

# gets set by main hook
ldap_cfg.server_config = ''
ldap_cfg.users_config = ''
ldap_cfg.groups_config = ''
ldap_cfg.roles_config = ''

# user and group factory defaults
factory_defaults = Properties()
factory_defaults.user = dict()
factory_defaults.group = dict()
factory_defaults.role = dict()


class LDAPServerSettings(UGMSettings):

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
        except Exception:
            logger.error(format_traceback())
            return False
        return testLDAPConnectivity(props=props) == 'success'

    @instance_property
    def ldap_props(self):
        settings = self.attrs
        return LDAPProps(
            uri=settings.uri,
            user=settings.user,
            password=settings.password,
            cache=int(settings.cache)
        )

    def invalidate(self):
        super(LDAPServerSettings, self).invalidate(attrs=['ldap_props'])


class LDAPContainerError(Exception):
    """Error thrown if creating a LDAP container fails.

    ``error_message`` containes a translation string.
    """

    def __init__(self, error_message):
        super(LDAPContainerError, self).__init__()
        self.error_message = error_message


class LDAPContainerSettings(UGMSettings):
    container_dn = None

    @property
    def server_settings(self):
        return self.root['settings']['ldap_server']

    @property
    def container_exists(self):
        try:
            return LDAPNode(
                self.container_dn,
                self.server_settings.ldap_props
            ).exists
        except Exception:
            logger.error(format_traceback())
            return False

    def create_container(self):
        """Create LDAP container by dn.

        Currently this only supports ou container type.

        XXX: Do we need to support c and dc?
        XXX: Should we create parents as well if missing?
        """
        dn = self.container_dn
        if not dn:
            raise LDAPContainerError(_(
                'no_container_dn_defined',
                default='No container DN defined.'
            ))
        if not dn.startswith('ou='):
            raise LDAPContainerError(_(
                'expected_ou_as_rdn',
                default="Expected 'ou' as RDN Attribute."
            ))
        props = self.server_settings.ldap_props
        try:
            parent_dn = ','.join(explode_dn(dn)[1:])
        except Exception:
            raise LDAPContainerError(_(
                'invalid_dn',
                default='Invalid DN.'
            ))
        rdn = explode_dn(dn)[0]
        parent = LDAPNode(parent_dn, props)
        if not parent.exists:
            raise LDAPContainerError(_(
                'parent_not_found',
                default="Parent not found. Can't continue."
            ))
        parent[rdn] = LDAPNode()
        parent[rdn].attrs['objectClass'] = ['organizationalUnit']
        parent()
        self.invalidate()
        message = _(
            'created_principal_container',
            default="Created ${rdn}",
            mapping={'rdn': rdn}
        )
        return message


class LDAPUsersSettings(LDAPContainerSettings):

    @property
    def config_file(self):
        return ldap_cfg.users_config

    @property
    def container_dn(self):
        return self.attrs.users_dn

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

    @instance_property
    def ldap_ucfg(self):
        ugm_settings = general_settings(self).attrs
        settings = self.attrs
        attr_map = odict(settings.users_aliases_attrmap.items())
        attr_map.update(ugm_settings.users_reserved_attrs)
        for attr in ugm_settings.users_form_attrmap:
            if attr in ugm_settings.users_reserved_attrs:
                continue
            attr_map[attr] = attr
        if ugm_settings.users_exposed_attributes:
            for attr in ugm_settings.users_exposed_attributes:
                attr_map[attr] = attr
        expires_attr = None
        expires_unit = EXPIRATION_DAYS
        if ugm_settings.users_account_expiration == 'True':
            expires_attr = ugm_settings.users_expires_attr
            expires_unit = int(ugm_settings.users_expires_unit)
            attr_map[expires_attr] = expires_attr
        if ugm_settings.users_portrait == 'True':
            image_attr = ugm_settings.users_portrait_attr
            attr_map[image_attr] = image_attr
        return UsersConfig(
            baseDN=settings.users_dn,
            attrmap=attr_map,
            scope=int(settings.users_scope),
            queryFilter=settings.users_query,
            objectClasses=settings.users_object_classes,
            defaults=factory_defaults.user,
            expiresAttr=expires_attr,
            expiresUnit=expires_unit
        )

    def invalidate(self):
        super(LDAPUsersSettings, self).invalidate(attrs=['ldap_ucfg'])


class LDAPGroupsSettings(LDAPContainerSettings):

    @property
    def config_file(self):
        return ldap_cfg.groups_config

    @property
    def container_dn(self):
        return self.attrs.groups_dn

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

    @instance_property
    def ldap_gcfg(self):
        ugm_settings = general_settings(self).attrs
        settings = self.attrs
        attr_map = odict(settings.groups_aliases_attrmap.items())
        attr_map.update(ugm_settings.groups_reserved_attrs)
        for attr in ugm_settings.groups_form_attrmap:
            if attr in ugm_settings.groups_reserved_attrs:
                continue
            attr_map[attr] = attr
        return GroupsConfig(
            baseDN=settings.groups_dn,
            attrmap=attr_map,
            scope=int(settings.groups_scope),
            queryFilter=settings.groups_query,
            objectClasses=settings.groups_object_classes,
            # member_relation=settings.groups_relation,
            defaults=factory_defaults.group
        )

    def invalidate(self):
        super(LDAPGroupsSettings, self).invalidate(attrs=['ldap_gcfg'])


class LDAPRolesSettings(LDAPContainerSettings):

    @property
    def config_file(self):
        return ldap_cfg.roles_config

    @property
    def container_dn(self):
        return self.attrs.roles_dn

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

    @instance_property
    def ldap_rcfg(self):
        settings = self.attrs
        attr_map = odict(settings.roles_aliases_attrmap.items())
        return RolesConfig(
            baseDN=settings.roles_dn,
            attrmap=attr_map,
            scope=int(settings.roles_scope),
            queryFilter=settings.roles_query,
            objectClasses=settings.roles_object_classes,
            # member_relation=settings.roles_relation,
            defaults=factory_defaults.role
        )

    def invalidate(self):
        super(LDAPRolesSettings, self).invalidate(attrs=['ldap_rcfg'])

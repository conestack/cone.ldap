from cone.app import get_root
from cone.ldap import testing
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from cone.ldap.settings import UGMGeneralSettings
from node.ext.ldap import LDAPProps
from node.ext.ldap.ugm import GroupsConfig
from node.ext.ldap.ugm import RolesConfig
from node.ext.ldap.ugm import UsersConfig
from node.tests import NodeTestCase


class TestSettings(NodeTestCase):
    layer = testing.ldap_layer

    #######################
    # XXX: move to cone.ugm

    def test_UGMGeneralSettings(self):
        root = get_root()
        settings = root['settings']['ugm']
        self.assertTrue(isinstance(settings, UGMGeneralSettings))
        self.assertEqual(sorted(settings.attrs.keys()), [
            'groups_form_attrmap',
            'groups_listing_columns',
            'groups_listing_default_column',
            'user_id_autoincrement',
            'user_id_autoincrement_prefix',
            'user_id_autoincrement_start',
            'users_account_expiration',
            'users_expires_attr',
            'users_expires_unit',
            'users_exposed_attributes',
            'users_form_attrmap',
            'users_listing_columns',
            'users_listing_default_column',
            'users_local_management_enabled',
            'users_portrait',
            'users_portrait_accept',
            'users_portrait_attr',
            'users_portrait_height',
            'users_portrait_width'
        ])

    # XXX: end move to cone.ugm
    ###########################

    def test_LDAPGroupsSettings(self):
        root = get_root()
        settings = root['settings']['ldap_groups']
        self.assertTrue(isinstance(settings, LDAPGroupsSettings))
        self.assertEqual(sorted(settings.attrs.keys()), [
            'groups_aliases_attrmap',
            'groups_dn',
            'groups_object_classes',
            'groups_query',
            'groups_relation',
            'groups_scope'
        ])
        self.assertEqual(isinstance(settings.ldap_gcfg, GroupsConfig), True)

    def test_LDAPRolesSettings(self):
        root = get_root()
        settings = root['settings']['ldap_roles']
        self.assertTrue(isinstance(settings, LDAPRolesSettings))
        self.assertEqual(sorted(settings.attrs.keys()), [
            'roles_aliases_attrmap',
            'roles_dn',
            'roles_object_classes',
            'roles_query',
            'roles_relation',
            'roles_scope'
        ])
        self.assertEqual(isinstance(settings.ldap_rcfg, RolesConfig), True)

    def test_LDAPServerSettings(self):
        root = get_root()
        settings = root['settings']['ldap_server']
        self.assertTrue(isinstance(settings, LDAPServerSettings))
        self.assertEqual(sorted(settings.attrs.keys()), [
            'cache',
            'password',
            'uri',
            'user'
        ])
        self.assertEqual(isinstance(settings.ldap_props, LDAPProps), True)

    def test_LDAPUsersSettings(self):
        root = get_root()
        settings = root['settings']['ldap_users']
        self.assertTrue(isinstance(settings, LDAPUsersSettings))
        self.assertEqual(sorted(settings.attrs.keys()), [
            'users_aliases_attrmap',
            'users_dn',
            'users_object_classes',
            'users_query',
            'users_scope'
        ])
        self.assertEqual(isinstance(settings.ldap_ucfg, UsersConfig), True)

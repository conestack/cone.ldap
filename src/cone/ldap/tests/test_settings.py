from cone.app import get_root
from cone.ldap import testing
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from cone.ldap.settings import UGMGeneralSettings
from node.tests import NodeTestCase


class TestSettings(NodeTestCase):
    layer = testing.ldap_layer

    def test_UGMGeneralSettings(self):
        root = get_root()
        settings = root['settings']['ugm']
        self.assertTrue(isinstance(settings, UGMGeneralSettings))

    def test_LDAPGroupsSettings(self):
        root = get_root()
        settings = root['settings']['ldap_groups']
        self.assertTrue(isinstance(settings, LDAPGroupsSettings))

    def test_LDAPRolesSettings(self):
        root = get_root()
        settings = root['settings']['ldap_roles']
        self.assertTrue(isinstance(settings, LDAPRolesSettings))

    def test_LDAPServerSettings(self):
        root = get_root()
        settings = root['settings']['ldap_server']
        self.assertTrue(isinstance(settings, LDAPServerSettings))

    def test_LDAPUsersSettings(self):
        root = get_root()
        settings = root['settings']['ldap_users']
        self.assertTrue(isinstance(settings, LDAPUsersSettings))

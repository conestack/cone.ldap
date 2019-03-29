from cone.app import get_root
from cone.ldap import testing
from cone.ldap.settings import ldap_cfg
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from node.tests import NodeTestCase


class TestLdap(NodeTestCase):
    layer = testing.ldap_layer

    def test_main_hook(self):
        root = get_root()
        settings = root['settings']

        self.assertTrue(isinstance(settings['ldap_groups'], LDAPGroupsSettings))
        self.assertTrue(isinstance(settings['ldap_roles'], LDAPRolesSettings))
        self.assertTrue(isinstance(settings['ldap_server'], LDAPServerSettings))
        self.assertTrue(isinstance(settings['ldap_users'], LDAPUsersSettings))

        self.assertTrue(ldap_cfg.server_config.endswith('ldap_server.xml') > -1)
        self.assertTrue(ldap_cfg.users_config.endswith('ldap_users.xml') > -1)
        self.assertTrue(ldap_cfg.groups_config.endswith('ldap_groups.xml') > -1)
        self.assertTrue(ldap_cfg.roles_config.endswith('ldap_roles.xml') > -1)

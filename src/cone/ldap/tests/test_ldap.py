from cone.app import get_root
from cone.ldap import LDAPUGMFactory
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

    @testing.invalidate_settings
    def test_ugm_factory_without_ldap_connectivity(self):
        settings = get_root()['settings']
        settings['ldap_server'].attrs.uri = ''
        with self.assertLogs('cone.ldap', level='ERROR') as logs:
            self.assertIsNone(LDAPUGMFactory({})())
        self.assertIn('LDAP Server is not available', logs.output[0])

    @testing.invalidate_settings
    def test_ugm_factory_without_groups_and_roles_container(self):
        settings = get_root()['settings']
        inexistent_dn = 'ou=inexistent,dc=my-domain,dc=com'
        settings['ldap_groups'].attrs.groups_dn = inexistent_dn
        settings['ldap_roles'].attrs.roles_dn = inexistent_dn
        with self.assertLogs('cone.ldap', level='WARNING') as logs:
            ugm = LDAPUGMFactory({})()
        self.assertEqual(ugm.name, 'ldap_ugm')
        self.assertEqual(
            [r.getMessage() for r in logs.records][-2:],
            [
                'Configured groups container invalid.',
                'Configured roles container invalid.',
            ],
        )

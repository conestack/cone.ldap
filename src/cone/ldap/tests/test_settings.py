from cone.app import get_root
from cone.ldap import testing
from cone.ldap.settings import LDAPContainerError
from cone.ldap.settings import LDAPContainerSettings
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from node.ext.ldap import LDAPProps
from node.ext.ldap.ugm import GroupsConfig
from node.ext.ldap.ugm import RolesConfig
from node.ext.ldap.ugm import UsersConfig
from node.tests import NodeTestCase


class TestSettings(NodeTestCase):
    layer = testing.ldap_layer

    @testing.invalidate_settings
    def test_LDAPServerSettings(self):
        settings = get_root()['settings']['ldap_server']

        self.assertTrue(isinstance(settings, LDAPServerSettings))

        md = settings.metadata
        self.assertEqual(md.title, 'server_settings_node')
        self.assertEqual(md.description, 'server_settings_node_description')

        attrs = settings.attrs
        self.assertEqual(sorted(attrs.keys()), [
            'cache',
            'password',
            'uri',
            'user'
        ])

        attrs.uri = 'ldap://127.0.0.1:12345'
        attrs.user = 'cn=Manager,dc=my-domain,dc=com'
        attrs.password = 'secret'
        attrs.cache = '0'

        ldap_props = settings.ldap_props
        self.assertEqual(isinstance(ldap_props, LDAPProps), True)
        self.assertEqual(ldap_props.uri, attrs.uri)
        self.assertEqual(ldap_props.user, attrs.user)
        self.assertEqual(ldap_props.password, attrs.password)
        self.assertEqual(ldap_props.cache, int(attrs.cache))

        self.assertTrue(settings.attrs is attrs)
        self.assertTrue(settings.ldap_props is ldap_props)
        settings.invalidate()
        self.assertFalse(settings.attrs is attrs)
        self.assertFalse(settings.ldap_props is ldap_props)

        settings.invalidate()
        self.assertTrue(settings.ldap_connectivity)

        settings.invalidate()
        settings.attrs.uri = ''
        self.assertFalse(settings.ldap_connectivity)

        settings.invalidate()
        settings.attrs.cache = None
        self.assertFalse(settings.ldap_connectivity)

    def test_LDAPContainerSettings(self):
        settings = LDAPContainerSettings()
        settings.__parent__ = get_root()['settings']

        self.assertTrue(isinstance(
            settings.server_settings,
            LDAPServerSettings
        ))

        settings.container_dn = None
        err = self.expectError(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'no_container_dn_defined')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'uid=foo,dc=my-domain,dc=com'
        err = self.expectError(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'expected_ou_as_rdn')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'ou=container,#'
        err = self.expectError(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'invalid_dn')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'ou=container,ou=inexistent,dc=my-domain,dc=com'
        err = self.expectError(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'parent_not_found')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'ou=container,dc=my-domain,dc=com'
        settings.create_container()
        self.assertTrue(settings.container_exists)

    @testing.invalidate_settings
    def test_LDAPUsersSettings(self):
        settings = get_root()['settings']['ldap_users']

        self.assertTrue(isinstance(settings, LDAPUsersSettings))

        md = settings.metadata
        self.assertEqual(md.title, 'user_settings_node')
        self.assertEqual(md.description, 'user_settings_node_description')

        attrs = settings.attrs
        self.assertEqual(sorted(attrs.keys()), [
            'users_aliases_attrmap',
            'users_dn',
            'users_expires_attr',
            'users_expires_unit',
            'users_object_classes',
            'users_query',
            'users_scope'
        ])

        attrs.users_dn = 'ou=users,dc=my-domain,dc=com'
        attrs.users_scope = '1'
        attrs.users_query = ''
        attrs.users_object_classes = [
            'top',
            'person',
            'organizationalPerson',
            'inetOrgPerson'
        ]
        attrs.users_aliases_attrmap = {
            'rdn': 'uid',
            'id': 'uid',
            'password': 'userPassword'
        }

        ugm_settings = settings.parent['ugm_general']
        ugm_attrs = ugm_settings.attrs
        ugm_attrs.users_login_name_attr = 'uid'
        ugm_attrs.users_form_attrmap = {
            'cn': 'Fullname',
            'sn': 'Surname',
            'mail': 'Email'
        }
        ugm_attrs.users_exposed_attributes = ['homePhone']
        ugm_attrs.users_account_expiration = 'True'
        ugm_attrs.users_expires_attr = 'shadowExpire'
        ugm_attrs.users_expires_unit = '0'
        ugm_attrs.users_portrait = 'True'
        ugm_attrs.users_portrait_attr = 'jpegPhoto'

        ldap_ucfg = settings.ldap_ucfg
        self.assertEqual(isinstance(ldap_ucfg, UsersConfig), True)
        self.assertEqual(
            ldap_ucfg.baseDN,
            'ou=users,dc=my-domain,dc=com'
        )
        self.assertEqual(sorted(ldap_ucfg.attrmap.items()), [
            ('cn', 'cn'),
            ('homePhone', 'homePhone'),
            ('id', 'uid'),
            ('jpegPhoto', 'jpegPhoto'),
            ('login', 'uid'),
            ('mail', 'mail'),
            ('password', 'userPassword'),
            ('rdn', 'uid'),
            ('shadowExpire', 'shadowExpire'),
            ('sn', 'sn'),
            ('uid', 'uid')
        ])
        self.assertEqual(ldap_ucfg.scope, 1)
        self.assertEqual(ldap_ucfg.queryFilter, '')
        self.assertEqual(sorted(ldap_ucfg.objectClasses), [
            'inetOrgPerson',
            'organizationalPerson',
            'person',
            'top'
        ])
        self.assertEqual(ldap_ucfg.defaults, {})
        self.assertEqual(ldap_ucfg.expiresAttr, 'shadowExpire')
        self.assertEqual(ldap_ucfg.expiresUnit, 0)

        self.assertTrue(settings.attrs is attrs)
        self.assertTrue(settings.ldap_ucfg is ldap_ucfg)
        settings.invalidate()
        self.assertFalse(settings.attrs is attrs)
        self.assertFalse(settings.ldap_ucfg is ldap_ucfg)

        ldap_settings = settings.parent['ldap_server']
        ldap_settings.invalidate()
        settings.invalidate()
        settings.attrs.users_dn = 'ou=users-container,dc=my-domain,dc=com'
        self.assertFalse(settings.container_exists)
        settings.create_container()
        self.assertTrue(settings.container_exists)

        ldap_settings.invalidate()
        settings.invalidate()
        ldap_settings.attrs.cache = None
        self.assertFalse(settings.container_exists)

    @testing.invalidate_settings
    def test_LDAPGroupsSettings(self):
        settings = get_root()['settings']['ldap_groups']

        self.assertTrue(isinstance(settings, LDAPGroupsSettings))

        md = settings.metadata
        self.assertEqual(md.title, 'group_settings_node')
        self.assertEqual(md.description, 'group_settings_node_description')

        attrs = settings.attrs
        self.assertEqual(sorted(attrs.keys()), [
            'groups_aliases_attrmap',
            'groups_dn',
            'groups_object_classes',
            'groups_query',
            'groups_relation',
            'groups_scope'
        ])

        attrs.groups_dn = 'ou=groups,dc=my-domain,dc=com'
        attrs.groups_scope = '1'
        attrs.groups_query = ''
        attrs.groups_object_classes = ['groupOfNames']
        attrs.groups_aliases_attrmap = {
            'rdn': 'cn',
            'id': 'cn'
        }
        attrs.groups_relation = ''

        ugm_settings = settings.parent['ugm_general']
        ugm_attrs = ugm_settings.attrs
        ugm_attrs.groups_form_attrmap = {
            'description': 'Description'
        }

        ldap_gcfg = settings.ldap_gcfg
        self.assertEqual(isinstance(ldap_gcfg, GroupsConfig), True)

        self.assertEqual(
            ldap_gcfg.baseDN,
            'ou=groups,dc=my-domain,dc=com'
        )
        self.assertEqual(sorted(ldap_gcfg.attrmap.items()), [
            ('description', 'description'),
            ('id', 'cn'),
            ('rdn', 'cn')
        ])
        self.assertEqual(ldap_gcfg.scope, 1)
        self.assertEqual(ldap_gcfg.queryFilter, '')
        self.assertEqual(ldap_gcfg.objectClasses, ['groupOfNames'])
        self.assertEqual(ldap_gcfg.defaults, {})

        self.assertTrue(settings.attrs is attrs)
        self.assertTrue(settings.ldap_gcfg is ldap_gcfg)
        settings.invalidate()
        self.assertFalse(settings.attrs is attrs)
        self.assertFalse(settings.ldap_gcfg is ldap_gcfg)

        ldap_settings = settings.parent['ldap_server']
        ldap_settings.invalidate()
        settings.invalidate()
        settings.attrs.groups_dn = 'ou=groups-container,dc=my-domain,dc=com'
        self.assertFalse(settings.container_exists)
        settings.create_container()
        self.assertTrue(settings.container_exists)

        ldap_settings.invalidate()
        settings.invalidate()
        ldap_settings.attrs.cache = None
        self.assertFalse(settings.container_exists)

    @testing.invalidate_settings
    def test_LDAPRolesSettings(self):
        settings = get_root()['settings']['ldap_roles']

        self.assertTrue(isinstance(settings, LDAPRolesSettings))

        md = settings.metadata
        self.assertEqual(md.title, 'role_settings_node')
        self.assertEqual(md.description, 'role_settings_node_description')

        attrs = settings.attrs
        self.assertEqual(sorted(attrs.keys()), [
            'roles_aliases_attrmap',
            'roles_dn',
            'roles_object_classes',
            'roles_query',
            'roles_relation',
            'roles_scope'
        ])

        attrs.roles_dn = 'ou=roles,dc=my-domain,dc=com'
        attrs.roles_scope = '1'
        attrs.roles_query = ''
        attrs.roles_object_classes = ['groupOfUniqueNames']
        attrs.roles_aliases_attrmap = {
            'rdn': 'cn',
            'id': 'cn'
        }
        attrs.roles_relation = ''

        ldap_rcfg = settings.ldap_rcfg
        self.assertEqual(isinstance(ldap_rcfg, RolesConfig), True)

        self.assertEqual(
            ldap_rcfg.baseDN,
            'ou=roles,dc=my-domain,dc=com'
        )
        self.assertEqual(sorted(ldap_rcfg.attrmap.items()), [
            ('id', 'cn'),
            ('rdn', 'cn')
        ])
        self.assertEqual(ldap_rcfg.scope, 1)
        self.assertEqual(ldap_rcfg.queryFilter, '')
        self.assertEqual(ldap_rcfg.objectClasses, ['groupOfUniqueNames'])
        self.assertEqual(ldap_rcfg.defaults, {})

        self.assertTrue(settings.attrs is attrs)
        self.assertTrue(settings.ldap_rcfg is ldap_rcfg)
        settings.invalidate()
        self.assertFalse(settings.attrs is attrs)
        self.assertFalse(settings.ldap_rcfg is ldap_rcfg)

        ldap_settings = settings.parent['ldap_server']
        ldap_settings.invalidate()
        settings.invalidate()
        settings.attrs.roles_dn = 'ou=roles-container,dc=my-domain,dc=com'
        self.assertFalse(settings.container_exists)
        settings.create_container()
        self.assertTrue(settings.container_exists)

        ldap_settings.invalidate()
        settings.invalidate()
        ldap_settings.attrs.cache = None
        self.assertFalse(settings.container_exists)

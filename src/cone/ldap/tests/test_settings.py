from cone.app import get_root
from cone.app.model import XMLProperties
from cone.ldap import testing
from cone.ldap.settings import LDAPContainerError
from cone.ldap.settings import LDAPContainerSettings
from cone.ldap.settings import LDAPGroupsSettings
from cone.ldap.settings import LDAPRolesSettings
from cone.ldap.settings import LDAPServerSettings
from cone.ldap.settings import LDAPUsersSettings
from cone.ldap.settings import UGMGeneralSettings
from cone.ldap.settings import XMLSettings
from node.ext.ldap import LDAPProps
from node.ext.ldap.ugm import GroupsConfig
from node.ext.ldap.ugm import RolesConfig
from node.ext.ldap.ugm import UsersConfig
from node.tests import NodeTestCase
import os
import shutil
import tempfile


class TestSettings(NodeTestCase):
    layer = testing.ldap_layer

    def test_XMLSettings(self):
        tempdir = tempfile.mkdtemp()
        path = os.path.join(tempdir, 'settings.xml')

        class MyXMLSettings(XMLSettings):
            config_file = path

        settings = MyXMLSettings()
        expected = 'LDAP configuration {} does not exist.'.format(path)
        err = self.expect_error(ValueError, lambda: settings.attrs)
        self.assertEqual(str(err), expected)

        with open(path, 'w') as f:
            f.write('<properties />')

        attrs = settings.attrs
        self.assertTrue(isinstance(attrs, XMLProperties))

        attrs.foo = 'foo'
        settings()

        with open(path, 'r') as f:
            content = f.read()
        expected = '<properties>\n  <foo>foo</foo>\n</properties>\n'
        self.assertEqual(content, expected)

        self.assertTrue(attrs is settings.attrs)
        settings.invalidate()
        self.assertFalse(attrs is settings.attrs)

        shutil.rmtree(tempdir)

    #######################
    # XXX: move to cone.ugm

    @testing.invalidate_settings
    def test_UGMGeneralSettings(self):
        settings = get_root()['settings']['ugm']

        self.assertTrue(isinstance(settings, UGMGeneralSettings))

        md = settings.metadata
        self.assertEqual(md.title, 'ugm_settings_node')
        self.assertEqual(md.description, 'ugm_settings_node_description')

        attrs = settings.attrs
        self.assertEqual(sorted(attrs.keys()), [
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

        self.assertTrue(attrs is settings.attrs)
        settings.invalidate()
        self.assertFalse(attrs is settings.attrs)

    # XXX: end move to cone.ugm
    ###########################

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
        err = self.expect_error(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'no_container_dn_defined')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'uid=foo,dc=my-domain,dc=com'
        err = self.expect_error(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'expected_ou_as_rdn')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'ou=container,#'
        err = self.expect_error(LDAPContainerError, settings.create_container)
        self.assertEqual(err.error_message, 'invalid_dn')
        self.assertFalse(settings.container_exists)

        settings.container_dn = 'ou=container,ou=inexistent,dc=my-domain,dc=com'
        err = self.expect_error(LDAPContainerError, settings.create_container)
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
            'login': 'uid',
        }

        ugm_settings = settings.parent['ugm']
        ugm_attrs = ugm_settings.attrs
        ugm_attrs.users_form_attrmap = {
            'id': 'id',
            'userPassword': 'Password',
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
        self.assertEqual(ldap_ucfg.attrmap, {
            'cn': 'cn',
            'userPassword': 'userPassword',
            'jpegPhoto': 'jpegPhoto',
            'shadowExpire': 'shadowExpire',
            'sn': 'sn',
            'mail': 'mail',
            'login': 'uid',
            'rdn': 'uid',
            'id': 'uid',
            'homePhone': 'homePhone'
        })
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

        ugm_settings = settings.parent['ugm']
        ugm_attrs = ugm_settings.attrs
        ugm_attrs.groups_form_attrmap = {
            'id': 'Id',
            'description': 'Description'
        }

        ldap_gcfg = settings.ldap_gcfg
        self.assertEqual(isinstance(ldap_gcfg, GroupsConfig), True)

        self.assertEqual(
            ldap_gcfg.baseDN,
            'ou=groups,dc=my-domain,dc=com'
        )
        self.assertEqual(ldap_gcfg.attrmap, {
            'rdn': 'cn',
            'id': 'cn',
            'description': 'description'
        })
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
        self.assertEqual(ldap_rcfg.attrmap, {
            'rdn': 'cn',
            'id': 'cn'
        })
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
        self.assertFalse(settings.container_exists)
        settings.create_container()
        self.assertTrue(settings.container_exists)

        ldap_settings.invalidate()
        settings.invalidate()
        ldap_settings.attrs.cache = None
        self.assertFalse(settings.container_exists)

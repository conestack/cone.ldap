from cone.ldap import testing
from cone.tile.tests import TileTestCase
from cone.ugm.tests import test_browser_actions
from cone.ugm.tests import test_browser_autoincrement
from cone.ugm.tests import test_browser_expires
from cone.ugm.tests import test_browser_group
from cone.ugm.tests import test_browser_groups
# from cone.ugm.tests import test_browser_password
from cone.ugm.tests import test_browser_portrait
from cone.ugm.tests import test_browser_principal
from cone.ugm.tests import test_browser_remote
from cone.ugm.tests import test_browser_roles
from cone.ugm.tests import test_browser_root
from cone.ugm.tests import test_browser_settings
from cone.ugm.tests import test_browser_user
from cone.ugm.tests import test_browser_users
from cone.ugm.tests import test_browser_utils
from cone.ugm.tests import test_layout
from cone.ugm.tests import test_localmanager
from cone.ugm.tests import test_model_group
from cone.ugm.tests import test_model_groups
from cone.ugm.tests import test_model_user
from cone.ugm.tests import test_model_users
from cone.ugm.tests import test_settings
from cone.ugm.tests import test_utils
from node.tests import NodeTestCase
import unittest


class TestLayout(
    unittest.TestCase,
    test_layout.LayoutTests
):
    pass


class TestModelLocalmanager(
    NodeTestCase,
    test_localmanager.ModelLocalmanagerTests
):
    layer = testing.ldap_layer


class TestSettings(
    NodeTestCase,
    test_settings.SettingsTests
):
    layer = testing.ldap_layer


class TestUtils(
    unittest.TestCase,
    test_utils.UtilsTests
):
    layer = testing.ldap_layer


class TestModelGroup(
    unittest.TestCase,
    test_model_group.ModelGroupTests
):
    layer = testing.ldap_layer


class TestModelGroups(
    NodeTestCase,
    test_model_groups.ModelGroupsTests
):
    layer = testing.ldap_layer


class TestModelUser(
    unittest.TestCase,
    test_model_user.ModelUserTests
):
    layer = testing.ldap_layer


class TestModelUsers(
    NodeTestCase,
    test_model_users.ModelUsersTests
):
    layer = testing.ldap_layer


class TestBrowserActions(
    TileTestCase,
    test_browser_actions.BrowserActionsTests
):
    layer = testing.ldap_layer


class TestBrowserAutoincrement(
    TileTestCase,
    test_browser_autoincrement.BrowserAutoincrementTests
):
    layer = testing.ldap_layer


class TestBrowserExpires(
    TileTestCase,
    test_browser_expires.BrowserExpiresTests
):
    layer = testing.ldap_layer


class TestBrowserGroup(
    TileTestCase,
    test_browser_group.BrowserGroupTests
):
    layer = testing.ldap_layer


class TestBrowserGroups(
    TileTestCase,
    test_browser_groups.BrowserGroupsTests
):
    layer = testing.ldap_layer


# class TestBrowserPassword(
#     TileTestCase,
#     test_browser_password.BrowserPasswordTests
# ):
#     layer = testing.ldap_layer


class TestBrowserPortrait(
    TileTestCase,
    test_browser_portrait.BrowserPortraitTests
):
    layer = testing.ldap_layer


class TestBrowserPrincipal(
    TileTestCase,
    test_browser_principal.BrowserPrincipalTests
):
    layer = testing.ldap_layer


class TestBrowserRemote(
    TileTestCase,
    test_browser_remote.BrowserRemoteTests
):
    layer = testing.ldap_layer


class TestBrowserRoles(
    TileTestCase,
    test_browser_roles.BrowserRolesTests
):
    layer = testing.ldap_layer


class TestBrowserRoot(
    TileTestCase,
    test_browser_root.BrowserRootTests
):
    layer = testing.ldap_layer


class TestBrowserSettings(
    TileTestCase,
    test_browser_settings.BrowserSettingsTests
):
    layer = testing.ldap_layer


class TestBrowserUser(
    TileTestCase,
    test_browser_user.BrowserUserTests
):
    layer = testing.ldap_layer


class TestBrowserUsers(
    TileTestCase,
    test_browser_users.BrowserUsersTests
):
    layer = testing.ldap_layer


class TestBrowserUtils(
    TileTestCase,
    test_browser_utils.BrowserUtilsTests
):
    layer = testing.ldap_layer

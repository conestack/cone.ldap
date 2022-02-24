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
    test_layout.TestLayoutBase
):
    pass


class TestModelLocalmanager(
    NodeTestCase,
    test_localmanager.TestModelLocalmanagerBase
):
    layer = testing.ldap_layer


class TestSettings(
    NodeTestCase,
    test_settings.TestSettingsBase
):
    layer = testing.ldap_layer


class TestUtils(
    unittest.TestCase,
    test_utils.TestUtilsBase
):
    layer = testing.ldap_layer


class TestModelGroup(
    unittest.TestCase,
    test_model_group.TestModelGroupBase
):
    layer = testing.ldap_layer


class TestModelGroups(
    NodeTestCase,
    test_model_groups.TestModelGroupsBase
):
    layer = testing.ldap_layer


class TestModelUser(
    unittest.TestCase,
    test_model_user.TestModelUserBase
):
    layer = testing.ldap_layer


class TestModelUsers(
    NodeTestCase,
    test_model_users.TestModelUsersBase
):
    layer = testing.ldap_layer


class TestBrowserActions(
    TileTestCase,
    test_browser_actions.TestBrowserActionsBase
):
    layer = testing.ldap_layer


class TestBrowserAutoincrement(
    TileTestCase,
    test_browser_autoincrement.TestBrowserAutoincrementBase
):
    layer = testing.ldap_layer


class TestBrowserExpires(
    TileTestCase,
    test_browser_expires.TestBrowserExpiresBase
):
    layer = testing.ldap_layer


class TestBrowserGroup(
    TileTestCase,
    test_browser_group.TestBrowserGroupBase
):
    layer = testing.ldap_layer


class TestBrowserGroups(
    TileTestCase,
    test_browser_groups.TestBrowserGroupsBase
):
    layer = testing.ldap_layer


# class TestBrowserPassword(
#     TileTestCase,
#     test_browser_password.TestBrowserPasswordBase
# ):
#     layer = testing.ldap_layer


class TestBrowserPortrait(
    TileTestCase,
    test_browser_portrait.TestBrowserPortraitBase
):
    layer = testing.ldap_layer


class TestBrowserPrincipal(
    TileTestCase,
    test_browser_principal.TestBrowserPrincipalBase
):
    layer = testing.ldap_layer


class TestBrowserRemote(
    TileTestCase,
    test_browser_remote.TestBrowserRemoteBase
):
    layer = testing.ldap_layer


class TestBrowserRoles(
    TileTestCase,
    test_browser_roles.TestBrowserRolesBase
):
    layer = testing.ldap_layer


class TestBrowserRoot(
    TileTestCase,
    test_browser_root.TestBrowserRootBase
):
    layer = testing.ldap_layer


class TestBrowserSettings(
    TileTestCase,
    test_browser_settings.TestBrowserSettingsBase
):
    layer = testing.ldap_layer


class TestBrowserUser(
    TileTestCase,
    test_browser_user.TestBrowserUserBase
):
    layer = testing.ldap_layer


class TestBrowserUsers(
    TileTestCase,
    test_browser_users.TestBrowserUsersBase
):
    layer = testing.ldap_layer


class TestBrowserUtils(
    TileTestCase,
    test_browser_utils.TestBrowserUtilsBase
):
    layer = testing.ldap_layer

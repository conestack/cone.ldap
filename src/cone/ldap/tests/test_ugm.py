from cone.ldap import testing
from cone.ugm.tests import test_browser_actions
from cone.ugm.tests import test_browser_autoincrement
from cone.ugm.tests import test_browser_expires
from cone.ugm.tests import test_browser_group
from cone.ugm.tests import test_browser_groups
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


class TestLayout(test_layout.TestLayout):
    pass


class TestModelLocalmanager(test_localmanager.TestModelLocalmanager):
    layer = testing.ldap_layer


class TestModelSettings(test_settings.TestModelSettings):
    layer = testing.ldap_layer


class TestModelUtils(test_utils.TestModelUtils):
    layer = testing.ldap_layer


class TestModelGroup(test_model_group.TestModelGroup):
    layer = testing.ldap_layer


class TestModelGroups(test_model_groups.TestModelGroups):
    layer = testing.ldap_layer


class TestModelUser(test_model_user.TestModelUser):
    layer = testing.ldap_layer


class TestModelUsers(test_model_users.TestModelUsers):
    layer = testing.ldap_layer


class TestBrowserActions(test_browser_actions.TestBrowserActions):
    layer = testing.ldap_layer


class TestBrowserAutoincrement(test_browser_autoincrement.TestBrowserAutoincrement):
    layer = testing.ldap_layer


class TestBrowserExpires(test_browser_expires.TestBrowserExpires):
    layer = testing.ldap_layer


class TestBrowserGroup(test_browser_group.TestBrowserGroup):
    layer = testing.ldap_layer


class TestBrowserGroups(test_browser_groups.TestBrowserGroups):
    layer = testing.ldap_layer


class TestBrowserPortrait(test_browser_portrait.TestBrowserPortrait):
    layer = testing.ldap_layer


class TestBrowserPrincipal(test_browser_principal.TestBrowserPrincipal):
    layer = testing.ldap_layer


class TestBrowserRemote(test_browser_remote.TestBrowserRemote):
    layer = testing.ldap_layer


class TestBrowserRoles(test_browser_roles.TestBrowserRoles):
    layer = testing.ldap_layer


class TestBrowserRoot(test_browser_root.TestBrowserRoot):
    layer = testing.ldap_layer


class TestBrowserSettings(test_browser_settings.TestBrowserSettings):
    layer = testing.ldap_layer


class TestBrowserUser(test_browser_user.TestBrowserUser):
    layer = testing.ldap_layer


class TestBroeserUsers(test_browser_users.TestBrowserUsers):
    layer = testing.ldap_layer


class TestBrowserUtils(test_browser_utils.TestBrowserUtils):
    layer = testing.ldap_layer

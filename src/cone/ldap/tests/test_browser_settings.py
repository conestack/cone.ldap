from cone.ldap import testing
from node.tests import NodeTestCase


class TestBrowserSettings(NodeTestCase):
    layer = testing.ldap_layer

    def test_foo(self):
        pass

from cone.app import get_root
from cone.app.browser.ajax import AjaxAction
from cone.app.browser.ajax import AjaxMessage
from cone.app.browser.utils import make_url
from cone.ldap import testing
from cone.ldap.browser.settings import CreateContainerAction
from cone.ldap.browser.settings import CreateContainerTrigger
from cone.ldap.browser.settings import ScopeVocabMixin
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm.testing import principals
from pyramid.httpexceptions import HTTPForbidden


class TestBrowserSettings(TileTestCase):
    layer = testing.ldap_layer

    def test_ScopeVocabMixin(self):
        vocab_mixin = ScopeVocabMixin()
        self.assertEqual(vocab_mixin.scope_vocab, [
            ('0', 'BASE'),
            ('1', 'ONELEVEL'),
            ('2', 'SUBTREE')
        ])

    @testing.invalidate_settings
    def test_CreateContainerTrigger(self):
        settings = get_root()['settings']['ldap_users']

        cct = CreateContainerTrigger()
        cct.model = settings
        cct.request = self.layer.new_request()

        self.assertTrue(cct.ldap_connectivity)
        self.assertEqual(
            cct.creation_target,
            'http://example.com/settings/ldap_users'
        )

    @testing.invalidate_settings
    def test_CreateContainerAction(self):
        settings = get_root()['settings']['ldap_users']

        cca = CreateContainerAction()
        cca.model = settings
        cca.request = self.layer.new_request()
        err = self.expectError(
            NotImplementedError,
            lambda: cca.continuation
        )
        expected = (
            'Abstract ``CreateContainerAction`` '
            'does not implement ``continuation``'
        )
        self.assertEqual(str(err), expected)

        class MyCreateContainerAction(CreateContainerAction):
            @property
            def continuation(self):
                url = make_url(self.request, node=self.model)
                return AjaxAction(url, 'content', 'inner', '.ldap_cca')

        cca = MyCreateContainerAction()

        request = self.layer.new_request()
        settings.attrs.users_dn = 'ou=cca,dc=other-domain,dc=com'
        self.assertEqual(cca(settings, request), '')
        self.assertFalse(settings.container_exists)

        self.assertEqual(len(request.environ['cone.app.continuation']), 1)
        message = request.environ['cone.app.continuation'][0]
        self.assertTrue(isinstance(message, AjaxMessage))
        self.assertEqual(message.flavor, 'error')
        self.assertEqual(
            message.payload,
            "Cannot create container: Parent not found. Can't continue."
        )

        request = self.layer.new_request()
        settings.attrs.users_dn = 'ou=cca,dc=my-domain,dc=com'
        self.assertEqual(cca(settings, request), '')
        # need to set users_dn again here because settings get invalidated
        # after container creation
        settings.attrs.users_dn = 'ou=cca,dc=my-domain,dc=com'
        self.assertTrue(settings.container_exists)

        self.assertEqual(len(request.environ['cone.app.continuation']), 2)
        message = request.environ['cone.app.continuation'][0]
        self.assertTrue(isinstance(message, AjaxMessage))
        self.assertEqual(message.flavor, 'info')
        self.assertEqual(message.payload, 'created_principal_container')
        action = request.environ['cone.app.continuation'][1]
        self.assertTrue(isinstance(action, AjaxAction))
        self.assertEqual(action.selector, '.ldap_cca')

    @principals(
        users={
            'editor': {},
            'manager': {}
        },
        roles={
            'editor': ['editor'],
            'manager': ['manager']
        })
    def test_server_settings_tiles(self):
        root = get_root()
        server_settings = root['settings']['ldap_server']
        request = self.layer.new_request()
        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            server_settings,
            request,
            'content'
        )
        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                server_settings,
                request,
                'editform'
            )
        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(server_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ldap_server/edit"'
        self.assertTrue(res.find(expected) > -1)

    @principals(
        users={
            'editor': {},
            'manager': {}
        },
        roles={
            'editor': ['editor'],
            'manager': ['manager']
        })
    def test_users_settings_tiles(self):
        root = get_root()
        users_settings = root['settings']['ldap_users']
        request = self.layer.new_request()
        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            users_settings,
            request,
            'content'
        )
        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                users_settings,
                request,
                'editform'
            )
        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(users_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ldap_users/edit"'
        self.assertTrue(res.find(expected) > -1)

    @principals(
        users={
            'editor': {},
            'manager': {}
        },
        roles={
            'editor': ['editor'],
            'manager': ['manager']
        })
    def test_groups_settings_tiles(self):
        root = get_root()
        groups_settings = root['settings']['ldap_groups']
        request = self.layer.new_request()
        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            groups_settings,
            request,
            'content'
        )
        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                groups_settings,
                request,
                'editform'
            )
        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(groups_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ldap_groups/edit"'
        self.assertTrue(res.find(expected) > -1)

    @principals(
        users={
            'editor': {},
            'manager': {}
        },
        roles={
            'editor': ['editor'],
            'manager': ['manager']
        })
    def test_roles_settings_tiles(self):
        root = get_root()
        roles_settings = root['settings']['ldap_roles']
        request = self.layer.new_request()
        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden,
            render_tile,
            roles_settings,
            request,
            'content'
        )
        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden,
                render_tile,
                roles_settings,
                request,
                'editform'
            )
        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(roles_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ldap_roles/edit"'
        self.assertTrue(res.find(expected) > -1)

from cone.app import get_root
from cone.app.browser.ajax import AjaxEvent
from cone.app.browser.ajax import AjaxMessage
from cone.app.ugm import ugm_backend
from cone.ldap import testing
from cone.ldap.browser.settings import CreateContainerAction
from cone.ldap.browser.settings import CreateContainerTrigger
from cone.ldap.browser.settings import GroupsSettingsForm
from cone.ldap.browser.settings import RolesSettingsForm
from cone.ldap.browser.settings import ScopeVocabMixin
from cone.ldap.browser.settings import ServerSettingsForm
from cone.ldap.browser.settings import UsersSettingsForm
from cone.ldap.settings import ldap_cfg
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm.testing import principals
from cone.ugm.testing import temp_directory
from cone.ugm.utils import general_settings
from pyramid.httpexceptions import HTTPForbidden
from webob.exc import HTTPFound
import os
import shutil


def reinitialize_ugm_backend(fn):
    """Decorator for tests which change the UGM backend by saving settings.

    Must be applied outside ``custom_config_path``, so the backend gets
    initialized with the restored settings.
    """
    def wrapper(*a, **kw):
        try:
            fn(*a, **kw)
        finally:
            ugm_backend.initialize()
    return wrapper


def use_temp_ldap_configs(tempdir):
    """Copy LDAP config files to ``tempdir`` and point settings to copies."""
    for name in ['server', 'users', 'groups', 'roles']:
        config_attr = f'{name}_config'
        source = getattr(ldap_cfg, config_attr)
        target = os.path.join(tempdir, os.path.basename(source))
        shutil.copy(source, target)
        setattr(ldap_cfg, config_attr, target)


def dict_params(name, entries, static=False):
    """Create request parameters for a dict widget.

    :param name: Dotted path of the dict widget.
    :param entries: List of key/value tuples.
    :param static: Flag whether dict widget is static.
    :return: Dict of request parameters.
    """
    params = {f'{name}.exists': '1'}
    for index, (key, value) in enumerate(entries):
        if not static:
            params[f'{name}.entry{index}.key'] = key
        params[f'{name}.entry{index}.value'] = value
    return params


def users_form_params(additional_aliases, expires_attr='shadowExpire'):
    params = {
        'ldap_users_settings.users_dn': 'ou=users,dc=my-domain,dc=com',
        'ldap_users_settings.users_scope': '2',
        'ldap_users_settings.users_query': '(objectClass=person)',
        'ldap_users_settings.users_object_classes': 'top, person, ',
        'ldap_users_settings.users_expires_attr': expires_attr,
        'ldap_users_settings.users_expires_unit': '1',
        'action.ldap_users_settings.save': '1'
    }
    params.update(dict_params(
        'ldap_users_settings.users_reserved_aliases',
        [('rdn', 'uid'), ('id', 'uid'), ('password', 'userPassword')],
        static=True
    ))
    params.update(dict_params(
        'ldap_users_settings.users_additional_aliases',
        additional_aliases
    ))
    return params


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
        self.assertEqual(message.payload, 'Created ou=cca')
        event = request.environ['cone.app.continuation'][1]
        self.assertTrue(isinstance(event, AjaxEvent))
        self.assertEqual(event.target, 'http://example.com/settings/ldap_users')
        self.assertEqual(event.name, 'contextchanged')
        self.assertEqual(event.selector, '#layout')

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

    @testing.invalidate_settings
    def test_ldap_status_down_if_server_not_reachable(self):
        server_settings = get_root()['settings']['ldap_server']
        form = ServerSettingsForm()
        form.model = server_settings
        form.request = self.layer.new_request()
        server_settings.attrs.password = 'invalid'
        self.assertEqual(form.ldap_status, 'server_down')
        self.assertEqual(form.ldap_status.default, 'Down')

    @testing.invalidate_settings
    def test_container_status_inexistent_if_container_missing(self):
        settings = get_root()['settings']
        for form_class, settings_name, status_attr in [
            (UsersSettingsForm, 'ldap_users', 'ldap_users'),
            (GroupsSettingsForm, 'ldap_groups', 'ldap_groups'),
            (RolesSettingsForm, 'ldap_roles', 'ldap_roles'),
        ]:
            model = settings[settings_name]
            form = form_class()
            form.model = model
            form.request = self.layer.new_request()
            self.assertEqual(getattr(form, status_attr), 'OK')

            dn_attr = f'{settings_name[5:]}_dn'
            setattr(
                model.attrs,
                dn_attr,
                'ou=inexistent,dc=my-domain,dc=com'
            )
            status = getattr(form, status_attr)
            self.assertEqual(status, 'inexistent')
            self.assertEqual(status.default, 'Inexistent')

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @reinitialize_ugm_backend
    @testing.custom_config_path
    @temp_directory
    def test_save_server_settings(self, tempdir):
        use_temp_ldap_configs(tempdir)
        model = get_root()['settings']['ldap_server']
        request = self.layer.new_request()
        request.params.update({
            'ldap_server_settings.uri': 'ldap://127.0.0.1:12345',
            'ldap_server_settings.user': 'cn=Manager,dc=my-domain,dc=com',
            'ldap_server_settings.password': 'secret',
            'ldap_server_settings.cache': '1',
            'ldap_server_settings.cache-exists': '1',
            'action.ldap_server_settings.save': '1'
        })
        ugm = ugm_backend.ugm
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertFalse(ugm_backend.ugm is ugm)

        model.invalidate()
        self.assertEqual(model.attrs.uri, 'ldap://127.0.0.1:12345')
        self.assertEqual(model.attrs.user, 'cn=Manager,dc=my-domain,dc=com')
        self.assertEqual(model.attrs.password, 'secret')
        self.assertEqual(model.attrs.cache, '1')
        self.assertEqual(model.ldap_props.cache, 1)

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @reinitialize_ugm_backend
    @testing.custom_config_path
    @temp_directory
    def test_save_users_settings(self, tempdir):
        use_temp_ldap_configs(tempdir)
        model = get_root()['settings']['ldap_users']
        request = self.layer.new_request()
        request.params.update(users_form_params([('email', 'mail')]))
        ugm = ugm_backend.ugm
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertFalse(ugm_backend.ugm is ugm)

        model.invalidate()
        attrs = model.attrs
        self.assertEqual(attrs.users_dn, 'ou=users,dc=my-domain,dc=com')
        self.assertEqual(attrs.users_scope, '2')
        self.assertEqual(attrs.users_query, '(objectClass=person)')
        self.assertEqual(attrs.users_object_classes, ['top', 'person'])
        self.assertEqual(attrs.users_expires_attr, 'shadowExpire')
        self.assertEqual(attrs.users_expires_unit, '1')
        self.assertEqual(dict(attrs.users_aliases_attrmap), {
            'rdn': 'uid',
            'id': 'uid',
            'password': 'userPassword',
            'email': 'mail'
        })

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @testing.custom_config_path
    def test_users_settings_additional_alias_must_not_be_empty(self):
        model = get_root()['settings']['ldap_users']
        request = self.layer.new_request()
        request.params.update(users_form_params([('email', ' ')]))
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        self.assertTrue(res.find('Additional aliases must not be empty') > -1)
        self.assertFalse('redirect' in request.environ)

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @testing.custom_config_path
    def test_users_settings_expires_attr_required_if_expiration_enabled(self):
        model = get_root()['settings']['ldap_users']
        general_settings(model).attrs.users_account_expiration = 'True'
        request = self.layer.new_request()
        request.params.update(users_form_params(
            [('email', 'mail')],
            expires_attr=''
        ))
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        expected = 'Value is required if account expiration is enabled'
        self.assertTrue(res.find(expected) > -1)
        self.assertFalse('redirect' in request.environ)

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @reinitialize_ugm_backend
    @testing.custom_config_path
    @temp_directory
    def test_save_users_settings_without_expires_attr_if_expiration_disabled(
        self,
        tempdir
    ):
        use_temp_ldap_configs(tempdir)
        model = get_root()['settings']['ldap_users']
        general_settings(model).attrs.users_account_expiration = 'False'
        request = self.layer.new_request()
        request.params.update(users_form_params(
            [('email', 'mail')],
            expires_attr=''
        ))
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))

        model.invalidate()
        self.assertEqual(model.attrs.users_expires_attr, '')

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @reinitialize_ugm_backend
    @testing.custom_config_path
    @temp_directory
    def test_save_groups_settings(self, tempdir):
        use_temp_ldap_configs(tempdir)
        model = get_root()['settings']['ldap_groups']
        request = self.layer.new_request()
        request.params.update({
            'ldap_groups_settings.groups_dn': 'ou=groups,dc=my-domain,dc=com',
            'ldap_groups_settings.groups_scope': '2',
            'ldap_groups_settings.groups_query': '(cn=*)',
            'ldap_groups_settings.groups_object_classes': 'groupOfNames',
            'action.ldap_groups_settings.save': '1'
        })
        request.params.update(dict_params(
            'ldap_groups_settings.groups_reserved_aliases',
            [('rdn', 'cn'), ('id', 'cn')],
            static=True
        ))
        request.params.update(dict_params(
            'ldap_groups_settings.groups_additional_aliases',
            [('groupname', 'description')]
        ))
        ugm = ugm_backend.ugm
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertFalse(ugm_backend.ugm is ugm)

        model.invalidate()
        attrs = model.attrs
        self.assertEqual(attrs.groups_dn, 'ou=groups,dc=my-domain,dc=com')
        self.assertEqual(attrs.groups_scope, '2')
        self.assertEqual(attrs.groups_query, '(cn=*)')
        self.assertEqual(attrs.groups_object_classes, ['groupOfNames'])
        self.assertEqual(dict(attrs.groups_aliases_attrmap), {
            'rdn': 'cn',
            'id': 'cn',
            'groupname': 'description'
        })

    @principals(
        users={'manager': {}},
        roles={'manager': ['manager']})
    @reinitialize_ugm_backend
    @testing.custom_config_path
    @temp_directory
    def test_save_roles_settings(self, tempdir):
        use_temp_ldap_configs(tempdir)
        model = get_root()['settings']['ldap_roles']
        request = self.layer.new_request()
        request.params.update({
            'ldap_roles_settings.roles_dn': 'ou=roles,dc=my-domain,dc=com',
            'ldap_roles_settings.roles_scope': '2',
            'ldap_roles_settings.roles_query': '(cn=*)',
            'ldap_roles_settings.roles_object_classes': 'groupOfUniqueNames',
            'action.ldap_roles_settings.save': '1'
        })
        request.params.update(dict_params(
            'ldap_roles_settings.roles_aliases_attrmap',
            [('rdn', 'cn'), ('id', 'cn')],
            static=True
        ))
        ugm = ugm_backend.ugm
        with self.layer.authenticated('manager'):
            res = render_tile(model, request, 'editform')
        self.assertEqual(res, '')
        self.assertTrue(isinstance(request.environ['redirect'], HTTPFound))
        self.assertFalse(ugm_backend.ugm is ugm)

        model.invalidate()
        attrs = model.attrs
        self.assertEqual(attrs.roles_dn, 'ou=roles,dc=my-domain,dc=com')
        self.assertEqual(attrs.roles_scope, '2')
        self.assertEqual(attrs.roles_query, '(cn=*)')
        self.assertEqual(attrs.roles_object_classes, ['groupOfUniqueNames'])
        self.assertEqual(dict(attrs.roles_aliases_attrmap), {
            'rdn': 'cn',
            'id': 'cn'
        })

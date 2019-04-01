from cone.app import get_root
from cone.app.browser.ajax import AjaxAction
from cone.app.browser.ajax import AjaxMessage
from cone.app.browser.utils import make_url
from cone.ldap import testing
from cone.ldap.browser.settings import CreateContainerAction
from cone.ldap.browser.settings import CreateContainerTrigger
from cone.ldap.browser.settings import GeneralSettingsForm
from cone.ldap.browser.settings import ScopeVocabMixin
from cone.ldap.settings import ldap_cfg
from cone.ldap.settings import ugm_cfg
from cone.tile.tests import TileTestCase
import os


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

        self.assertFalse(settings.container_exists)

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

    #######################
    # XXX: move to cone.ugm

    @testing.custom_config_path
    @testing.temp_directory
    def test_GeneralSettingsForm(self, tempdir):
        config_file = os.path.join(tempdir, 'ugm.xml')
        ugm_cfg.ugm_settings = config_file
        with open(config_file, 'w') as f:
            f.write('<properties></properties>')

        model = get_root()['settings']['ugm']
        request = self.layer.new_request()

        tile = GeneralSettingsForm()
        tile.model = model
        tile.request = request
        tile.prepare()

        form = tile.form
        self.assertEqual(form.keys(), [
            'users_heading',
            'users_account_expiration',
            'users_expires_attr',
            'users_expires_unit',
            'user_id_autoincrement',
            'user_id_autoincrement_prefix',
            'user_id_autoincrement_start',
            'users_portrait',
            'users_portrait_attr',
            'users_portrait_accept',
            'users_portrait_width',
            'users_portrait_height',
            'users_local_management_enabled',
            'users_exposed_attributes',
            'users_form_attrmap',
            'users_listing_columns',
            'users_listing_default_column',
            'groups_heading',
            'groups_form_attrmap',
            'groups_listing_columns',
            'groups_listing_default_column',
            'save'
        ])

    # XXX: end move to cone.ugm
    ###########################

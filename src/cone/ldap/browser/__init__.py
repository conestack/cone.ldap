from cone.app.browser.resources import resources
from cone.app.browser.resources import set_resource_include
from cone.ugm.browser.principal import default_form_field_factory
from cone.ugm.browser.principal import user_field
from functools import partial
import os
import webresource as wr


ldap_cn_field_factory = user_field('cn', backend='ldap')(
    partial(default_form_field_factory, required=True)
)
ldap_sn_field_factory = user_field('sn', backend='ldap')(
    partial(default_form_field_factory, required=True)
)

resources_dir = os.path.join(os.path.dirname(__file__), 'static')
cone_ldap_resources = wr.ResourceGroup(
    name='cone.ldap-ldap',
    directory=resources_dir,
    path='ldap',
    group=resources
)
cone_ldap_resources.add(wr.StyleResource(
    name='cone-ldap-css',
    resource='cone.ldap.css'
))


def configure_resources(settings):
    include = 'authenticated' if settings.get('ugm.backend') == 'ldap' else False
    set_resource_include(settings, 'cone-ldap-css', include)

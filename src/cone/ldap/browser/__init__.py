from cone.ugm.browser.principal import default_form_field_factory
from cone.ugm.browser.principal import user_field
from functools import partial
from pyramid.static import static_view


static_resources = static_view('static', use_subpath=True)


ldap_cn_field_factory = user_field('cn', backend='ldap')(
    partial(default_form_field_factory, required=True)
)
ldap_sn_field_factory = user_field('sn', backend='ldap')(
    partial(default_form_field_factory, required=True)
)

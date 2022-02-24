from cone.app import get_root
from cone.app.ugm import ugm_backend
from cone.ldap.settings import ldap_cfg
from cone.ugm import testing
from cone.ugm.settings import ugm_cfg
from cone.ugm.testing import UGMLayer
from node.ext.ldap.testing import LDIF_base
from node.ext.ldap.ugm.defaults import creation_defaults
from plone.testing import Layer
import os


base_path = os.path.split(__file__)[0]
ldap_server_config = os.path.join(base_path, 'ldap_server.xml')
ldap_users_config = os.path.join(base_path, 'ldap_users.xml')
ldap_groups_config = os.path.join(base_path, 'ldap_groups.xml')
ldap_roles_config = os.path.join(base_path, 'ldap_roles.xml')


def _invalidate_settings():
    settings = get_root()['settings']
    settings['ugm_general'].invalidate()
    settings['ldap_server'].invalidate()
    settings['ldap_users'].invalidate()
    settings['ldap_groups'].invalidate()
    settings['ldap_roles'].invalidate()


def invalidate_settings(fn):
    """Decorator for tests working on settings nodes.
    """
    def wrapper(*a, **kw):
        _invalidate_settings()
        try:
            fn(*a, **kw)
        finally:
            _invalidate_settings()
    return wrapper


def custom_config_path(fn):
    """Decorator for tests writing to config files.
    """
    def wrapper(*a, **kw):
        ugm_settings = ugm_cfg.ugm_settings
        server_config = ldap_cfg.server_config
        users_config = ldap_cfg.users_config
        groups_config = ldap_cfg.groups_config
        roles_config = ldap_cfg.roles_config
        _invalidate_settings()
        try:
            fn(*a, **kw)
        finally:
            ugm_cfg.ugm_settings = ugm_settings
            ldap_cfg.server_config = server_config
            ldap_cfg.users_config = users_config
            ldap_cfg.groups_config = groups_config
            ldap_cfg.roles_config = roles_config
            _invalidate_settings()
    return wrapper


def rdn_value(node, uid):
    return uid.split('=')[1]


def create_mail(node, uid):
    return '%s@example.com' % rdn_value(node, uid)


creation_defaults['inetOrgPerson'] = dict()
creation_defaults['inetOrgPerson']['sn'] = rdn_value
creation_defaults['inetOrgPerson']['cn'] = rdn_value
creation_defaults['inetOrgPerson']['mail'] = create_mail


class LDAPLayer(UGMLayer, Layer):
    defaultBases = (LDIF_base,)

    def __init__(self):
        Layer.__init__(self)

    def make_app(self):
        super(UGMLayer, self).make_app(**{
            'cone.plugins': '\n'.join([
                'cone.ugm',
                'cone.ldap'
            ]),
            'ugm.backend': 'ldap',
            'ugm.config': testing.ugm_config,
            'ugm.localmanager_config': testing.localmanager_config,
            'ldap.server_config': ldap_server_config,
            'ldap.users_config': ldap_users_config,
            'ldap.groups_config': ldap_groups_config,
            'ldap.roles_config': ldap_roles_config
        })

        settings = get_root()['settings']
        settings['ldap_users'].create_container()
        settings['ldap_groups'].create_container()
        settings['ldap_roles'].create_container()
        ugm_backend.initialize()


ldap_layer = LDAPLayer()

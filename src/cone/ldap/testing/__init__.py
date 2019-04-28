from cone.app import get_root
from cone.app.testing import Security
from cone.ldap.settings import ldap_cfg
from cone.ugm.model.settings import ugm_cfg
from node.ext.ldap.testing import LDIF_base
from plone.testing import Layer
import os
import shutil
import tempfile


base_path = os.path.split(__file__)[0]
ugm_config = os.path.join(base_path, 'ugm.xml')
ldap_server_config = os.path.join(base_path, 'ldap_server.xml')
ldap_users_config = os.path.join(base_path, 'ldap_users.xml')
ldap_groups_config = os.path.join(base_path, 'ldap_groups.xml')
ldap_roles_config = os.path.join(base_path, 'ldap_roles.xml')


def _invalidate_settings():
    settings = get_root()['settings']
    settings['ugm'].invalidate()
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


def temp_directory(fn):
    """Decorator for tests needing a temporary directory.
    """
    def wrapper(*a, **kw):
        tempdir = tempfile.mkdtemp()
        kw['tempdir'] = tempdir
        try:
            fn(*a, **kw)
        finally:
            shutil.rmtree(tempdir)
    return wrapper


class LDAPLayer(Security, Layer):
    defaultBases = (LDIF_base,)

    def __init__(self):
        Layer.__init__(self)

    def make_app(self):
        super(LDAPLayer, self).make_app(**{
            'cone.plugins': 'cone.ldap\ncone.ugm',
            'ugm.backend': 'ldap',
            'ugm.config': ugm_config,
            'ldap.server_config': ldap_server_config,
            'ldap.users_config': ldap_users_config,
            'ldap.groups_config': ldap_groups_config,
            'ldap.roles_config': ldap_roles_config
        })


ldap_layer = LDAPLayer()

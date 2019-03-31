from cone.app.testing import Security
from node.ext.ldap.testing import LDIF_base
from plone.testing import Layer
import os


base_path = os.path.split(__file__)[0]
ugm_config = os.path.join(base_path, 'ugm.xml')
ldap_server_config = os.path.join(base_path, 'ldap_server.xml')
ldap_users_config = os.path.join(base_path, 'ldap_users.xml')
ldap_groups_config = os.path.join(base_path, 'ldap_groups.xml')
ldap_roles_config = os.path.join(base_path, 'ldap_roles.xml')


class LDAPLayer(Security, Layer):
    defaultBases = (LDIF_base,)

    def __init__(self):
        Layer.__init__(self)

    def make_app(self):
        super(LDAPLayer, self).make_app(**{
            'cone.plugins': 'cone.ldap',
            'ugm.backend': 'ldap',
            'ugm.config': ugm_config,
            'ldap.server_config': ldap_server_config,
            'ldap.users_config': ldap_users_config,
            'ldap.groups_config': ldap_groups_config,
            'ldap.roles_config': ldap_roles_config
        })


ldap_layer = LDAPLayer()

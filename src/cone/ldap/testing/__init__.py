from cone.app.testing import Security
from node.ext.ldap.testing import LDIF_groupOfNames_10_10
from plone.testing import Layer
import os


class LDAPLayer(Security, Layer):
    defaultBases = (LDIF_groupOfNames_10_10,)

    def __init__(self):
        Layer.__init__(self)

    def make_app(self):
        base_path = os.path.split(__file__)[0]
        ldap_config = os.path.join(base_path, 'ldap.xml')
        localmanager_config = os.path.join(base_path, 'localmanager.xml')
        super(LDAPLayer, self).make_app(**{
            'cone.plugins': 'cone.ugm\ncone.ldap',
            'ugm.backend': 'ldap',
            'ugm.localmanager_config': localmanager_config,
            'ldap.config': ldap_config,
        })


ldap_layer = LDAPLayer()

from cone.app.testing import Security
from node.ext.ldap.testing import LDIF_groupOfNames_10_10
from plone.testing import Layer
import os
import pkg_resources


class LDAPLayer(Security, Layer):
    defaultBases = (LDIF_groupOfNames_10_10,)

    def __init__(self):
        Layer.__init__(self)

    def setUp(self, args=None):
        super(LDAPLayer, self).setUp(args)
        import cone.ugm
        path = pkg_resources.resource_filename('cone.ugm.testing', 'ldap.xml')
        cone.ugm.model.utils.LDAP_CFG_FILE = path
        cone.ugm.model.settings._invalidate_ugm_settings(cone.app.get_root())
        ugm = cone.ugm.model.utils.ugm_backend(cone.app.get_root())
        roles = ['viewer', 'editor', 'admin', 'manager']

        def create_user(uid):
            data = {
                'cn': uid,
                'sn': uid,
                'mail': '%s@example.com' % uid,
            }
            user = ugm.users.create(uid, **data)
            ugm()
            ugm.users.passwd(uid, None, 'secret')
            return user
        for uid in ['viewer', 'editor', 'admin', 'manager', 'max', 'sepp']:
            user = create_user(uid)
            if uid in roles:
                user.add_role(uid)
        for uid in ['localmanager_1', 'localmanager_2']:
            create_user(uid)
        for gid, uid in [('admin_group_1', 'localmanager_1'),
                         ('admin_group_2', 'localmanager_2')]:
            group = ugm.groups.create(gid)
            group.add(uid)
        ugm()

    def tearDown(self):
        super(LDAPLayer, self).tearDown()
        import cone.app
        ugm = cone.app.cfg.auth
        for uid in ['viewer', 'editor', 'admin', 'manager', 'max', 'sepp',
                    'localmanager_1', 'localmanager_2']:
            del ugm.users[uid]
        for gid in ['admin_group_1', 'admin_group_2']:
            del ugm.groups[gid]
        ugm.users()

    def make_app(self):
        base_path = os.path.split(__file__)[0]
        ldap_config = os.path.join(base_path, 'ldap.xml')
        localmanager_config = os.path.join(base_path, 'localmanager.xml')
        super(LDAPLayer, self).make_app(**{
            'cone.auth_impl': 'node.ext.ldap',
            'cone.plugins': 'node.ext.ugm\ncone.ugm',
            'cone.ugm.ldap_config': ldap_config,
            'cone.ugm.localmanager_config': localmanager_config,
        })
        LDIF_groupOfNames_10_10.gcfg.attrmap['cn'] = 'cn'


ldap_layer = LDAPLayer()

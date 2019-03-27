cone.ldap.model.settings
=======================

Test imports::

    >>> from cone.ldap.model.settings import GroupsSettings
    >>> from cone.ldap.model.settings import ServerSettings
    >>> from cone.ldap.model.settings import UsersSettings
    >>> from node.base import OrderedNode
    >>> from node.ext.ldap.properties import LDAPProps
    >>> import cone.app
    >>> import cone.ldap
    >>> import os
    >>> import pkg_resources

App path for testing::

    >>> path = pkg_resources.resource_filename('cone.ldap', '')
    >>> path = os.path.sep.join(path.split(os.path.sep)[:-3])
    >>> path
    '...cone.ldap'

Dummy settings container::

    >>> settings = OrderedNode()
    >>> settings['ldap_server'] = ServerSettings()
    >>> settings['ldap_users'] = UsersSettings()
    >>> settings['ldap_groups'] = GroupsSettings()

LDAP props::

    >>> props = settings['ldap_server'].ldap_props
    >>> props.uri
    u'ldap://127.0.0.1:12345'

    >>> props.user
    u'cn=Manager,dc=my-domain,dc=com'

    >>> props.password
    u'secret'

    >>> md = settings['ldap_server'].metadata
    >>> md.title
    u'ldap_props_node'

    >>> md.description
    u'ldap_props_node_description'

LDAP users config::

    >>> ucfg = settings['ldap_users'].ldap_ucfg
    >>> ucfg.baseDN
    u'ou=users,ou=groupOfNames_10_10,dc=my-domain,dc=com'

    >>> ucfg.attrmap
    {'cn': 'cn', 
    'userPassword': 'userPassword', 
    u'jpegPhoto': u'jpegPhoto', 
    'sn': 'sn', 
    'mail': 'mail', 
    'login': 'uid', 
    'rdn': 'uid', 
    'id': 'uid'}

    >>> ucfg.scope
    1

    >>> ucfg.queryFilter
    u''

    >>> ucfg.objectClasses
    [u'top', u'person', u'organizationalPerson', u'inetOrgPerson']

    >>> md = settings['ldap_users'].metadata
    >>> md.title
    u'user_settings_node'

    >>> md.description
    u'user_settings_node_description'

LDAP groups config::

    >>> gcfg = settings['ldap_groups'].ldap_gcfg
    >>> gcfg.baseDN
    u'ou=groups,ou=groupOfNames_10_10,dc=my-domain,dc=com'

    >>> gcfg.attrmap
    {'rdn': 'cn', 
    'id': 'cn'}

    >>> gcfg.scope
    1

    >>> gcfg.queryFilter
    u''

    >>> gcfg.objectClasses
    [u'groupOfNames']

    >>> md = settings['ldap_groups'].metadata
    >>> md.title
    u'group_settings_node'

    >>> md.description
    u'group_settings_node_description'

LDAP connectivity tests::

    >>> props = LDAPProps(
    ...     uri='ldap://127.0.0.1:12346/',
    ...     user='',
    ...     password='',
    ...     cache=False,
    ... )

    >>> settings['ldap_server']._ldap_props = props

    >>> settings['ldap_server'].ldap_connectivity
    False

    >>> settings['ldap_users'].ldap_users_container_valid
    False

    >>> settings['ldap_groups'].ldap_groups_container_valid
    False

    >>> settings['ldap_server']._ldap_props = layer['props']
    >>> settings['ldap_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ldap_groups']._ldap_gcfg = layer['gcfg']

    >>> settings['ldap_server'].ldap_connectivity
    True

    >>> settings['ldap_users'].ldap_users_container_valid
    True

    >>> settings['ldap_groups'].ldap_groups_container_valid
    True

Settings are written on ``__call__``. At the moment all settings are in one
file, so calling either ucfg, gcfg or props writes all of them::

    >>> settings['ldap_server']()

Test invalidate::

    >>> root = cone.app.root

    >>> settings = root['settings']
    >>> settings
    <AppSettings object 'settings' at ...>

    >>> props = settings['ldap_server'].ldap_props
    >>> props
    <node.ext.ldap.properties.LDAPServerProperties object at ...>

    >>> ucfg = settings['ldap_users'].ldap_ucfg
    >>> ucfg
    <node.ext.ldap.ldap._api.UsersConfig object at ...>

    >>> gcfg = settings['ldap_groups'].ldap_gcfg
    >>> gcfg
    <node.ext.ldap.ldap._api.GroupsConfig object at ...>

    >>> from cone.ugm.model.utils import ugm_backend
    >>> backend = ugm_backend(root)

    >>> backend
    <Ugm object 'ldap_ugm' at ...>

    >>> backend is ugm_backend(root)
    True

    >>> settings = root['settings']
    >>> props = settings['ldap_server'].ldap_props
    >>> ucfg = settings['ldap_users'].ldap_ucfg
    >>> gcfg = settings['ldap_groups'].ldap_gcfg

    >>> props is settings['ldap_server'].ldap_props
    True

    >>> ucfg is settings['ldap_users'].ldap_ucfg
    True

    >>> gcfg is settings['ldap_groups'].ldap_gcfg
    True

    >>> settings['ldap_server'].invalidate()
    >>> backend is ugm_backend(root)
    False

    >>> props is settings['ldap_server'].ldap_props
    False

    >>> ucfg is settings['ldap_users'].ldap_ucfg
    False

    >>> gcfg is settings['ldap_groups'].ldap_gcfg
    False

Cleanup. Reset backend and prepare settings for following tests::

    >>> cone.ugm.backend = None
    >>> settings['ldap_server']._ldap_props = layer['props']
    >>> settings['ldap_users']._ldap_ucfg = layer['ucfg']
    >>> settings['ldap_groups']._ldap_gcfg = layer['gcfg']

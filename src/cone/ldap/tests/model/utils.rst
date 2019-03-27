cone.ldap.model.utils
=====================

::

    >>> from cone.app import root
    >>> from cone.ldap.model.utils import ugm_backend
    >>> from cone.ldap.model.utils import ldap_groups
    >>> from cone.ldap.model.utils import ldap_server
    >>> from cone.ldap.model.utils import ldap_users

    >>> ldap_server(root)
    <ServerSettings object 'ldap_server' at ...>

    >>> ldap_users(root)
    <UsersSettings object 'ldap_users' at ...>

    >>> ldap_groups(root)
    <GroupsSettings object 'ldap_groups' at ...>

    >>> import cone.app
    >>> cone.app.backend = None

    >>> backend = ugm_backend(root)
    >>> backend
    <Ugm object 'ldap_ugm' at ...>

    >>> backend is ugm_backend(root)
    True

    >>> import cone.app
    >>> cone.app.cfg.auth = None
    >>> backend is ugm_backend(root)
    False

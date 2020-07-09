.. image:: https://img.shields.io/pypi/v/cone.ldap.svg
    :target: https://pypi.python.org/pypi/cone.ldap
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/cone.ldap.svg
    :target: https://pypi.python.org/pypi/cone.ldap
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/bluedynamics/cone.ldap.svg?branch=master
    :target: https://travis-ci.org/bluedynamics/cone.ldap

.. image:: https://coveralls.io/repos/github/bluedynamics/cone.ldap/badge.svg?branch=master
    :target: https://coveralls.io/github/bluedynamics/cone.ldap?branch=master

Plugin for `cone.app <http://packages.python.org/cone.app>`_ providing LDAP
integration.


Features
--------

- LDAP access via ``node.ext.ldap``
- Application integration into ``cone.app``
- Integration into ``cone.ugm``
- POSIX support
- Samba support


Development Setup
=================

Prerequirements
---------------

``lxml``, ``python-ldap`` and ``openldap`` gets compiled, the required dev
headers must be installed on the system.

On debian based systems install:

.. code-block:: shell

    $ apt-get install -y libxml2-dev libxslt1-dev
    $ apt-get install -y libsasl2-dev libssl-dev libdb-dev


Installation
------------

``cone.ldap`` contains a buildout configuration. Download or checkout package
and run:

.. code-block:: shell

    cone.ldap$ ./bootstrap.sh python3

Start Test LDAP server with appropriate LDIF layer:

.. code-block:: shell

    cone.ldap$ ./bin/testldap start groupOfNames_10_10

Start the application:

.. code-block:: shell

    cone.ldap$ ./bin/pserve cfg/gon_10_10/ldap_gon_10_10.ini

and browse ``http://localhost:8081/``. Default ``admin`` user password is
``admin``.

The "roles" behavior in the principal form is only displayed if roles
configuration is sane. The LDIF imported for test layer does not provide the
roles container by default. Browse "Settings -> LDAP Roles" and perform
"create roles container" action if you want to enable roles in the demo.

**Note**: If ``python_ldap`` fails, don't use buildout offline mode!


Configuration and Customization
===============================

General
-------

For customizing the plugin, make an integration package and include it in
your setup.


Application configuration
-------------------------

To define the LDAP related configuration locations, provide the following
settings in your application ini file.

.. code-block:: ini

    # LDAP UGM backend activation
    ugm.backend = ldap

    # Basic LDAP server configuration
    ldap.server_config = /path/to/ldap_server.xml

    # LDAP UGM backend related configuration
    ldap.users_config = /path/to/ldap_users.xml
    ldap.groups_config = /path/to/ldap_groups.xml
    ldap.roles_config = /path/to/ldap_roles.xml

Examples of these configuration file can be found at ``cfg`` folder of the
source package.


UGM Default values and default value callbacks
----------------------------------------------

Depending on the LDAP object classes used for users and groups, more or less
attributes are required for the entries. Maybe not all of these attributes
should be visible to the user. Some might even require to be computed.
Therefor the plugin supports default values and default value callbacks.

Default values and callbacks are registered via ``factory_defaults.users``,
``factory_defaults.groups`` and ``factory_defaults.roles``.

.. code-block:: python

    from cone.ldap.settings import factory_defaults

The factory defaults can be static values.

.. code-block:: python

    factory_defaults.user['someField'] = '12345'

Default value callbacks get the principal node and id as attributes.

.. code-block:: python

    def some_field_callback(node, id):
        return 'some computed value'

    factory_defaults.user['someField'] = some_field_callback


Samba support
-------------

Example configuration to enable samba support.

.. code-block:: python

    from cone.ldap.settings import factory_defaults
    from node.ext.ldap.ugm import posix
    from node.ext.ldap.ugm import shadow
    from node.ext.ldap.ugm import samba

    samba.SAMBA_LOCAL_SID = 'S-1-5-21-1234567890-1234567890-1234567890'
    samba.SAMBA_DEFAULT_DOMAIN = 'yourdomain'
    samba.SAMBA_PRIMARY_GROUP_SID = 'S-1-5-21-1234567890-1234567890-1234567890-123'

    user = factory_defaults.user
    user['gidNumber'] = posix.memberGid
    user['loginShell'] = posix.loginShell
    user['shadowFlag'] = shadow.shadowFlag
    user['shadowMin'] = shadow.shadowMin
    user['shadowMax'] = shadow.shadowMax
    user['shadowWarning'] = shadow.shadowWarning
    user['shadowInactive'] = shadow.shadowInactive
    user['shadowLastChange'] = shadow.shadowLastChange
    user['shadowExpire'] = shadow.shadowExpire
    user['sambaSID'] = samba.sambaUserSID
    user['sambaDomainName'] = samba.sambaDomainName
    user['sambaPrimaryGroupSID'] = samba.sambaPrimaryGroupSID
    user['sambaAcctFlags'] = samba.sambaAcctFlags
    user['sambaPwdLastSet'] = samba.sambaPwdLastSet

    group = factory_defaults.group
    factory_defaults.group['memberUid'] = posix.memberUid


Contributors
============

- Robert Niederreiter (Author)


Copyright
=========

Copyright (c) 2019, BlueDynamics Alliance, Austria
All rights reserved.

cone.ldap
=========

Plugin for `cone.app <http://packages.python.org/cone.app>`_ providing LDAP
integration.


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


Contributors
============

- Robert Niederreiter (Author)


Copyright
=========

Copyright (c) 2019, BlueDynamics Alliance, Austria
All rights reserved.

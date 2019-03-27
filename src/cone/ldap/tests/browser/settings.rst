cone.ldap.browser.settings
==========================

::

    >>> from cone.app import root
    >>> from cone.tile import render_tile

    >>> server_settings = root['settings']['ldap_server']
    >>> users_settings = root['settings']['ldap_users']
    >>> groups_settings = root['settings']['ldap_groups']

    >>> request = layer.new_request()

Unauthenticated content tile raises error::

    >>> render_tile(server_settings, request, 'content')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: ... failed permission check

    >>> render_tile(users_settings, request, 'content')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: ... failed permission check

    >>> render_tile(groups_settings, request, 'content')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: ... failed permission check

Form tiles raise if not manager::

    >>> layer.login('editor')

    >>> render_tile(server_settings, request, 'editform')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.ldap.browser.settings.ServerSettingsForm object at ...> 
    failed permission check

    >>> render_tile(users_settings, request, 'editform')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.ldap.browser.settings.UsersSettingsForm object at ...> 
    failed permission check

    >>> render_tile(groups_settings, request, 'editform')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.ldap.browser.settings.GroupsSettingsForm object at ...> 
    failed permission check

Authenticate and render tiles::

    >>> layer.login('manager')

    >>> res = render_tile(server_settings, request, 'editform')
    >>> expected = 'form action="http://example.com/settings/ldap_server/edit"'
    >>> res.find(expected) > -1
    True

    >>> res = render_tile(users_settings, request, 'editform')
    >>> expected = 'form action="http://example.com/settings/ldap_users/edit"'
    >>> res.find(expected) > -1
    True

    >>> res = render_tile(groups_settings, request, 'editform')
    >>> expected = 'form action="http://example.com/settings/ldap_groups/edit"'
    >>> res.find(expected) > -1
    True

    >>> layer.logout()

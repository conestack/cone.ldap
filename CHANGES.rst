Changes
=======

2.0.2 (unreleased)
------------------

- Nothing changed yet.


2.0.1 (2026-10-31)
------------------

- Use ``YAMLEditFormTarget`` for the settings forms, ``YAMLForm.form_action``
  is deprecated.
  [rnix]

- Sort the imports with ruff (one per line, ``from`` imports first, no
  sections) and format the code with ``ruff format`` (90 characters per line,
  single quotes).
  [rnix]

- Add import sorting (``I`` rules) and the formatter settings to the ruff
  configuration in ``pyproject.toml``.
  [rnix]


2.0.0 (2026-10-24)
------------------

- Modernise the code ruff flags as outdated: ``u''`` prefixes, ``class
  X(object)``. Behaviour unchanged. ``super(Class, self)`` is kept, see
  ``cone.app``.
  [rnix]

- Add ``qa.ruff`` domain to Makefile and pin the ruff rule selection in
  ``pyproject.toml``, ``make check`` runs ``ruff check``.
  [rnix]

- Check out ``cone.app``, ``cone.ugm`` and ``treibstoff`` from their 2.0
  branches in ``mx.ini`` and pin ``setuptools<82.0.0``. ``make install`` failed
  on the ``cone.ugm>1.99`` requirement, and ``pyramid`` 2.0.2 still imports
  ``pkg_resources``, which ``setuptools`` 82 removed.
  [rnix]

- Bootstrap 5 styles.


1.1.0 (2026-02-03)
------------------

- Refactor package layout to use ``pyproject.toml`` and implicit namespace packages.
  [rnix]

- Adopt Settings UI changes from ``cone.app``.
  [rnix]

- Use ``webresource`` for resource registration.
  [rnix]


0.3 (2025-10-25)
----------------

- Pin upper versions of dependencies.
  [rnix]


0.2 (2022-12-05)
----------------

- Move ``users_expires_attr`` and ``users_expires_unit`` settings from cone.ugm,
  since they always have been used only for LDAP UGM backend.


0.1 (2020-07-09)
----------------

- Initial release.


dephell_changelogs
==================

Installation
------------

.. code-block:: bash

   python3 -m pip install --user dephell_changelogs

Usage
-----

Get changelog url:

.. code-block:: python

   from dephell_changelogs import get_changelog_url

   url = get_changelog_url('dephell')
   url = get_changelog_url('https://dephell.readthedocs.io/')
   url = get_changelog_url('https://github.com/dephell/dephell/')

Parse changelog:

.. code-block:: python

   from dephell_changelogs import parse_changelog

   parsed = parse_changelog(url)
   parsed['0.8.0']
   # 'New commands:\n\n+ [dephell package bug]...'

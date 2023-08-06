Google Play Music - Playlist Generator
======================================

|build status|

This is a command-line tool to generate a set of standard playlists for
Google Play Music libraries.

It's currently in beta, and some knowledge of Python and comfort with
the command line is required. Depending on interest, I will make it more
user friendly. The author is using the tool and care is being taken not
to make a mess in the library manipulated (I care about mine too), but
USE AT YOUR OWN RISK.

Installation
------------

You can either do a:

.. code::

    pip install GPM-Playlist-Generator

or if you've cloned this repo:

.. code::

    python setup.py install

Running the tool
----------------

Simply run:

.. code::

    gpm-playlistgen.py config.yaml

What it does
------------

The default configuration captured in ``config.sample.yaml`` will log
prompt you to log into your account via OAuth, download the list of tracks
and playlists in your library, and do the following as per the ``playlist``
section in the configuration:

-  Generate a set of playlists grouping your tracks by month in which
   they've been added to your library (``monthly_added``)
-  Generate a sorted list of your most frequently played tracks
   (``most_played``)

The playlist generated will all have a name starting with "[PG]". This
is configurable.

If you rerun the tool, it will only regenerate the playlists that are
needed (new tracks in monthly added, and most played).

I need help
-----------

Try:

.. code::

    gpm-playlistgen.py config.yaml

I want to report a problem or I have a cool idea for this tool
--------------------------------------------------------------

Please use the `issue
tracker <https://gitlab.com/hugoh/gpm-playlistgen/issues>`__.

FAQ
---

I don't trust this tool
~~~~~~~~~~~~~~~~~~~~~~~

"No problem". You can run it with the ``--dry-run`` option. It will not
write anything to your account, simply show you what it would do.

I want to get rid of all those generated playlists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can run:

.. code::

    gpm-playlistgen.py --delete-all-playlists config.yaml

The description field is used to check that this is a generated list,
but I strongly advise to the the following first to see what it's going
to do:

.. code::

    gpm-playlistgen.py --delete-all-playlists config.yaml --dry-run

Credits
-------

The heavy lifting is done by `Simon Weber's
gmusicapi <https://github.com/simon-weber/gmusicapi>`__.

.. |build status| image:: https://gitlab.com/hugoh/gpm-playlistgen/badges/master/pipeline.svg
   :target: https://gitlab.com/hugoh/gpm-playlistgen/commits/master

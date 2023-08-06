About
=====

A websocket server written in Python.
It uses [GIO](https://developer.gnome.org/gio/) for network communication and
hence it easily integrates with the
[GLib](https://developer.gnome.org/glib/) mainloop.

Some code is derived from Tulip, a reference implementation of PEP
3156, by Guido van Rossum.

Hacking
=======

Please run lint before submitting pull requests

    python setup.py lint

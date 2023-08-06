# Deluge Web Browser


---

Deluge Web Browser is a plugin for [Deluge](http://deluge-torrent.org) that
can be used to browse the downloaded torrents by starting a webserver.

This is only a webui plugin at the moment, and the parametrisation needs to be done by *hand*
(if the default configuration is not satisfactory).

The plugin add a torrent submenu to browse the downloaded folder, then directory or the downloaded file,
or retrieve it content in a zip.

Features
--------
- Web browser
- Browse the standard download directory
- Download all files of a torrent in a zip.

Compatibility
-------------
- Requires at least Deluge 1.3.3
- Was not tested on Deluge 2.x

Limitations / Todo
-------------
- Create interface for customisation in the WebUi
- Use the *twisted" native web server to serve the files, as
[SimpleHTTPServer](https://docs.python.org/2/library/simplehttpserver.html#module-SimpleHTTPServer)
is not recommended for production
- Maybe a GTK plugin, but unlikely to be high priority considering the main usage of the tool

## Installation
**Stable Release:** `pip install DelugeWebBrowser`<br>
**Development Head:** `pip install git+https://github.com/aerospeace/DelugeWebBrowser.git`

## Documentation
Docuemntation is not yet there. Will come on following site when available:
[aerospeace.github.io/DelugeWebBrowser](https://aerospeace.github.io/DelugeWebBrowser).

## Development
See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

## The Four Commands You Need To Know
1. `pip install -e .[dev]`

    This will install your package in editable mode with all the required development dependencies (i.e. `tox`).

2. `make build`

    This will run `tox` which will run all your tests in both Python 3.6 and Python 3.7 as well as linting your code.

    At the moment there is not test integrated

3. `make clean`

    This will clean up various Python and build generated files so that you can ensure that you are working in a clean
    environment.

4. `make docs`

    This will generate and launch a web browser to view the most up-to-date documentation for your Python package.

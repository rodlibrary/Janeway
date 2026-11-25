![Janeway Logo](https://www.openlibhums.org/media/press/Janeway_RGB_Keyline_Logo_Black.png "Janeway")

Janeway is a web-based platform for publishing journals, preprints, conference proceedings, and books. It is developed and maintained by a team of developers at the Open Library of Humanities, part of Birkbeck, University of London.

# Technology
Janeway is written in Python (3.10+) and utilises the Django framework (4.2).

# Installation instructions
Developer installation [instructions are available in our documentation site](https://janeway.readthedocs.io/en/latest/dev/installation.html).

A guide for installing on the live environment with [apache and mod_wsgi](https://github.com/openlibhums/janeway/wiki/Janeway%2C-Apache-and-WSGI) is also available.

## Running Janeway with docker
Janeway's development server can be run within a docker container, avoiding the need to install and run its dependencies from your machine. A docker compose file as well as a Makefile can be found at the root of the project wrapping the most common operations.
Docker is compatible with multiple architectures and Operating systems, if you need help installing docker, have a look at the [docker documentation](https://docs.docker.com/install/).

Simarly to the native installation, Janeway can be installed in a docker environment by running ``make install`` and following the installation steps described [above](https://github.com/openlibhums/janeway/wiki/Installation). As a result, a database volume will be populated under janeway/db/postgres-data
Once installation is completed, just type ``make janeway`` to run janeway with a postgres backend (default behaviour).

If a change to the dependencies for Janeway is required, the Janeway container can be re-created with ``make rebuild``. The database volume will be preserved.

In order to run a different RDBMS, the environment variable ``DB_VENDOR`` can be set to one of ``postgres``, ``mysql`` or ``sqlite``. e.g: ``DB_VENDOR=mysql make install && make``

Uninstalling Janeway is as simple as running ``make uninstall`` which will delete all docker related containers as well as wipe the database volume.
# Major Releases
All releases are listed on the [releases](https://github.com/openlibhums/janeway/releases) page.


# Geolocation
Janeway includes GeoLite2 data created by MaxMind, available from [https://www.maxmind.com](https://www.maxmind.com)

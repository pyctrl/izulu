Contributors
============

For developers
**************

1. Install required tools

   * `uv <https://docs.astral.sh/uv/>`__ (manually)
   * `Taplo <https://taplo.tamasfe.dev/>`__ (manually)
   * `Tox <https://tox.wiki/en/stable/>`__

     .. code-block:: shell

        uv tool install tox --with tox-uv

2. Clone `repository <https://github.com/pyctrl/izulu>`__

3. Initialize developer's environment

   .. code-block:: shell

       uv sync
       tox run -e init

4. Run tests

   .. code-block:: shell

       # run only mypy env
       tox run -e lint-mypy

       # run all linting envs (labeled)
       tox run -m lint

       # run only ruff formatting env
       tox run -e fmt-py

       # run all formatting envs (labeled)
       tox run -m fmt

       # list all envs
       tox list

       # run all envs
       tox run

5. Contributing — start from opening an `issue <https://github.com/pyctrl/izulu/issues>`__


Versioning
**********

`SemVer <http://semver.org/>`__ used for versioning.
For available versions see the repository
`tags <https://github.com/pyctrl/izulu/tags>`__
and `releases <https://github.com/pyctrl/izulu/releases>`__.

======
pep582
======


.. image:: https://img.shields.io/pypi/v/pep582.svg
        :target: https://pypi.python.org/pypi/pep582

.. image:: https://img.shields.io/travis/pawnhearts/pep582.svg
        :target: https://travis-ci.org/pawnhearts/pep582

.. image:: https://readthedocs.org/projects/pep582/badge/?version=latest
        :target: https://pep582.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




implements pep582(adds __pypackages__ to PYTHONPATH) via patching site.py

https://www.python.org/dev/peps/pep-0582/

there are 2 other ways - patched interpreter from pep and https://pypi.org/project/pythonloc/

pythonloc requires using pythonloc instad of python command. and patched interpeter is generally hard it's more of POC.

my module allows to use your regular python binary.

to patch site.py run python -m pep582.patch

if you create __pypackages__ directorry inside your projects:

"pip install" would install there by default

to install elsewhere use -t/--target

modules would me imported from there first


* Free software: MIT license
* Documentation: https://pep582.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

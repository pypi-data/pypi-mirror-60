======
pep582
=====


implements pep582(adds __pypackages__ to PYTHONPATH) via patching site.py

https://www.python.org/dev/peps/pep-0582/

there are 2 other ways - patched interpreter from pep and https://pypi.org/project/pythonloc/

pythonloc requires using pythonloc instad of python command. and patched interpeter is generally hard it's more of POC.

my module allows to use your regular python binary.

"pip install" would install to __pypackages__ by default

to install elsewhere use -t/--target

modules would me imported from there first


* Free software: MIT license

Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

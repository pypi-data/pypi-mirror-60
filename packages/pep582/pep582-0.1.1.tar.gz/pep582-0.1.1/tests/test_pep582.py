#a!/usr/bin/env python
"""Tests for `pep582` package."""


import unittest
import tempfile
import os


class TestPep582(unittest.TestCase):
    """Tests for `pep582` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        os.chdir(tempfile.mkdtemp())
        print(os.getcwd())
        os.mkdir('__pypackages__')

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_pip_install(self):
        """Test pip install."""
        os.system('pip install pythonloc')
        self.assertEqual(os.system('test -e __pypackages__/*/lib/pythonloc/'), 0)  # assuming we are on unix, sorry

    def test_import_module(self):
        """Test import module."""
        os.system('pip install pythonloc')
        import pythonloc
        self.assertTrue(pythonloc.__file__.startswith('__pypackages__'))

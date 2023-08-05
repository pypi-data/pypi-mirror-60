#a!/usr/bin/env python
"""Tests for `pep582` package."""
import importlib
import unittest
import tempfile
import os
from subprocess import check_call


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
        check_call('pip install tinydb')
        self.assertEqual(os.system('test -e __pypackages__/*/lib/tinydb/'), 0)  # assuming we are on unix, sorry

    def test_import_module(self):
        """Test import module."""
        check_call('pip install tinydb')
        self.assertTrue(getattr(importlib.import_module('tinydb'), '__file__', '.').startswith('__pypackages__'))

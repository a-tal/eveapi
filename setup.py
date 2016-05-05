#!/usr/bin/env python

import io
import re
import platform

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


PYVER = platform.sys.version_info
if platform.python_implementation() != "PyPy" and (PYVER < (2, 7) or
   (PYVER.major == 3 and PYVER.minor < 4)):
    raise SystemExit("requires PyPy, Python2.7 or Python3.4+")


class PyTest(TestCommand):
    """TestCommand subclass to use pytest with setup.py test."""

    def finalize_options(self):
        """Find our package name and test options to fill out test_args."""

        TestCommand.finalize_options(self)
        self.test_args = ['-v', '-rx', '-x', '--pdb', '--cov-report',
                          'term-missing', '--cov', 'eveapi', 'tests']
        self.test_suite = True

    def run_tests(self):
        """pytest discovery and test execution."""

        # HACK
        import os
        os.environ["EVEAPI_TEST_KEYID"] = ""
        os.environ["EVEAPI_TEST_VCODE"] = ""
        # HACK

        import pytest
        raise SystemExit(pytest.main(self.test_args))


def find_version(filename):
    """Uses re to pull out the assigned value to VERSION in filename."""

    with io.open(filename, 'r', encoding='utf-8') as version_file:
        version_match = re.search(r'^VERSION = [\'"]([^\'"]*)[\'"]',
                                  version_file.read(), re.M)
    if version_match:
        return version_match.group(1)
    return '0.0.0'


setup(
    name='eveapi',
    version=find_version('eveapi/__init__.py'),
    description='Python library for accessing the EVE Online API.',
    author='Jamie van den Berge',
    author_email='jamie@hlekkir.com',
    url='https://github.com/ntt/eveapi',
    keywords=('eve-online', 'api'),
    cmdclass={'test': PyTest},
    tests_require=['mock', 'pytest', 'pytest-cov'],
    platforms='any',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Games/Entertainment',
    ),
    zip_safe=True,
    packages=find_packages(),
)

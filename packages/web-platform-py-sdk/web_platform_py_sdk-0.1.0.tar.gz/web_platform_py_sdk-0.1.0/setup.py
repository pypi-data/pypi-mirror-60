#!/usr/bin/env python

from __future__ import print_function

import sys

from setuptools import setup

if sys.version_info < (3, 6):
    print("Python versions prior to 3.6 are not supported for pip installed web_platform_py_sdk.",
          file=sys.stderr)
    sys.exit(-1)

try:
    exec(open('tech/mlsql/serviceframework/sdk/version.py').read())
except IOError:
    print("Failed to load web_platform_py_sdk version file for packaging.",
          file=sys.stderr)
    sys.exit(-1)

VERSION = __version__

setup(
    name='web_platform_py_sdk',
    version=VERSION,
    description='web-platform sdk tools',
    long_description="With this lib help you to develop base on web-platform",
    author='ZhuWilliam',
    author_email='allwefantasy@gmail.com',
    url='https://github.com/allwefantasy/sfcli',
    packages=['tech',
              'tech.mlsql',
              'tech.mlsql.serviceframework',
              'tech.mlsql.serviceframework.sdk',
              'tech.mlsql.serviceframework.sdk.plugins',
              'tech.mlsql.serviceframework.sdk.tests',
              ],
    include_package_data=True,
    license='http://www.apache.org/licenses/LICENSE-2.0',
    install_requires=[
        'requests>=2.22.0'],
    setup_requires=['pypandoc'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy']
)

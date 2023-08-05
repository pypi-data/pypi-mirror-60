#!/usr/bin/env python

# This file is part of spot_motion_monitor.
#
# Developed for LSST System Integration, Test and Commissioning.
#
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.command.build import build
from distutils_ui import build_ui

cmdclass = {
    'build_ui': build_ui.build_ui,
}

# Inject ui specific build into standard build process
build.sub_commands.insert(0, ('build_ui', None))

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://spot_motion_monitor.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = None
with open('requirements/prod.txt') as prodFile:
    requirements = [x.strip() for x in prodFile]

test_requirements = None
with open('requirements/test.txt') as testFile:
    test_requirements = [x.strip() for x in testFile]

setup(
    name='spot_motion_monitor',
    version='2.0.3',
    description='User interface for Spot Seeing Monitor.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Michael Reuter',
    author_email='mareuter@lsst.org',
    url='https://github.com/lsst-sitcom/spot_motion_monitor',
    packages=[
        'spot_motion_monitor',
        'spot_motion_monitor.camera',
        'spot_motion_monitor.config',
        'spot_motion_monitor.controller',
        'spot_motion_monitor.models',
        'spot_motion_monitor.utils',
        'spot_motion_monitor.views',
        'spot_motion_monitor.views.forms'
    ],
    package_dir={'spot_motion_monitor': 'spot_motion_monitor',
                 'spot_motion_monitor.camera': 'spot_motion_monitor/camera',
                 'spot_motion_monitor.config': 'spot_motion_monitor/config',
                 'spot_motion_monitor.controller': 'spot_motion_monitor/controller',
                 'spot_motion_monitor.models': 'spot_motion_monitor/models',
                 'spot_motion_monitor.utils': 'spot_motion_monitor/utils',
                 'spot_motion_monitor.views': 'spot_motion_monitor/views',
                 'spot_motion_monitor.views.forms': 'spot_motion_monitor/views/forms'},
    include_package_data=True,
    install_requires=requirements,
    license='BSD 3-Clause License',
    zip_safe=False,
    keywords='spot_motion_monitor',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    cmdclass=cmdclass,
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'gui_scripts': [
            'smm_ui = spot_motion_monitor.views.main_window:main'
        ]
    },
)

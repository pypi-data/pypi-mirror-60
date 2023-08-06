"""Setup inaccel package."""

from __future__ import absolute_import

import io
import os
import setuptools
import sys

CURRENT_DIR = os.path.dirname(__file__)
VERSION = open(os.path.join(CURRENT_DIR, 'inaccel/coral/VERSION')).read().strip()

setuptools.setup(
    name = 'coral-api',
    packages = ['inaccel.coral'],
    namespace_packages=['inaccel'],
    version = VERSION,
    license = 'Apache-2.0',
    description = 'InAccel Python Package',
    author = 'InAccel',
    author_email='info@inaccel.com',
    url = 'https://docs.inaccel.com',
    keywords = ['InAccel', 'Coral', 'API', 'FPGA', 'resource', 'manager'],
    install_requires = [
        'numpy',
    ],
    zip_safe = False,
    include_package_data = True,
    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.5',
)

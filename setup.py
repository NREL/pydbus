"""
pydbus setup.py
"""

import os
from codecs import open

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(HERE, './README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open(
        os.path.join(HERE, 'pydbus', '_version.py'),
        encoding='utf-8',
) as f:
    VERSION = f.read()

VERSION = VERSION.split()[2].strip('"').strip("'")

setup(
    name='pydbus',
    version=VERSION,
    description='Python DBus COSIM',
    long_description=LONG_DESCRIPTION,

    # Author details
    author='Dheepak Krishnamurthy',
    license='BSD-compatible',
    packages=find_packages(),
    install_requires=["future", "six", "click"],
    entry_points={
        "console_scripts": [
            "pydbus = pydbus.cli:cli",
        ],
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

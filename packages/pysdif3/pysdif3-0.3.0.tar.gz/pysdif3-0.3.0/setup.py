"""
************************************************************************
*
* GPL 
*
* This file is part of pysdif
*
* pysdif is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* pysdif is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
* 
* You should have received a copy of the GNU General Public License
* along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
*************************************************************************
"""

import sys
from setuptools import setup, Extension


def get_version():
    d = {}
    with open("pysdif/version.py") as f:
        code = f.read()
    exec(code, d)
    version = d.get('__version__', (0, 0, 0))
    return version


class numpy_include(str):

    def __str__(self):
        import numpy
        return numpy.get_include()

library_dirs = []

compile_args = [
    '-fno-strict-aliasing',
    '-Werror-implicit-function-declaration',
    '-Wfatal-errors'
]

include_dirs = []

if sys.platform == "windows":
    compile_args += ["-march=i686"]
elif sys.platform == "linux":
    include_dirs.append("/usr/local/include/")
    library_dirs.append("/usr/local/lib")
elif sys.platform == "darwin":
    include_dirs.append("/usr/local/include/")
    library_dirs.append("/usr/local/lib")

versionstr = "%d.%d.%d" % get_version()

classifiers = """
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: MacOS
Operating System :: POSIX
Operating System :: Unix
Programming Language :: C
Programming Language :: Cython
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Multimedia :: Sound/Audio
Topic :: Multimedia :: Sound/Audio :: Analysis
Topic :: Multimedia :: Sound/Audio :: Sound Synthesis
Topic :: Multimedia :: Sound/Audio :: Speech
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

long_description = """
SDIF for python

This is a wrapper to IRCAM's SDIF C library, written mostly in Cython.

Needs Cython >= 0.22

It allows to read and write any kind of SDIF file, to define new
kinds of frames and matrices and to read and write metadata. 

The matrices read from a sdif file are exposed as numpy arrays.


See release notes and changes at http://github.com/gesellkammer/pysdif
"""


setup(
    name = "pysdif3",
    python_requires=">=3.6",
    ext_modules = [
        Extension(
            'pysdif._pysdif',
            sources = ['pysdif/_pysdif.pyx', 'pysdif/pysdif.pxd'],
            include_dirs = include_dirs + ['pysdif', numpy_include()],
            libraries = ['sdif'],
            library_dirs = library_dirs,
            extra_compile_args = compile_args,
            extra_link_args = compile_args,
        )
    ],
    setup_requires = [
        'numpy>=1.8',
        'cython>=0.20'
    ],
    install_requires = [
        'numpy>=1.8',
    ],
    packages = ['pysdif'],
    package_dir  = {'pysdif': 'pysdif'},
    package_data = {'pysdif': ['data/*']},
    version  = versionstr,
    url = 'https://github.com/gesellkammer/pysdif',
    author = 'Eduardo Moguillansky',
    author_email = 'eduardo.moguillansy@gmail.com',
    long_description = long_description,
    description = "Wrapper for the SDIF library for audio analysis",
    classifiers = [c for c in classifiers.split('\n') if c]
)

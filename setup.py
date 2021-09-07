# coding: utf-8

# The MIT License (MIT)
# 
# Copyright (c) <2015-2021> <Shibzukhov Zaur, szport at gmail dot com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension

extra_compile_args = ["-O3",]
# extra_compile_args = []
extra_link_args = []

use_cython = 1

if use_cython:
    from Cython.Distutils import Extension, build_ext
    from Cython.Compiler import Options
    Options.fast_fail = True

ext_modules = [
    Extension(
        "recordclass._dataobject",
        ["lib/recordclass/_dataobject.c"],
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
    ),
    Extension(
        "recordclass._litetuple",
        ["lib/recordclass/_litetuple.c"],
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
    ),
]

if use_cython:
    ext_modules.append(Extension(
        "recordclass.litelist",
        ["lib/recordclass/litelist.pyx"],
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
    ))
    ext_modules.append(Extension(
        "recordclass._linkedlist",
        ["lib/recordclass/_linkedlist.pyx"],
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
    ))
else:
    ext_modules.append(Extension(
        "recordclass.litelist",
        ["lib/recordclass/litelist.c"],
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
    ))
    ext_modules.append(Extension(
        "recordclass._linkedlist",
        ["lib/recordclass/_linkedlist.c"],
        extra_compile_args = extra_compile_args,
        extra_link_args = extra_link_args,
    ))

description = """Mutable variant of collections.namedtuple -- recordclass.recordclass, which support assignments, and other memory saving variants."""

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

packages = [ 'recordclass', 
             'recordclass.test',
             'recordclass.test.typing',
             'recordclass.typing',
             'recordclass.tools',
           ]

setup(
    name = 'recordclass',
    version = '0.16.1',
    description = description,
    author = 'Zaur Shibzukhov',
    author_email = 'szport@gmail.com',
    maintainer = 'Zaur Shibzukhov',
    maintainer_email = 'szport@gmail.com',
    license = "MIT License",
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    package_dir = {'': 'lib'},
    packages = packages,
    url = 'https://bitbucket.org/intellimath/recordclass',
    download_url = 'https://pypi.org/project/recordclass/#files',
    long_description=long_description,
    long_description_content_type='text/markdown',
#     description_content_type='text/plain',
    platforms='Linux, Mac OS X, Windows',
    keywords=['namedtuple', 'recordclass', 'dataclass', 'dataobject'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

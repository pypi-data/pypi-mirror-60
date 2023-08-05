#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ) as fh:
        return fh.read()


setup(
    name="subsample-fastas",
    version="0.0.0",
    license="CeCILL 2.1 Free Software License",
    description="Randomly alter fasta files by substracting a given % of genes in a genome (fasta) or in a (% of a) set of genomes ",
    long_description="%s\n%s"
    % (read("README.md"), re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.md"))),
    author="Clémence Frioux",
    author_email="clemence.frioux@inria.fr",
    url="https://gitlab.inria.fr/pleiade/python-subsample_fastas",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        # uncomment if you test on these interpreters:
        # "Programming Language :: Python :: Implementation :: IronPython",
        # "Programming Language :: Python :: Implementation :: Jython",
        # "Programming Language :: Python :: Implementation :: Stackless",
        "Topic :: Utilities",
    ],
    project_urls={
        "Changelog": "https://gitlab.inria.fr/pleiade/python-subsample_fastas/blob/master/CHANGELOG.md",
        "Issue Tracker": "https://gitlab.inria.fr/pleiade/python-subsample_fastas/issues",
    },
    keywords=[
        # eg: "keyword1", "keyword2", "keyword3",
    ],
    python_requires=">=3.7",
    install_requires=[
        "biopython>=1.76",
        "pytest"
        # eg: "numpy", "pandas>=0.23.0",
    ],
    extras_require={
        # eg:
        #   "rst": ["docutils>=0.11"],
        #   ":python_version=="2.6"": ["argparse"],
    },
    entry_points={"console_scripts": ["subsample_fastas = subsample_fastas.cli:main", ]},
)

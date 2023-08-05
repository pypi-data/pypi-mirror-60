#!/usr/bin/env python
# Copyright 2016, Yahoo Inc.
# Licensed under the terms of the Apache License, Version 2.0. See the LICENSE file associated with the project for terms.
import io
import os
import re
from setuptools import setup


with open("README.rst") as f:
    long_description = f.read()

# Grab the version using convention described by flask
# https://github.com/pallets/flask/blob/master/setup.py#L10
with io.open("graphtik/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

plot_reqs = ["matplotlib", "pydot"]  # to test plot  # to test plot
test_reqs = plot_reqs + ["pytest", "pytest-cov", "pytest-sphinx", "dill"]

setup(
    name="graphtik",
    version=version,
    description="Lightweight computation graphs for Python",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Kostis Anagnostopoulos, Huy Nguyen, Arel Cordero, Pierre Garrigues, Rob Hess, "
    "Tobi Baumgartner, Clayton Mellina",
    author_email="ankostis@gmail.com",
    url="http://github.com/pygraphkit/graphtik",
    project_urls={
        "Documentation": "https://graphtik.readthedocs.io/",
        "Release Notes": "https://graphtik.readthedocs.io/en/latest/changes.html",
        "Sources": "https://github.com/pygraphkit/graphtik",
        "Bug Tracker": "https://github.com/pygraphkit/graphtik/issues",
    },
    packages=["graphtik"],
    python_requires=">=3.6",
    install_requires=[
        "contextvars; python_version < '3.7'",
        "networkx; python_version >= '3.5'",
        "networkx == 2.2; python_version < '3.5'",
        "boltons",  # for IndexSet
    ],
    extras_require={
        "plot": plot_reqs,
        "test": test_reqs,
        # May help for pickling `parallel` tasks.
        # See :term:`marshalling` and :func:`set_marshal_tasks()` configuration.
        "dill": ["dill"],
        "all": plot_reqs + test_reqs + ["sphinx"],
    },
    tests_require=test_reqs,
    license="Apache-2.0",
    keywords=[
        "graph",
        "computation graph",
        "DAG",
        "directed acyclical graph",
        "executor",
        "scheduler",
        "etl",
        "workflow",
        "pipeline",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
    ],
    zip_safe=True,
    platforms="Windows,Linux,Solaris,Mac OS-X,Unix",
)

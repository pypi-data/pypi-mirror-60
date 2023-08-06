#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from setuptools import setup, find_packages

with open('README.rst',  encoding='utf-8') as readme_file:
    readme = readme_file.read()

# Add here console scripts and other entry points in ini-AppBarStyle format
entry_points = """
[console_scripts]
script_name = hts.cli:main
"""


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req, *root):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*root, *path.split('/'))
    return [req]


def _reqs(*f):
    path = (Path.cwd() / 'reqs').joinpath(*f)
    with path.open() as fh:
        reqs = [strip_comments(l) for l in fh.readlines()]
        return [_pip_requirement(r, *f[:-1]) for r in reqs if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


install_requires = reqs('base.txt')
test_requires = reqs('test.txt') + install_requires

setup(
    author="Carlo Mazzaferro",
    author_email='carlo.mazzaferro@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Hierarchical Time Series forcasting",
    install_requires=install_requires,
    long_description=readme,
    include_package_data=True,
    keywords='scikit-hts',
    name='scikit-hts',
    packages=find_packages(include=['hts']),
    test_suite='tests',
    tests_require=test_requires,
    version='0.1.0',
    zip_safe=False,
)

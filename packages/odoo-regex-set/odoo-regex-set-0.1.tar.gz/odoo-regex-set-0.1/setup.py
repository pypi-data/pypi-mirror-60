#!/usr/bin/env python

from setuptools import find_packages, setup
from odoo_regex_set import manifest

setup(
    name=manifest.name,
    use_scm_version=True,
    setup_requires=['setuptools_scm', 'pytest_runner'],
    description=manifest.description,
    author=manifest.author,
    author_email=manifest.email,
    url=manifest.url,
    packages=find_packages(exclude=('tests',)),
    install_requires=[
    ],
    tests_require=[
        'pytest<5.0.0',
        'pytest-cov',
        'pytest-random-order',
    ],
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)

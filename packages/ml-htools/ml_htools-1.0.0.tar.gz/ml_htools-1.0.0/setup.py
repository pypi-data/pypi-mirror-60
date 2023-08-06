#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f][11:]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Harrison Mamin",
    author_email='Hmamin2@dons.usfca.edu',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description='Utilities for machine learning using scikit-learn and '
                'PyTorch.',
    entry_points={
        'console_scripts': [
            'ml_htools=ml_htools.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ml_htools',
    name='ml_htools',
    packages=find_packages(include=['ml_htools']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hdmamin/ml_htools',
    version='1.0.0',
    zip_safe=False,
)

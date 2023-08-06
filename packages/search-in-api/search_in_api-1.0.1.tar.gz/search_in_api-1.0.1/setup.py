#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'altgraph==0.17',
    'asn1crypto==1.3.0',
    'certifi==2019.11.28',
    'cffi==1.13.2',
    'chardet==3.0.4',
    'cryptography==2.8',
    'dis3==0.1.3',
    'future==0.18.2',
    'idna==2.8',
    'ipaddress==1.0.23',
    'macholib==1.14',
    'pefile==2019.4.18',
    'pycparser==2.19',
    'PyInstaller==3.6',
    'pyOpenSSL==19.1.0',
    'requests>=2.22.0',
    'urllib3>=1.25.8',
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Aidas Bendoraitis",
    author_email='aidasbend@yahoo.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Search in API is a script that allows you to search among multiple pages of an API endpoint.",
    entry_points={
        'console_scripts': [
            'search_in_api=search_in_api.search_in_api:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='search_in_api',
    name='search_in_api',
    packages=find_packages(include=['search_in_api']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/archatas/search_in_api',
    version='1.0.1',
    zip_safe=False,
)

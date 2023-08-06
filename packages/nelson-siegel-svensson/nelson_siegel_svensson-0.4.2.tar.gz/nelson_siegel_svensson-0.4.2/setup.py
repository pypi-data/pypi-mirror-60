#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The setup script.'''

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0',
                'numpy>=1.14',
                'scipy>=1.2',
                'matplotlib>=3.0']

setup_requirements = []

test_requirements = []

setup(
    author='luphord',
    author_email='luphord@protonmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    description='Implementation of the Nelson-Siegel-Svensson ' +
                'interest rate curve model.',
    entry_points={
        'console_scripts': [
            'nelson_siegel_svensson=nelson_siegel_svensson.cli:cli_main',
        ],
    },
    install_requires=requirements,
    license='MIT license',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='nelson_siegel_svensson',
    name='nelson_siegel_svensson',
    packages=find_packages(include=['nelson_siegel_svensson']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/luphord/nelson_siegel_svensson',
    version='0.4.2',
    zip_safe=False,
)

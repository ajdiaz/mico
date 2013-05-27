#!/usr/bin/env python

import re

from setuptools import setup, find_packages
from os import path

try:
    from setuptools import setup
    extra = dict(test_suite="tests.test.suite", include_package_data=True)
except ImportError:
    from distutils.core import setup
    extra = {}

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)
    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    return dependency_links


def get_file_contents(filename):
    fd = file(path.join(path.dirname(__file__), filename), "r")
    content = fd.read()
    fd.close()
    return content

setup(
    name = "mico",
    version = "0.1",
    description = "A monkey driven cloud management",
    long_description=get_file_contents("README.rst"),
    author='Andres J. Diaz',
    author_email='ajdiaz@connectical.com',
    url='http://ajdiaz.github.com/mico',
    packages=find_packages(),
    install_requires = parse_requirements('requirements.txt'),
    dependency_links = parse_dependency_links('requirements.txt'),
    license = "GPL",
    entry_points={
        'console_scripts': [
            'mico = mico.scripts.cmdline:main',
        ]
    },
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 2.6',
          'Operating System :: OS Independent',
          'Programming Language :: Python'
    ],
    **extra
)

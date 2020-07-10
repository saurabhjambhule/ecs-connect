#!/usr/bin/env python

"""The setup script."""

import os
import codecs
import re
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open(os.path.join(HERE, "requirements.txt"), "r") as fh:
    INSTALL_REQUIRES = [line.strip() for line in fh]

with open(os.path.join(HERE, "requirements_dev.txt"), "r") as fh:
    SETUP_REQUIRES = [line.strip() for line in fh]


setup(
    author="Saurabh Jambhule",
    author_email='saurabhjambhule@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Seamlessly connect to containers running in ECS.",
    entry_points={
        'console_scripts': [
            'ecs_connect=ecs_connect.cli:main',
        ],
    },
    install_requires=INSTALL_REQUIRES,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords=[
        "ecs_connect",
        "ecs",
    ],
    name='ecs_connect',
    packages=find_packages(include=['ecs_connect', 'ecs_connect.*']),
    setup_requires=SETUP_REQUIRES,
    url='https://github.com/saurabhjambhule/ecs_connect',
    version=find_version("ecs_connect/version.py"),
    test_suite='tests',
    zip_safe=False,
)

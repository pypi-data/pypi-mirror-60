from setuptools import setup, find_packages
from sys import platform
from setuptools.command.install import install
import os

with open('requirements.txt', 'r') as req_fp:
    required_packages = req_fp.readlines()

# Use README for long description
with open('README.md', 'r') as readme_fp:
    long_description = readme_fp.read()

setup(
    name="py_cui_2048",
    version="0.0.1",
    author="Jakub Wlodek",
    author_email="jwlodek.dev@gmail.com",
    description="A command line version of the classic 2048 game, built with py_cui.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="BSD 3-Clause",
    keywords="tui command-line cli cui curses 2048",
    url="https://github.com/jwlodek/py_cui_2048",
    packages = find_packages(exclude=['tests', 'docs']),
    entry_points={
        'console_scripts': [
            'py2048 = py_cui_2048:main',
        ],
    },
    install_requires=required_packages,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

)
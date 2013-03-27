#!/usr/bin/env python
# -*- coding: utf-8 -*

from distutils.core import setup, Command
import os

class TestCommand(Command):
    description = "run tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from unittest import TextTestRunner, TestLoader
        loader = TestLoader()
        runner = TextTestRunner(verbosity=2)
        tests = loader.discover('tests')
        runner.run(tests)

def get_packages(package):
    """
    Return root package & all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

setup(
    name='mega.py',
    version='0.9',
    packages=get_packages('mega'),
    package_data=get_package_data('mega'),
    cmdclass=dict(test=TestCommand),
    description='Python lib for the Mega.co.nz API',
    author='Richard O\'Dwyer',
    author_email='richard@richard.do',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'
    ]
)

#!/usr/bin/env python

#import distribute_setup
#distribute_setup.use_setuptools()
from setuptools import setup
#from distutils.command.sdist import sdist
import os

setup(
    name = "Bilbo_core",
    version = '0.0.1',
    package_dir={'bilbo_core': 'src'},
    packages = ['bilbo_core'],
    scripts = ['bin/bilbo.py'],
    author = "Andrew P. Davison",
    author_email = "andrewpdavison@gmail.com",
    description = "A tool for automated tracking of computation-based scientific projects",
    long_description = open('README').read(),
    license = "CeCILL http://www.cecill.info",
    keywords = "computational science neuroscience simulation analysis project-management",
    url = "http://neuralensemble.org/sumatra/",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Environment :: Web Environment',
                   'Intended Audience :: Science/Research',
                   'License :: Other/Proprietary License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering'],
    install_requires = ['Django>=1.2', 'django-tagging'],
    extras_require = {'svn': 'pysvn',
                      'hg': 'mercurial',
                      'git': 'GitPython',
                      'bzr': 'bzrlib',
                      'mpi': 'mpi4py'},
    #test_suite = ?,
    #tests_require = ?,
    #use_2to3 = True,
)


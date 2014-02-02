#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


setup(name='MAGeT',
      version='0.0.1',
      author='Jon Pipitone',
      author_email='jon@pipitone.ca',
      url='http://github.com/pipitone/MAGeTbrain',
      download_url='http://github.com/pipitone/MAGeTbrain',
      description='Multiple automatically generated templates brain segmentation',
      long_description='...',

      packages = find_packages(),
      include_package_data = True,
      package_data = {
        '': ['*.txt', '*.rst'],
        'MAGeT': ['data/*.html', 'data/*.css'],
      },
      exclude_package_data = { '': ['README.txt'] },

      scripts = ['bin/morpho'],

      keywords='python neuroimaging segmentation image',
      license='CC-BY',
      classifiers=['Development Status :: 5 - Experimental/Alpha',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Topic :: Neuroimaging',
                  ],

      #setup_requires = ['python-stdeb', 'fakeroot', 'python-all'],
      install_requires = ['setuptools'],
     )

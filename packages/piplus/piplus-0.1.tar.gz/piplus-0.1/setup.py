# -*- coding: UTF-8 -*-
'''
Created on 2020-01-28

@author: daizhaolin
'''

from setuptools import setup, find_packages

setup(
    name='piplus',
    version='0.1',
    url='https://github.com/daizhaolin/piplus',
    license='BSD',
    author='daizhaolin',
    author_email='',
    description='Python Package Installer Plus',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='',
    install_requires=['pip>=20.0'],
)

#!/usr/local/bin/python3

import os
from setuptools import setup, find_packages

VERSION='0.0.01'
PYTHON_REQUIRES='3.7'

packagedata=dict()

packagedata['include_package_data']=True
packagedata['name']="botocredspath"
packagedata['version']=VERSION
packagedata['author']="Health Union Data Team"
packagedata['author_email']='data@health-union.com'
packagedata['description']="enables you to directly set boto3 aws folder path."
packagedata['classifiers']=['Development Status :: 3 - Alpha', "License :: OSI Approved :: MIT License", "Operating System :: OS Independent"]
packagedata['python_requires']=f'>={PYTHON_REQUIRES}'
packagedata['install_requires']=list()
packagedata['packages']=find_packages(exclude=['tests',])
packagedata['install_requires']=list()

with open('./README.rst','r') as readme:
    packagedata['long_description']=readme.read()


setup(**packagedata)

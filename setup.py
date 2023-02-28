#!/usr/bin/python3
"""
Description: setup up the A-ops utils module.
"""
import os
from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib


MAP_XML = os.path.join(get_python_lib(), "vulcanus", "restful", "resp")
setup(
    name='aops-vulcanus',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'concurrent-log-handler',
        'xmltodict',
        'PyYAML',
        'marshmallow>=3.13.0',
        'xlrd',
        'requests',
        'prettytable',
        'pygments',
        'SQLAlchemy',
        'elasticsearch>=7',
        'prometheus_api_client',
        'urllib3',
        'Werkzeug',
        'Flask_RESTful',
        'Flask'
    ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/system.ini']),
        (MAP_XML, ["vulcanus/restful/resp/map.xml"])
    ],
    scripts=['aops-vulcanus'],
    zip_safe=False
)

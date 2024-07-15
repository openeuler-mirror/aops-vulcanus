#!/usr/bin/python3
"""
Description: setup up the A-ops utils module.
"""
import os
from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib


MAP_XML = os.path.join(get_python_lib(), "vulcanus", "restful", "resp")
setup(
    name="aops-vulcanus",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "concurrent-log-handler",
        "xmltodict",
        "PyYAML",
        "marshmallow>=3.13.0",
        "xlrd",
        "requests",
        "SQLAlchemy",
        "elasticsearch>=7,<8",
        "Flask_RESTful",
        "Flask",
        "Flask-APScheduler",
        "apscheduler",
        "retrying",
        "kazoo",
    ],
    data_files=[
        ("/etc/aops", ["conf/aops-config.yml"]),
        (MAP_XML, ["vulcanus/restful/resp/map.xml"]),
    ],
    zip_safe=False,
)

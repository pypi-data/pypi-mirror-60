# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:12:08 2020

@author: sharma._.g
"""
from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis-101703557",
    version="1.1",
    description="A Python package to rank ML models/choices using topsis technique",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/souravsharma6633/topsis-101703557",
    author="Sourav Sharma",
    author_email="souravsharma6633@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_101703557"],
    include_package_data=True,
    install_requires=["pandas"],
    entry_points={
        "console_scripts": [
            "topsis-101703557=topsis_101703557.__init__:main",
        ]
    },
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 12:14:52 2020

@author: sihanzhou
"""


from setuptools import setup,find_packages


setup(
    name='zimpute', 
    version='1.7', 
    keywords=['zimpute'],
    description='A low rank complement method based on scRNA-seq data',
    long_description='For the data matrix of scRNA-seq, each cell is treated as a sample, and each row (column) indicates the expression of different genes in this cell is affected by noise.In summary, we have developed a low rank constraint matrix completion method based on truncated kernel norm.',
    license='MIT', 
    # Agreement to follow
    install_requires=[
            "numpy>=1.17.4",
            "mpmath>=1.1.0",
            "scipy>=1.3.2"
            ], 
    # Third-party libraries used in the project
     author='zhousihan0126',
    author_email='zhousihan0126@gmail.com',
    packages=find_packages(), # 项目内所有自己编写的库
    platforms='any',
    url='https://github.com/zhousihan0126' ,
    include_package_data = True,
    entry_points={
        'console_scripts':[
            'str=zimpute.zimpute:main' 
        ]
    },
)


# 以上字段不需要都包含
# coding: utf-8
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

"""
打包的用的setup必须引入，
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
 

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 

 
# 版本号，自己随便写
VERSION = "1.0.0"

LICENSE = "MIT"

readme = "https://github.com/puntsokCN/tibetan_anlysis/blob/master/README.md"
 
setup(
    name='tibetan-analysis',
    version=VERSION,
    description=(
        '藏文字词句分析模块'
    ),
    long_description=readme,
    author='puntsok',
    author_email='1195209380@qq.com',
    maintainer='puntsok',
    maintainer_email='1195209380@qq.com',
    license=LICENSE,
    # packages=find_packages(),
    platforms=["all"],
    url='https://github.com/puntsokCN/tibetan_anlysis',
      
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)


# URL 你这个包的项目地址，如果有，给一个吧，没有你直接填写在PyPI你这个包的地址也是可以的
# INSTALL_REQUIRES 模块所依赖的python模块
# 以上字段不需要都包含
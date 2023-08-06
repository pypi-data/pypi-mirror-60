# encoding: utf-8
"""
基于redis的AES加解密工具包

2/4/2020   Bruce  0.8.2   初始版本

"""
import sys
from setuptools import setup, find_packages
import cad

SHORT = 'a util for aes'

if sys.platform == 'win32':
    setup(
        name='cad',
        version=cad.__version__,
        packages=find_packages(),
        install_requires=[
            'requests', 'redis', 'dynaconf', 'pycryptodome'
        ],
        url='',
        author=cad.__author__,
        author_email=cad.__email__,
        classifiers=[
            'Programming Language :: Python :: 3',
        ],
        include_package_data=True,
        package_data={'': ['*.py', '*.pyc']},
        zip_safe=False,
        platforms='any',

        description=SHORT,
        long_description=__doc__,
    )
else:
    setup(
        name='cad',
        version=cad.__version__,
        packages=find_packages(),
        install_requires=[
            'requests', 'redis', 'dynaconf', 'pycrypto'
        ],
        url='',
        author=cad.__author__,
        author_email=cad.__email__,
        classifiers=[
            'Programming Language :: Python :: 3',
        ],
        include_package_data=True,
        package_data={'': ['*.py', '*.pyc']},
        zip_safe=False,
        platforms='any',

        description=SHORT,
        long_description=__doc__,
    )

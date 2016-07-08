from setuptools import setup, find_packages
from os import path
import sys


here = path.abspath(path.dirname(__file__))

extra_require = {
        'dev': ['sphinx'],
        'test': ['nose', 'coverage', 'wsgi_intercept'],
    }

if sys.version_info.major == 2:
    extra_require['test'].append('typing')

setup(
    name='leancloud-sdk',
    version='1.6.1',
    description='LeanCloud Python SDK',

    url='https://leancloud.cn/',

    author='asaka',
    author_email='lan@leancloud.rocks',

    license='LGPL',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='Leancloud SDK',

    packages=find_packages(exclude=['docs', 'tests*']),

    test_suite='nose.collector',

    install_requires=[
        'arrow',
        'iso8601',
        'qiniu',
        'requests',
        'werkzeug',
    ],

    extras_require=extra_require
)

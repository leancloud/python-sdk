from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='leancloud-sdk',
    version='1.0.0',
    description='Leancloud Python SDK',

    url='https://leancloud.cn/',

    author='asaka',
    author_email='lan@leancloud.rocks',

    license='BSD-2-Clause',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='Leancloud SDK',

    packages=find_packages(exclude=['docs', 'tests*']),

    test_suite='nose.collector',

    install_requires=[
        'requests',
    ],
)

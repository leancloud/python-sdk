from setuptools import setup, find_packages
from os import path
import sys


here = path.abspath(path.dirname(__file__))

install_requires = [
    "arrow>=0.17.0,<1.0.0; python_version < '3.6'",
    "arrow>=1.0.0,<2.0.0; python_version >= '3.6'",
    'iso8601>=0.1.14',
    'six>=1.11.0',
    'qiniu==7.3.1',
    "requests<=2.31.0; python_version >= '3.7'",
    "urllib3<=1.26.18; python_version >= '3.7'",
    'requests-toolbelt>=1.0.0',
    'Werkzeug>=0.16.0,<2.0.0',
    'secure-cookie>=0.1.0,<1.0.0',
    'gevent>=22.10.2,<23.0.0',
    "typing; python_version < '3.5'",
    'markupsafe<=2.0.1',
]

setup(
    name='leancloud',
    version='3.0.2',
    description='LeanCloud Python SDK',
    url='https://leancloud.cn/',
    author='asaka',
    author_email='lan@leancloud.rocks',
    license='LGPL',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='Leancloud SDK',
    packages=find_packages(exclude=['docs', 'tests*']),
    test_suite='nose.collector',
    install_requires=install_requires,
    extras_require={
        'dev': ['sphinx', 'sphinx_rtd_theme'],
        'test': ['nose', 'wsgi_intercept', 'flask'],
    }
)

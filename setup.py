from setuptools import setup, find_packages
from os import path
import sys


here = path.abspath(path.dirname(__file__))

install_requires = [
    'iso8601>=0.1.14',
    'six>=1.11.0',
    'qiniu>=7.1.4,<7.2.4',
    'requests>=2.25.1',
    'Werkzeug>=0.16.0,<=2.0.0',
    'secure-cookie>=0.1.0,<1.0.0',
    'gevent>=21.1.0,<22.0.0'
]

if sys.version_info < (3, 6, 0):
    install_requires.append('arrow>=0.17.0,<1.0.0')
else:
    install_requires.append('arrow>=1.0.0,<2.0.0')

if sys.version_info < (3, 5, 0):
    install_requires.append('typing')

if sys.version_info < (2, 7, 9):
    install_requires.append('pyOpenSSL')
    install_requires.append('idna')

setup(
    name='leancloud',
    version='2.9.1',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
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

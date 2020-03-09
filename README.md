# Python-SDK

[![Build Status](https://travis-ci.org/leancloud/python-sdk.svg?branch=master)](https://travis-ci.org/leancloud/python-sdk) [![Python3 Support](https://caniusepython3.com/project/leancloud-sdk.svg)](https://caniusepython3.com/project/leancloud-sdk) [![Codecov](https://img.shields.io/codecov/c/github/leancloud/python-sdk.svg)](https://codecov.io/gh/leancloud/python-sdk)

LeanCloud Python SDK

## Install

```bash
pip install leancloud
```

or

```
easy_install leancloud
```

Maybe you need the `sudo` prefix depends on your OS environment.

## Generate API document

```bash
cd docs
make html
```

## Run Tests

Configure the following environment variables:

- `APP_ID`
- `APP_KEY`
- `MASTER_KEY`
- `USE_REGION`

Install dependencies:

```sh
pip install -e .'[test]'
```

Run tests:

```sh
nosetests
```

## Release a New Version

1. Edit `changelog` and `setup.py` (`version`).
2. Commit them and add a new tag. Then publish a new release at GitHub.
3. Publish the package at PyPI with following commands:

```sh
python3 -m pip install --user --upgrade setuptools wheel
rm -rf dist
python3 setup.py sdist bdist_wheel
python3 -m pip install --user --upgrade twine
twine upload dist/*
```

## License

License: [GNU LGPL](https://www.gnu.org/licenses/lgpl.html).

Author: asaka (lan@leancloud.rocks)

# Python-SDK

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/leancloud/python-sdk/Python%20package/master)
[![Codecov](https://img.shields.io/codecov/c/github/leancloud/python-sdk.svg)](https://codecov.io/gh/leancloud/python-sdk)

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

## Supported Python Versions

Python 2.7.18 and Python 3.6+.

## Generate API document

Install dependencies:

```sh
pip install Sphinx sphinx_rtd_theme
```

```sh
cd apidoc
make html
```

## Run Tests

Configure the following environment variables:

- `APP_ID`
- `APP_KEY`
- `MASTER_KEY`
- `USE_REGION`

Make sure the following options are configured on the LeanCloud console:

- Data Storage > Settings > Include ACL with objects being queried: **checked**
- Push Notification > Push notification settings > Prevent clients from sending push notifications: **unchecked**
- Settings > Security > Service switches > Push notifications: **enabled**
- Settings > Security > Service switches > SMS: **disabled**

And there is a cloud function naming `add` which returns `3` for `add(a=1, b=2)` deployed on the LeanEngine production environment of the application.
For example:

```js
AV.Cloud.define('add', async function (request) {
    return request.params["a"] + request.params["b"]
})
```

Install dependencies:

```sh
pip install -e .'[test]'
```

Run tests:

```sh
python -m nose
```

Run a single test without swallowing print:

```sh
python -m nose -v --nocapture tests/test_engine.py:test_lean_engine_error
```

## Linter and Formatter

Currently, flake8 (linter) and black (formatter) are used.
But we are still exploring.

## Release a New Version

0. Edit `changelog` and `setup.py` (`version`).
1. Generate API doc.
2. Commit the changes above and send a pull request.
3. The maintainer will review and merge the pull request, then create a new release at GitHub web UI.
4. A new version of the package will be published to PyPI automatically (via GitHub Actions).

## License

License: [GNU LGPL](https://www.gnu.org/licenses/lgpl.html).

Author: asaka (lan@leancloud.rocks)

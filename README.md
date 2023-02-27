# py-multiauth ![PyPI](https://img.shields.io/pypi/v/py-multiauth) [![CI](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml) [![CD](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml) [![codecov](https://codecov.io/gh/Escape-Technologies/py-multiauth/branch/main/graph/badge.svg?token=NL148MNKAE)](https://codecov.io/gh/Escape-Technologies/py-multiauth)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-multiauth)
![PyPI - Downloads](https://img.shields.io/pypi/dm/py-multiauth)

## Installation

```bash
pip install py-multiauth
```

## Supported methods

|Name     |Authenticate|Refresh|Extra    |
|---------|:----------:|:-----:|---------|
|`API_KEY`|✓           |       |         |
|`AWS`    |✓           |✓      |Signature|
|`BASIC`  |✓           |       |         |
|`REST`   |✓           |✓      |         |
|`DIGEST` |✓           |       |         |
|`GRAPHQL`|✓           |       |         |
|`HAWK`   |✓           |       |         |
|`MANUAL` |✓           |       |         |
|`OAUTH`  |✓           |✓      |         |

## Usage

### Loading a configuration file

Currently, we support 4 way of loading a configuration file.

```python

# Using constructor argument
MultiAuth(authrc_file='path.json')

# Using environment variable
os.environ['AUTHRC'] = 'path.json'

# Using autodection
os.paths.exists('.authrc')?

# Using autodection from user home directory
os.path.exists(os.path.expanduser('~/.multiauth/.authrc'))?
```

### Managing authentication flow

**MultiAuth supports context singleton.
From that, you can instanciate MultiAuth and re-use the same class in another package as far it is sharing the same context.**

```python
auth = MultiAuth(auths=.., users=.., authrc=.., logger=..)

# Sending the requests to get the correct headers
auth.authenticate_users()

# Getting the header before sending a HTTP request
auth_headers = auth.reauthenticate(username=.., additional_headers=.., public=..)
r = requests.get('https://example.com', headers=auth_headers[0])
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License ![PyPI - License](https://img.shields.io/pypi/l/py-multiauth)

[MIT](https://choosealicense.com/licenses/mit/)

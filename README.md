# py-multiauth ![PyPI](https://img.shields.io/pypi/v/py-multiauth) [![CI](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml) [![CD](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml) [![codecov](https://codecov.io/gh/Escape-Technologies/py-multiauth/branch/main/graph/badge.svg?token=NL148MNKAE)](https://codecov.io/gh/Escape-Technologies/py-multiauth)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-multiauth)
![PyPI - Downloads](https://img.shields.io/pypi/dm/py-multiauth)

## Installation

```bash
pip install py-multiauth
```

```python
from multiauth import ...
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

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License ![PyPI - License](https://img.shields.io/pypi/l/py-multiauth)

[MIT](https://choosealicense.com/licenses/mit/)

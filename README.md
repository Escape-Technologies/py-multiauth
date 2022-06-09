# py-multiauth ![PyPI](https://img.shields.io/pypi/v/py-multiauth) [![codecov](https://codecov.io/gh/Escape-Technologies/py-multiauth/branch/main/graph/badge.svg?token=NL148MNKAE)](https://codecov.io/gh/Escape-Technologies/py-multiauth)

[![CI](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/ci.yaml) [![CD](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml/badge.svg)](https://github.com/Escape-Technologies/py-multiauth/actions/workflows/cd.yaml)

![PyPI - License](https://img.shields.io/pypi/l/py-multiauth) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-multiauth)
![PyPI - Downloads](https://img.shields.io/pypi/dm/py-multiauth)

[View it on pypi!](https://pypi.org/project/py-multiauth/)

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
|`REST`   |✓           |       |         |
|`DIGEST` |✓           |       |         |
|`GRAPHQL`|✓           |       |         |
|`HAWK`   |✓           |       |         |
|`MANUAL` |✓           |       |         |
|`OAUTH`  |✓           |✓      |         |

"""Utility functions independent of the library."""

import logging
import os
from typing import Dict, List, Mapping, Optional, TypeVar, Union

from pydash import py_

Default = TypeVar('Default')
Value = TypeVar('Value')


def install_logger(logger: logging.Logger) -> None:
    """Install logger."""

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s'))

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if os.getenv('DEBUG') else logging.INFO)

    # Ignore asyncio debug logs
    logging.getLogger('asyncio').setLevel(logging.ERROR)


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup logger."""

    name = name or 'multiauth'
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        install_logger(logger)

    return logger


def dict_find_path(
    nested_dict: Mapping,
    key: str,
    prepath: str = '',
    index: Optional[int] = None,
) -> str:
    """Recursively find the path of a certain key in a Dict."""

    for k, v in nested_dict.items():
        if prepath == '':
            path = k
        elif index is not None:
            path = f'{prepath}.{index}.{k}'
        else:
            path = f'{prepath}.{k}'

        if k == key:  # found value
            return path

        if isinstance(v, Dict):
            p = dict_find_path(v, key, path, None)  # recursive call
            if p != '':
                return p

        if isinstance(v, List):
            for i, elem in enumerate(v):
                if isinstance(elem, Dict):
                    p = dict_find_path(elem, key, path, i)
                    if p != '':
                        return p

    return ''


def dict_nested_get(
    dictionary: Mapping[str, Value],
    key: str,
    default_return: Default = None,
) -> Union[Default, Value]:
    """Search for a certain key inside a dict and returns its value (no matter the depth)"""
    return py_.get(dictionary, dict_find_path(dictionary, key, ''), default_return)

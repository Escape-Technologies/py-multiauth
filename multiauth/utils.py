"""Utility functions independent of the library."""

from enum import Enum
from typing import Any, Mapping, Type, TypeVar
from urllib.parse import urlparse

from pydash import py_

Default = TypeVar('Default')
Value = TypeVar('Value')


def is_url(url: str) -> bool:
    """This function checks if the url is valid."""

    if not isinstance(url, str):
        raise TypeError(f'Expected a string, got {type(url)}')

    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


def dict_deep_merge(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merge two dictionaries, including nested dictionaries.
    """
    result = dict1.copy()  # Start with dict1's keys and values
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # If the key is in both dictionaries and both values are dicts, merge them
            result[key] = dict_deep_merge(result[key], value)
        else:
            # Otherwise, use dict2's value, overriding dict1's value if key is present
            result[key] = value
    return result


def merge_headers(headers1: dict[str, str], headers2: dict[str, str]) -> dict[str, str]:
    """This function merges two headers together."""

    headers1 = {k.lower(): v for k, v in headers1.items()}
    headers2 = {k.lower(): v for k, v in headers2.items()}

    headers: dict[str, str] = headers1.copy()  # Start with headers1

    for name, value in headers2.items():
        # Resolving duplicate keys
        if name in headers:
            headers[name] += f', {value}'
        else:
            headers[name] = value

    return headers


def deep_merge_data(base_data: Any, user_data: Any) -> Any:
    # If the base data is a dict, and the user data is a dict, then we merge them
    if isinstance(base_data, dict) and isinstance(user_data, dict):
        return dict_deep_merge(base_data, user_data)

    # If the base data is a list, and the user data is a list, then we merge them
    if isinstance(base_data, list) and isinstance(user_data, list):
        return base_data + user_data

    if user_data is None:
        return base_data

    # In any other case, user_data prevails over base_data
    return user_data


def in_enum(method: str, myenum: Type[Enum]) -> bool:
    """This function checks if the http method is valid."""

    try:
        myenum(method.upper())
        return True
    except ValueError:
        return False


def dict_find_path(
    nested_dict: Mapping,
    key: str,
    prepath: str = '',
    index: int | None = None,
) -> str:
    """Recursively find the path of a certain key in a dict."""

    for k, v in nested_dict.items():
        if prepath == '':
            path = k
        elif index is not None:
            path = f'{prepath}.{index}.{k}'
        else:
            path = f'{prepath}.{k}'

        if k == key:  # found value
            return path

        if isinstance(v, dict):
            p = dict_find_path(v, key, path, None)  # recursive call
            if p != '':
                return p

        if isinstance(v, list):
            for i, elem in enumerate(v):
                if isinstance(elem, dict):
                    p = dict_find_path(elem, key, path, i)
                    if p != '':
                        return p

    return ''


def dict_nested_get(
    dictionary: Mapping[str, Value],
    key: str,
    default_return: Default | None = None,
) -> Default | Value:
    """Search for a certain key inside a dict and returns its value (no matter the depth)"""
    return py_.get(dictionary, dict_find_path(dictionary, key, ''), default_return)

import pytest

from multiauth.utils import dict_deep_merge, is_url, merge_headers  # Replace with the actual module name


def test_merge_different_keys() -> None:
    headers1 = {'Content-Type': 'application/json'}
    headers2 = {'Authorization': 'Bearer token'}
    result = merge_headers(headers1, headers2)
    expected = {'content-type': 'application/json', 'authorization': 'Bearer token'}
    assert result == expected


def test_merge_with_overlap() -> None:
    headers1 = {'Content-Type': 'application/json'}
    headers2 = {'content-type': 'text/html'}
    result = merge_headers(headers1, headers2)
    expected = {'content-type': 'application/json, text/html'}  # Expecting failure here
    assert result == expected


def test_merge_empty_headers() -> None:
    headers1: dict[str, str] = {}
    headers2: dict[str, str] = {}
    result = merge_headers(headers1, headers2)
    assert result == {}


def test_merge_with_one_empty_header() -> None:
    headers1 = {'Accept': 'application/json'}
    headers2: dict[str, str] = {}
    result = merge_headers(headers1, headers2)
    assert result == {'accept': 'application/json'}


def test_merge_case_insensitivity() -> None:
    headers1 = {'content-TYPE': 'application/json'}
    headers2 = {'Content-type': 'text/html'}
    result = merge_headers(headers1, headers2)
    expected = {'content-type': 'application/json, text/html'}  # Expecting failure here
    assert result == expected


def test_merge_flat_dictionaries() -> None:
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'c': 3, 'd': 4}
    expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    assert dict_deep_merge(dict1, dict2) == expected


def test_merge_nested_dictionaries() -> None:
    dict1 = {'a': {'x': 1}, 'b': 2}
    dict2 = {'a': {'y': 2}, 'c': 3}
    expected = {'a': {'x': 1, 'y': 2}, 'b': 2, 'c': 3}
    assert dict_deep_merge(dict1, dict2) == expected


def test_merge_with_overlapping_keys() -> None:
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    expected = {'a': 1, 'b': 3, 'c': 4}
    assert dict_deep_merge(dict1, dict2) == expected


def test_merge_with_mixed_types() -> None:
    dict1 = {'a': 1, 'b': {'x': 1}}
    dict2 = {'b': 'new value', 'c': 3}
    expected = {'a': 1, 'b': 'new value', 'c': 3}
    assert dict_deep_merge(dict1, dict2) == expected


def test_merge_with_empty_dict() -> None:
    dict1: dict[str, str] = {}
    dict2 = {'a': 1}
    assert dict_deep_merge(dict1, dict2) == dict2
    assert dict_deep_merge(dict2, dict1) == dict2


# Test suite


def test_valid_urls() -> None:
    assert is_url('http://example.com') is True
    assert is_url('https://www.example.com') is True
    assert is_url('ftp://example.com/file.txt') is True


def test_invalid_urls() -> None:
    assert is_url('www.example.com') is False
    assert is_url('example') is False
    assert is_url('http//example') is False


def test_empty_string() -> None:
    assert is_url('') is False


def test_non_string_input() -> None:
    with pytest.raises(TypeError):
        is_url(None)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        is_url(123)  # type: ignore[arg-type]

from typing import Any

from deepmerge import Merger  # type: ignore  # noqa: PGH003

from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPQueryParameter


def merge_headers(headers_a: list[HTTPHeader], headers_b: list[HTTPHeader]) -> list[HTTPHeader]:
    """Merge two headers lists."""

    headers = {h.name: h.values for h in headers_a}
    headers.update({h.name: h.values for h in headers_b})

    return [HTTPHeader(name=name, values=values) for name, values in headers.items()]


def merge_cookies(cookies_a: list[HTTPCookie], cookies_b: list[HTTPCookie]) -> list[HTTPCookie]:
    """Merge two cookies lists."""

    cookies = {c.name: c.values for c in cookies_a}
    cookies.update({c.name: c.values for c in cookies_b})

    return [HTTPCookie(name=name, values=values) for name, values in cookies.items()]


def merge_query_parameters(qp_a: list[HTTPQueryParameter], qp_b: list[HTTPQueryParameter]) -> list[HTTPQueryParameter]:
    """Merge two query parameters lists."""

    qp = {c.name: c.values for c in qp_a}
    qp.update({c.name: c.values for c in qp_b})

    return [HTTPQueryParameter(name=name, values=values) for name, values in qp.items()]


body_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [
        (list, ['append']),
        (dict, ['merge']),
        (set, ['union']),
    ],
    # next, choose the fallback strategies,
    # applied to all other types:
    ['override'],
    # finally, choose the strategies in
    # the case where the types conflict:
    ['override'],
)


def merge_bodies(body_a: Any, body_b: Any) -> Any:
    if body_a is None:
        return body_b

    if body_b is None:
        return body_a

    return body_merger.merge(body_a, body_b)

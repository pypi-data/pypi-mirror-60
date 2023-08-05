from typing import Generator, KeysView, Optional, Sequence, Union, ValuesView


def _normalize_header_name(name: str) -> str:
    """
    According to rfc https://www.ietf.org/rfc/rfc2616.txt header names are case insensitive,
    thus they can be normalized to ease usage of Headers class.
    :param name:
    :return:
    """
    name = name.lower()
    if name.startswith("http_"):
        name = name[5:]

    return name.replace("_", "-")


def _normalize_headers(headers: dict) -> dict:
    normalized = {}
    for name, value in headers.items():
        normalized[_normalize_header_name(name)] = value

    return normalized


class Headers:
    """
    Dict-like object containing http headers. Header names are case-insensitive, and
    their values are internally stored as sequences to conform RFC-2616 standard.

    .. _RFC-2616 Section 4.2: https://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2
    """

    def __init__(self, headers: Optional[dict] = None):

        headers = {} if headers is None else headers
        self._headers = _normalize_headers(headers)

    def set(self, name: str, value: str) -> None:
        """
        Appends new value to the header, if header does not exists it will get created.
        """
        normalized_name = _normalize_header_name(name)
        if normalized_name not in self._headers:
            self._headers[normalized_name] = []

        self._headers[normalized_name].append(value)

    def get(self, name: str, default: str = "") -> Union[str, Sequence[str]]:
        if name in self:
            return self.__getitem__(name)
        return default

    def __setitem__(self, name: str, value: Sequence[str]) -> None:
        """
        Sets value for header. Value must be valid sequence of strings.
        """
        self._headers[_normalize_header_name(name)] = value

    def __getitem__(self, name: str) -> Union[str, Sequence[str]]:
        """
        Returns string if header is unique otherwise sequence of strings is returned.
        """
        value = self._headers[_normalize_header_name(name)]
        if len(value) == 1:
            return value[0]

        return value

    def __contains__(self, name: str) -> bool:
        return _normalize_header_name(name) in self._headers

    def items(self) -> Generator:
        for key, values in self._headers.items():
            if len(values) == 1:
                yield key, values[0]
            for value in values:
                yield key, value

    def values(self) -> ValuesView[Union[str, Sequence[str]]]:
        return self._headers.values()

    def keys(self) -> KeysView[str]:
        return self._headers.keys()


__all__ = ["Headers"]

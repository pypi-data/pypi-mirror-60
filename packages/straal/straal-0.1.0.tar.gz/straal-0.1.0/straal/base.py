from abc import ABC
from string import Formatter
from typing import List, Optional, Type, TypeVar
from urllib.parse import urljoin

import requests

from straal.exceptions import StraalException

_API_KEY = None
_BASE_URL = "https://api.straal.com/"
T = TypeVar("T", bound="ApiObject")


def get_api_key() -> Optional[str]:
    return _API_KEY


def get_base_url() -> Optional[str]:
    return _BASE_URL


def init(api_key: str, base_url: Optional[str] = None):
    global _API_KEY
    _API_KEY = api_key

    if base_url:
        global _BASE_URL
        _BASE_URL = base_url


def _get_required_format_vars(url: str) -> List[str]:
    return [ref for _, ref, _, _ in Formatter().parse(url) if ref is not None]


def _build_request_data(uri: str, **kwargs):
    req_url_tpl = urljoin(_BASE_URL, uri)
    required_format_vars = _get_required_format_vars(req_url_tpl)
    # TODO: Provide better exc with proper ctx instead of KeyError
    format_kwargs = {k: kwargs[k] for k in required_format_vars}
    for kwarg in required_format_vars:
        kwargs.pop(kwarg)

    return req_url_tpl.format(**format_kwargs), kwargs


def _handle_create_errors(response: requests.Response):
    # naive assumption that we will always have JSON in res
    error_json = response.json()
    if "errors" in error_json:
        # Right now only raise mapped exc from first error
        # TODO: elegant way to propagate all received errors
        err_code = error_json["errors"][0]["code"]
        raise StraalException._REGISTRY[err_code]


class ApiObject(ABC):
    RESOURCE_CREATE_URI: str
    RESOURCE_DETAIL_URI: str
    RESOURCE_LIST_URI: str

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        req_url, json_data = _build_request_data(cls.RESOURCE_CREATE_URI, **kwargs)
        res = requests.post(req_url, json=json_data, auth=("", _API_KEY))

        if res.status_code != 200:
            _handle_create_errors(res)

        return cls(**res.json())

    @classmethod
    def get(cls: Type[T], **kwargs) -> T:
        req_url, _ = _build_request_data(cls.RESOURCE_DETAIL_URI, **kwargs)
        res = requests.get(req_url, auth=("", _API_KEY))
        return cls(**res.json())

    @classmethod
    def list(cls: Type[T], **kwargs) -> List[T]:
        req_url, _ = _build_request_data(cls.RESOURCE_LIST_URI, **kwargs)
        res = requests.get(req_url, auth=("", _API_KEY))
        return [cls(**entry) for entry in res.json()["data"]]

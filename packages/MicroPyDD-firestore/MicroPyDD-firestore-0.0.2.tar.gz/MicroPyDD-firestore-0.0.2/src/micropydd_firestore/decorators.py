from functools import wraps
from typing import Type

from colorlog import logging

from micropydd.utils import dict_to_object

LOG = logging.getLogger(__name__)


def fs_document_to_type(t: Type, is_list: bool = False):
    def inner(func):
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs).to_dict()
            if is_list:
                return list(map(lambda x: dict_to_object(x, t), result))
            return dict_to_object(result, t)
        return wrap
    return inner

from functools import wraps
from typing import Type

from colorlog import logging

from micropydd.utils import dict_to_object

LOG = logging.getLogger(__name__)


def fs_document_to_type(type: Type, is_list: bool = False):
    def inner(func):
        def wrap(*args, **kwargs):
            return dict_to_object(func(*args, **kwargs).to_dict(), type)
        return wrap
    return inner

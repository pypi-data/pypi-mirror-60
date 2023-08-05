from typing import Type

from colorlog import logging

from micropydd_firestore.models import Entity
from micropydd_firestore.utils import fs_document_to_object_type, fs_query_to_object_type

LOG = logging.getLogger(__name__)


def fs_to_object_type(t: Type[Entity], is_list: bool = False):
    def inner(func):
        def wrap(*args, **kwargs):
            result = func(*args, **kwargs)
            if is_list:
                return fs_query_to_object_type(result, t)
            return fs_document_to_object_type(result, t)
        return wrap
    return inner

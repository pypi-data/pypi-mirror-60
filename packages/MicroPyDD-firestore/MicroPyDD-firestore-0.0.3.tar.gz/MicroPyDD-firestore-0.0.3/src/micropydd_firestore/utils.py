from typing import List, Iterable, TypeVar

import micropydd

from micropydd.utils import dict_to_object

from micropydd_firestore.config import FirestoreConfig

from google.cloud import firestore
from google.cloud.firestore_v1 import CollectionReference, DocumentSnapshot


T = TypeVar("T")


def root_collection(collection_path) -> CollectionReference:
    """
    It return the root collection
    :param collection_path:
    :return:
    """
    main_collection = micropydd.app_context[FirestoreConfig].ROOT_COLLECTION
    return micropydd.app_context[firestore.Client].collection(f'{main_collection}/{collection_path}')


def fs_document_to_object_type(d: DocumentSnapshot, t: T) -> T:
    """
    Transform a fs document to object type
    :param d:
    :param t:
    :return:
    """
    return dict_to_object(d.to_dict(), t)


def fs_query_to_object_type(i: Iterable[DocumentSnapshot], t: T) -> List[T]:
    """
    Transform query to List of entities
    :param i:
    :param t:
    :return:
    """
    return [dict_to_object(x.to_dict(), t) for x in i]

import micropydd
from google.cloud import firestore

from micropydd_firestore.config import FirestoreConfig


def root_collection(collection_path):
    """
    It return the root collection
    :param collection_path:
    :return:
    """
    main_collection = micropydd.app_context[FirestoreConfig].ROOT_COLLECTION
    return micropydd.app_context[firestore.Client].collection(f'{main_collection}/{collection_path}')

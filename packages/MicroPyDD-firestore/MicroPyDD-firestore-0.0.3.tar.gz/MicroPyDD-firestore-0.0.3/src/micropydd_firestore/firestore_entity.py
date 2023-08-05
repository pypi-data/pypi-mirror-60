from typing import Tuple, Any, List, Generic, TypeVar

import google
from google.cloud import firestore
from micropydd.utils import object_to_dict, get_timestamp

from micropydd_firestore.exceptions import EntityNotFound
from micropydd_firestore.models import PaginatedResult
from micropydd_firestore.utils import root_collection, fs_document_to_object_type, fs_query_to_object_type

T = TypeVar("T")


class FirestoreEntityService(Generic[T]):

    def __init__(self, collection_name: str, model_class: T, db: firestore.Client) -> None:
        super().__init__()
        self._db = db
        self._model_class = model_class
        self._collection_ref = root_collection(collection_name)

    def create(self, id: str, model: T) -> None:
        """
        Create a new object into the system
        :param id:
        :param model:
        :return:
        """
        self._collection_ref.document(id).create({
            **object_to_dict(model),
            'created_at': get_timestamp()
        })

    def find_by_id(self, id: str) -> T:
        """
        Find element by id
        :param id:
        :return:
        """
        try:
            result = self._collection_ref.document(id).get()
        except google.cloud.exceptions.NotFound:
            raise EntityNotFound(id)
        return fs_document_to_object_type(result, self._model_class)

    def find(self,
             order_by: str = None,
             where: List[Tuple[str, str, Any]] = None,
             cursor: str = None,
             limit: int = 100) -> PaginatedResult[T]:
        """
        Search by query
        :param order_by:
        :param where:
        :param cursor:
        :param limit:
        :return:
        """
        result = self._collection_ref
        if where:
            for where_clause in where:
                result = result.where(where_clause[0], where_clause[1], where_clause[2])
        if order_by:
            result = result.order_by(order_by)
        if cursor:
            result = result.start_at(self._collection_ref.document(cursor).get())
        if limit:
            result = result.limit(limit)

        result = [x for x in result.stream()]
        return PaginatedResult(
            results=fs_query_to_object_type(result, self._model_class),
            next=result[-1].id
        )

    def find_all(self,
                 order_by: str = None,
                 cursor: str = None,
                 limit: int = 100) -> PaginatedResult[T]:
        """
        Search all
        :param order_by:
        :param cursor:
        :param limit:
        :return:
        """
        return self.find(order_by=order_by, cursor=cursor, limit=limit)

    def update(self, id: str, model: T):
        """
        Update an existing entity
        :param id:
        :param model:
        :return:
        """
        self._collection_ref.document(id).update({
            **object_to_dict(model),
            'created_at': get_timestamp()
        })

    def delete_by_id(self, id: str):
        """
        Delete element by id
        :param id:
        :return:
        """
        self._collection_ref.document(id).delete()

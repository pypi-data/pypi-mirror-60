from typing import Dict

from micropydd.config import Config
from micropydd.module import MicroPyDDModule
from google.cloud import firestore

from micropydd_firestore.config import FirestoreConfig


class MicroPyDDTenantFirestoreModule(MicroPyDDModule):

    def context(self, existing_context: Dict) -> Dict:
        super().context(existing_context)
        result = {
            FirestoreConfig: existing_context[Config] if isinstance(existing_context[Config], FirestoreConfig) else None,
            firestore.Client: firestore.Client(),
        }

        return result

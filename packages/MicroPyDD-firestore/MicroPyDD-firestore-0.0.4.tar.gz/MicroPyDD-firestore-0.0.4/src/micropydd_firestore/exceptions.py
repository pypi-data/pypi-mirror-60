from micropydd.exceptions import MicroPyDDException


class EntityNotFound(MicroPyDDException):
    def __init__(self, tenant_id) -> None:
        super().__init__(f'Tenand {tenant_id} not found')

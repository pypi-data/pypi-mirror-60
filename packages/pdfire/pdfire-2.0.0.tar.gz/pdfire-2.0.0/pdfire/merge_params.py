from typing import List
from pdfire import ConversionParams

class MergeParams:
    def __init__(
        self,
        documents: List[ConversionParams] = [],
        owner_password: str = None,
        user_password: str = None,
        cdn: bool = None,
        storage = None
    ):
        self.documents = documents
        self.owner_password = owner_password
        self.user_password = user_password
        self.cdn = cdn
        self.storage = storage

    def to_dict(self):
        values = {
            'documents': list(map(lambda d: d.to_dict(), self.documents)),
            'ownerPassword': self.owner_password,
            'userPassword': self.user_password,
            'cdn': self.cdn,
            'storage': self.storage,
        }

        return {k: v for k, v in values.items() if v is not None}

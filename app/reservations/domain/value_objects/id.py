from uuid import UUID


class ID(str):
    @classmethod
    def from_uuid(cls, uuid: UUID) -> "ID":
        return cls(str(uuid))

    def to_uuid(self) -> UUID:
        return UUID(self)

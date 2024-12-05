from uuid import UUID


class Id(str):
    @classmethod
    def from_uuid(cls, uuid: UUID) -> "Id":
        return cls(str(uuid))

    def to_uuid(self) -> UUID:
        return UUID(self)

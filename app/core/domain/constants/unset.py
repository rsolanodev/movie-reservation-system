from dataclasses import dataclass


@dataclass(frozen=True)
class UnsetType: ...


UNSET = UnsetType()

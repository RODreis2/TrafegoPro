from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class User:
    id: UUID
    name: str
    email: str
    password: str

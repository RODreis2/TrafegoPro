from uuid import UUID

import psycopg

from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User


class PostgresUserRepository(UserRepository):
    def __init__(self, connection_string: str):
        self.conn = psycopg.connect(connection_string)

    def save(self, user: User) -> None:
        raise NotImplementedError

    def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

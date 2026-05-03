from uuid import UUID

from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, user_id: UUID) -> User | None:
        return self.user_repository.get_by_id(user_id)

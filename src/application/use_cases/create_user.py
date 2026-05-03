from uuid import UUID

from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, user_id: UUID, name: str, email: str, password: str) -> User:
        user = User(id=user_id, name=name, email=email, password=password)
        self.user_repository.save(user)

        return user

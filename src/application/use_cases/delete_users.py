from uuid import UUID
from src.application.ports.user_repository import UserRepository


class DeleteUser:
    def __init__(self, user_repository:UserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, user_id:UUID) -> None:
        self.user_repository.delete_users(user_id) 
   

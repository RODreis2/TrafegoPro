from src.domain.entities.user import User 
from src.application.dto.request.user_request import UserRequest
from src.application.dto.response.user_response import UserResponse
import uuid

class UserMapper:

    def to_entity(self,user_request:UserRequest) -> User:
        return User(
                id=uuid.uuid4(),
                name=user_request.name,
                email=user_request.email,
                password=user_request.password 
                )
   
    def to_response(self, user:User) -> UserResponse:
        return UserResponse(
                id=user.id,
                name=user.name,
                email=user.email, 
                )

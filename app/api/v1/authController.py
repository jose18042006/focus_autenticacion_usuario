from litestar import Controller, post
from litestar.status_codes import HTTP_201_CREATED, HTTP_200_OK

from app.domain.structs import UserCredentials, TokenResponse
from app.services.user_service import register_new_user, authenticate_user
from app.repositories.user_repository import UserRepository

class AuthController(Controller):
    path = "/auth"

    @post("/register", status_code=HTTP_201_CREATED)
    async def register(self, data: UserCredentials, user_repo: UserRepository) -> dict:
        user = await register_new_user(data, user_repo)
        return {
            "message": "Usuario registrado exitosamente", 
            "email": user.email,
            "id": str(user.id)
        }

    @post("/login", status_code=HTTP_200_OK)
    async def login(self, data: UserCredentials, user_repo: UserRepository) -> TokenResponse:
        return await authenticate_user(data, user_repo)
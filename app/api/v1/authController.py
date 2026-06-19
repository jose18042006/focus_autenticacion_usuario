from litestar import Controller, post
from litestar.status_codes import HTTP_201_CREATED, HTTP_200_OK

from app.services.user_service import register_new_user, authenticate_user
from app.repositories.user_repository import UserRepository
from app.domain.structs import UserCredentials, TokenResponse, RegisterResponse
from litestar.params import Dependency
class AuthController(Controller):
    path = "/api/v1/auth"

    @post("/register", status_code=HTTP_201_CREATED, opt={"publico": True})
    async def register(
        self,
        data: UserCredentials,
        user_repo: UserRepository = Dependency()
    ) -> RegisterResponse:
        return await register_new_user(data, user_repo)

    @post("/login", status_code=HTTP_200_OK, opt={"publico": True})
    async def login(
        self, data: UserCredentials,
        user_repo: UserRepository = Dependency()
    ) -> TokenResponse:
        return await authenticate_user(data, user_repo)
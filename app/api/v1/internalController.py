from litestar import Controller, post
from litestar.status_codes import HTTP_200_OK
from uuid import UUID
from app.domain.structs import ExpPayload
from app.services.user_service import add_exp_to_user
from app.repositories.user_repository import UserRepository    

class InternalController(Controller):
    path = "/internal/users"

    @post("/{user_id:uuid}/add-xp", status_code=HTTP_200_OK)
    async def add_xp(
        self,
        user_id: UUID,
        data: ExpPayload,
        user_repo: UserRepository
    ) -> dict:
        result = await add_exp_to_user(user_id, data.exp_to_add, user_repo)
        return result
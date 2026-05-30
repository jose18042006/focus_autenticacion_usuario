from litestar import Controller, patch
from litestar.status_codes import HTTP_200_OK
from uuid import UUID
from app.domain.structs import ExpPayload
from app.services.user_service import update_user_exp
from app.repositories.user_repository import UserRepository    

class InternalController(Controller):
    path = "/internal/users"

    @patch("/me/exp/batch")
    async def add_xp(
        self,
        user_id: UUID,
        data: ExpPayload,
        user_repo: UserRepository,
    ) -> dict:
        result = await update_user_exp(user_id, data.exp_to_add, user_repo)
        return result
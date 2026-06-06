from uuid import UUID
from litestar import Controller, patch, Request
from app.services.user_service import update_user_exp
from app.repositories.user_repository import UserRepository    
from app.domain.structs import ExpPayload, UpdateExpResponse

class UsersController(Controller):
    path = "/api/v1/users"

    @patch("/me/exp/batch")
    async def add_xp(
        self,
        request: Request,
        data: ExpPayload,
        user_repo: UserRepository,
    ) -> UpdateExpResponse:
        
        user_data = request.user
        user_id_str = str(user_data.get("sub")) if isinstance(user_data, dict) else str(user_data)

        return await update_user_exp(UUID(user_id_str), data.exp_to_add, user_repo)
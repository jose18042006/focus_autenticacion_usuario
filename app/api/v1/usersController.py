from litestar import Controller, patch, Request
from app.domain.structs import ExpPayload
from app.services.user_service import update_user_exp
from app.repositories.user_repository import UserRepository    

class UsersController(Controller):
    path = "/api/v1/users"

    @patch("/me/exp/batch")
    async def add_xp(
        self,
        request: Request,
        data: ExpPayload,
        user_repo: UserRepository,
    ) -> dict:
        
        user_id = request.user 
        result = await update_user_exp(user_id, data.exp_to_add, user_repo)

        return result
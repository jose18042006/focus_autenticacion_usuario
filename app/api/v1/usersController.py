from uuid import UUID
from litestar import Controller, patch, Request, get
from app.services.user_service import update_user_exp, get_stats_from_user
from app.repositories.user_repository import UserRepository    
from app.domain.structs import ExpPayload, UpdateExpResponse, UserStatsResponse
from litestar.exceptions import ValidationException
from litestar.params import Dependency

class UsersController(Controller):
    path = "/api/v1/users"

    @get("/me/stats")
    async def get_my_stats(
        self, 
        request: Request, 
        user_repo: UserRepository = Dependency()
    ) -> UserStatsResponse:
        
        user_data = request.user
        user_id_str = str(user_data.get("sub")) if isinstance(user_data, dict) else str(user_data)
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise ValidationException("El ID del usuario en el token no es válido.")
        
        return await get_stats_from_user(user_id,user_repo)
        

    @patch("/me/exp/batch")
    async def add_xp(
        self,
        request: Request,
        data: ExpPayload,
        user_repo: UserRepository = Dependency(),
    ) -> UpdateExpResponse:
        
        user_data = request.user
        user_id_str = str(user_data.get("sub")) if isinstance(user_data, dict) else str(user_data)
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise ValidationException("El ID del usuario en el token no es válido.")

        return await update_user_exp(user_id, data.exp_to_add, user_repo)
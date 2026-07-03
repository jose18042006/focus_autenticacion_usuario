from uuid import UUID
from litestar import Controller, patch, Request, get, delete
from app.services.user_service import (
    update_user_exp, 
    get_stats_from_user, 
    get_all_users_list, 
    modify_user_full, 
    remove_user_by_id
)
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
        
        return await get_stats_from_user(user_id, user_repo)

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

    # ==============================================================================
    # ⚙️ ENDPOINTS CONECTADOS COMPLETOS PARA OPERACIONES CRUD DEL PANEL
    # ==============================================================================

    @get("/")
    async def list_all_users_dashboard(
        self, 
        user_repo: UserRepository = Dependency()
    ) -> list:
        users = await get_all_users_list(user_repo)
        return [
            {
                "id": str(u.id),
                "email": u.email,
                "role": getattr(u.role, 'value', str(u.role)),
                "total_exp": u.total_exp,
                "current_level": u.current_level
            }
            for u in users
        ]

    @patch("/{user_id:uuid}")
    async def edit_user_dashboard(
        self,
        user_id: UUID,
        request: Request,
        user_repo: UserRepository = Dependency()
    ) -> dict:
        payload = await request.json()
        updated_user = await modify_user_full(user_id, payload, user_repo)
        return {
            "id": str(updated_user.id),
            "email": updated_user.email,
            "role": getattr(updated_user.role, 'value', str(updated_user.role)),
            "total_exp": updated_user.total_exp,
            "current_level": updated_user.current_level,
            "message": "Usuario actualizado de manera exitosa"
        }

    @delete("/{user_id:uuid}", status_code=200)  # 🔥 CORREGIDO: Forzamos status 200 para que soporte el return
    async def delete_user_dashboard(
        self,
        user_id: UUID,
        user_repo: UserRepository = Dependency()
    ) -> dict:
        await remove_user_by_id(user_id, user_repo)
        return {"message": "Usuario eliminado correctamente", "id": str(user_id)}
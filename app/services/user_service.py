from uuid import UUID
import math
from litestar.exceptions import NotAuthorizedException, HTTPException
from app.models.user import UserModel
from app.domain.structs import UserCredentials, TokenResponse
from app.services.auth_logic import hash_password, verify_password, create_access_token
from app.repositories.user_repository import UserRepository


async def register_new_user(
        data: UserCredentials,
        user_repo: UserRepository
    ) -> UserModel:

    existing_user = await user_repo.get_one_or_none(email=data.email)
    
    if existing_user:
        raise HTTPException(status_code=409, detail="El correo electrónico ya está registrado.")    
    
    new_user = UserModel(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    created_user = await user_repo.add(new_user)
    
    return created_user

async def authenticate_user(
        data: UserCredentials,
        user_repo: UserRepository
    ) -> TokenResponse:
    user = await user_repo.get_one_or_none(email=data.email)
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise NotAuthorizedException("Credenciales incorrectas.")
    
    token = create_access_token(user.email, str(user.id), user.role.value)
    
    return TokenResponse(access_token=token)

async def update_user_exp(user_id: UUID, added_exp: int, user_repo: UserRepository) -> dict:
    user = await user_repo.get_one(id=user_id)
    
    user.total_exp += added_exp
    
    new_level = get_level_from_total_exp(user.total_exp)
    
    result = {
        "new_level": new_level,
        "levels_gained": new_level - user.current_level,
        "leveled_up": new_level > user.current_level
    }
    
    user.current_level = new_level
    await user_repo.update(user)
    return result


def calculate_total_exp_required(level: int, base: int = 100, ratio: float = 1.2) -> int:
    if level <= 1:
        return 0
    return int(base * (math.pow(ratio, level - 1) - 1) / (ratio - 1))

def get_level_from_total_exp(total_exp: int, base: int = 100, ratio: float = 1.2) -> int:
    if total_exp < base:
        return 1
    val = (total_exp * (ratio - 1) / base) + 1
    level = math.log(val, ratio) + 1
    return int(level)
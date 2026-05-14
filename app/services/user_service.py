from uuid import UUID
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

async def add_exp_to_user(
        user_id: UUID,
        exp_to_add: int,
        user_repo: UserRepository
        ) -> dict:

    user = await user_repo.get_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.total_exp += exp_to_add
    
    nivel_anterior = user.current_level
    user.current_level = (user.total_exp // 1000) + 1
    
    leveled_up = user.current_level > nivel_anterior
    
    await user_repo.update(user)
    
    return {
        "new_exp": user.total_exp,
        "current_level": user.current_level,
        "leveled_up": leveled_up
    }
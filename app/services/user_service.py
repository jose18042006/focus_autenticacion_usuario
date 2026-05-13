from litestar.exceptions import NotAuthorizedException, ConflictException
from app.models.user import UserModel
from app.domain.structs import UserCredentials, TokenResponse
from app.services.auth_logic import hash_password, verify_password, create_access_token
from app.repositories.user_repository import UserRepository


async def register_new_user(data: UserCredentials, user_repo: UserRepository) -> UserModel:

    existing_user = await user_repo.get_one_or_none(email=data.email)
    
    if existing_user:
        raise ConflictException("El correo electrónico ya está registrado.")
    
    new_user = UserModel(
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    created_user = await user_repo.add(new_user)
    
    return created_user

async def authenticate_user(data: UserCredentials, user_repo: UserRepository) -> TokenResponse:
    
    user = await user_repo.get_one_or_none(email=data.email)
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise NotAuthorizedException("Credenciales incorrectas.")
    
    token = create_access_token(user.email, user.id)
    
    return TokenResponse(access_token=token)
from uuid import UUID
import math
from litestar.exceptions import NotAuthorizedException, HTTPException, NotFoundException
from app.models.user import UserModel
from app.services.auth_logic import hash_password, verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.domain.structs import UserCredentials, TokenResponse, RegisterResponse, UpdateExpResponse, UserStatsResponse, UserRole

async def register_new_user(
        data: UserCredentials,
        user_repo: UserRepository
) -> RegisterResponse:

    existing_user = await user_repo.get_one_or_none(email=data.email)
    
    if existing_user:
        raise HTTPException(status_code=409, detail="El correo electrónico ya está registrado.")    
    
    # Registra directamente con el rol explícito validado que viene en el DTO
    new_user = UserModel(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    created_user = await user_repo.add(new_user, auto_commit=True)
    
    return RegisterResponse(
        message="Usuario registrado exitosamente",
        email=created_user.email,
        id=created_user.id  
    )

async def authenticate_user(
        data: UserCredentials,
        user_repo: UserRepository
) -> TokenResponse:
    user = await user_repo.get_one_or_none(email=data.email)
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise NotAuthorizedException("Credenciales incorrectas.")
    
    # Convierte el Enum a texto plano para inyectarlo dentro del token JWT
    role_value = getattr(user.role, 'value', str(user.role))
    token = create_access_token(user.email, str(user.id), role_value)
    
    return TokenResponse(access_token=token)

async def update_user_exp(
    user_id: UUID,
    added_exp: int,
    user_repo: UserRepository
) -> UpdateExpResponse:
    user = await user_repo.get_one(id=user_id)
    
    user.total_exp += added_exp
    
    new_level = get_level_from_total_exp(user.total_exp)    
    levels_gained = new_level - user.current_level
    leveled_up = new_level > user.current_level
    user.current_level = new_level

    await user_repo.update(user, auto_commit=True)
    
    return UpdateExpResponse(
        new_level=new_level,
        levels_gained=levels_gained,
        leveled_up=leveled_up,
        total_exp=user.total_exp
    )

async def get_stats_from_user(
    user_id: UUID,
    user_repo: UserRepository
) -> UserStatsResponse:
    user = await user_repo.get_one_or_none(id=user_id)
    if not user:
        raise NotFoundException("Usuario no encontrado en la base de datos.")
    
    return UserStatsResponse(
        total_exp=user.total_exp,
        current_level=user.current_level
    )

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


# ==============================================================================
# 🛠️ FUNCIONES CRUD DE EXTENSIÓN PARA EL PANEL DE ADMINISTRACIÓN
# ==============================================================================

async def get_all_users_list(user_repo: UserRepository) -> list[UserModel]:
    """Consulta la base de datos completa y devuelve todos los usuarios"""
    from sqlalchemy import select
    result = await user_repo.session.execute(select(UserModel))
    return list(result.scalars().all())

async def modify_user_full(
    user_id: UUID, 
    payload: dict, 
    user_repo: UserRepository
) -> UserModel:
    """Modifica dinámicamente cualquier campo editado desde la interfaz web"""
    user = await user_repo.get_one_or_none(id=user_id)
    if not user:
        raise NotFoundException("El usuario solicitado no existe.")

    if "email" in payload:
        user.email = payload["email"]
        
    if "role" in payload:
        role_str = str(payload["role"]).lower().strip()
        if role_str == "administrador":
            user.role = UserRole.ADMINISTRADOR
        elif role_str == "dm":
            user.role = UserRole.DM
        else:
            user.role = UserRole.STUDENT
            
    if "current_level" in payload:
        user.current_level = int(payload["current_level"])
        
    if "total_exp" in payload:
        user.total_exp = int(payload["total_exp"])
        
    if "password" in payload and payload["password"]:
        user.hashed_password = hash_password(payload["password"])

    await user_repo.update(user, auto_commit=True)
    return user

async def remove_user_by_id(user_id: UUID, user_repo: UserRepository) -> bool:
    """Borra físicamente el registro de la base de datos relacional"""
    user = await user_repo.get_one_or_none(id=user_id)
    if not user:
        raise NotFoundException("El usuario a eliminar no existe.")
    
    await user_repo.session.delete(user)
    await user_repo.session.commit()
    return True
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from litestar import Litestar, post, Response, get
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from passlib.context import CryptContext

# Configuración de Seguridad
SECRET_KEY = "una_clave_muy_secreta_y_larga_12345"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# "Base de datos" temporal
users_db: dict[str, str] = {} 

@dataclass
class UserData:
    email: str
    password: str

# --- FUNCIONES ---
def create_token(email: str) -> str:
    # Usamos timezone.utc para evitar advertencias en Python moderno
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

# --- ENDPOINTS ---

@post("/register")
async def register(data: UserData) -> Any:
    if data.email in users_db:
        return Response(
            content={"detail": "El usuario ya existe"}, 
            status_code=HTTP_409_CONFLICT
        )
    
    hashed_password = pwd_context.hash(data.password)
    users_db[data.email] = hashed_password
    return {"message": "Usuario registrado", "email": data.email}

@post("/login")
async def login(data: UserData) -> Any:
    user_hashed_pwd = users_db.get(data.email)
    
    if not user_hashed_pwd or not pwd_context.verify(data.password, user_hashed_pwd):
        return Response(
            content={"detail": "Credenciales incorrectas"}, 
            status_code=HTTP_401_UNAUTHORIZED
        )
    
    token = create_token(data.email)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@get("/")
async def health() -> dict:
    return {"status": "ok"}

@get("/users")
async def get_users() -> dict:
    return {"users": users_db}

app = Litestar(route_handlers=[register, login, health, get_users])


import os
from litestar.security.jwt import JWTAuth, Token
from litestar.connection import ASGIConnection

SECRET_KEY = os.getenv("SECRET_KEY", "clave_super_secreta")

async def retrieve_user_handler(token: Token, connection: ASGIConnection) -> str:
    return token.sub

jwt_auth = JWTAuth[str](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=SECRET_KEY,
    exclude=["/api/v1/auth/login", "/api/v1/auth/register"] 
)
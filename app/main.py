from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.authController import AuthController
from app.api.v1.usersController import UsersController
from app.repositories.user_repository import UserRepository
from app.core.db_config import db_plugin
from app.core.security import jwt_auth

async def provide_user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)

app = Litestar(
    route_handlers=[
        AuthController,
        UsersController
    ],
    on_app_init=[jwt_auth.on_app_init],
    plugins=[db_plugin],
    dependencies={
        "user_repo": Provide(provide_user_repo)
    }
)
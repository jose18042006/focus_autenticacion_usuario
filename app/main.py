from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.authController import AuthController
from app.api.v1.internalController import InternalController
from app.repositories.user_repository import UserRepository
from app.core.db_config import db_plugin

async def provide_user_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)

app = Litestar(
    route_handlers=[
        AuthController,
        InternalController
    ],
    plugins=[db_plugin],
    dependencies={
        "user_repo": Provide(provide_user_repo)
    }
)
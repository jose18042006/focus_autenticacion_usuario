from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from app.models.user import UserModel

class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel
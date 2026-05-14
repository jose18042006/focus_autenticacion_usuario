import msgspec
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    DM = "dm"

class UserCredentials(msgspec.Struct):
    email: str
    password: str
    role: UserRole = UserRole.STUDENT

class TokenResponse(msgspec.Struct):
    access_token: str
    token_type: str = "bearer"

class UserProfileResponse(msgspec.Struct):
    id: UUID
    email: str
    total_xp: int
    current_level: int
    role: UserRole
import msgspec
from uuid import UUID

class UserCredentials(msgspec.Struct):
    email: str
    password: str

class TokenResponse(msgspec.Struct):
    access_token: str
    token_type: str = "bearer"

class UserProfileResponse(msgspec.Struct):
    id: UUID
    email: str
    total_xp: int
    current_level: int
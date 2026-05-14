import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from litestar.exceptions import HTTPException, NotAuthorizedException

from app.services.user_service import register_new_user, authenticate_user
from app.domain.structs import UserCredentials, UserRole
from app.models.user import UserModel
from app.services.auth_logic import hash_password

@pytest.mark.asyncio
async def test_register_new_user_success():
    mock_repo = AsyncMock()
    mock_repo.get_one_or_none.return_value = None 
    
    credentials = UserCredentials(email="nuevo@mail.com", password="123")
    
    fake_user = UserModel(id=uuid4(), email="nuevo@mail.com", role=UserRole.STUDENT)
    mock_repo.add.return_value = fake_user
    
    result = await register_new_user(credentials, mock_repo)
    
    assert result.email == "nuevo@mail.com"
    mock_repo.add.assert_called_once()

@pytest.mark.asyncio
async def test_register_new_user_conflict():
    mock_repo = AsyncMock()
    mock_repo.get_one_or_none.return_value = UserModel(email="clon@mail.com") 
    
    credentials = UserCredentials(email="clon@mail.com", password="123")
    
    with pytest.raises(HTTPException) as excinfo:
        await register_new_user(credentials, mock_repo)
    
    assert excinfo.value.status_code == 409
    mock_repo.add.assert_not_called()

@pytest.mark.asyncio
async def test_authenticate_user_success():
    mock_repo = AsyncMock()
    credentials = UserCredentials(email="fury@mail.com", password="password_correcta")
    
    fake_user = UserModel(
        id=uuid4(), 
        email="fury@mail.com", 
        hashed_password=hash_password("password_correcta"),
        role=UserRole.DM
    )
    mock_repo.get_one_or_none.return_value = fake_user
    
    token_response = await authenticate_user(credentials, mock_repo)
    
    assert token_response.access_token is not None
    assert isinstance(token_response.access_token, str)

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    mock_repo = AsyncMock()
    credentials = UserCredentials(email="fury@mail.com", password="hacker123")
    
    fake_user = UserModel(
        id=uuid4(), 
        email="fury@mail.com", 
        hashed_password=hash_password("password_correcta"),
        role=UserRole.STUDENT
    )
    mock_repo.get_one_or_none.return_value = fake_user
    
    with pytest.raises(NotAuthorizedException):
        await authenticate_user(credentials, mock_repo)
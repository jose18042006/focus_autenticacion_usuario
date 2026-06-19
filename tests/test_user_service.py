import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from litestar.exceptions import HTTPException, NotAuthorizedException, NotFoundException

from app.services.user_service import register_new_user, authenticate_user, update_user_exp, get_stats_from_user
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
        role=UserRole.STUDENT
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

@pytest.mark.asyncio
async def test_update_user_exp_level_up():
    mock_repo = AsyncMock()
    
    fake_user = UserModel(id=uuid4(), email="estudiante@mail.com", total_exp=0, current_level=1)
    
    mock_repo.get_one.return_value = fake_user 
    
    result = await update_user_exp(fake_user.id, 150, mock_repo)
    
    assert result.new_level == 2
    assert result.leveled_up is True
    assert result.levels_gained == 1
    
    mock_repo.update.assert_called_once_with(fake_user, auto_commit=True)
    assert fake_user.total_exp == 150


@pytest.mark.asyncio
async def test_get_user_stats_service_success():
    user_id = uuid4()
    mock_user = UserModel(id=user_id, total_exp=1200, current_level=5)
    
    mock_repo = AsyncMock()
    mock_repo.get_one_or_none.return_value = mock_user

    result = await get_stats_from_user(user_id, mock_repo)

    assert result.total_exp == 1200
    assert result.current_level == 5
    mock_repo.get_one_or_none.assert_called_once_with(id=user_id)


@pytest.mark.asyncio
async def test_get_user_stats_service_not_found():
    # Arrange
    user_id = uuid4()
    mock_repo = AsyncMock()
    mock_repo.get_one_or_none.return_value = None
    with pytest.raises(NotFoundException) as exc_info:
        await get_stats_from_user(user_id, mock_repo)
    
    assert "Usuario no encontrado" in str(exc_info.value)
    mock_repo.get_one_or_none.assert_called_once_with(id=user_id)
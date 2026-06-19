import os
import jwt
import pytest
from uuid import uuid4
from unittest.mock import patch as mock_patch, AsyncMock
from datetime import datetime, timedelta, timezone

from litestar import Litestar
from litestar.testing import TestClient
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from app.api.v1.authController import AuthController
from app.api.v1.usersController import UsersController 
from app.core.security import jwt_auth
from app.domain.structs import TokenResponse
from app.repositories.user_repository import UserRepository
from app.domain.structs import RegisterResponse, UpdateExpResponse, UserStatsResponse


os.environ["SECRET_KEY"] = "clave_super_secreta"

def get_test_token(user_id: str) -> str:
    secret = jwt_auth.token_secret
    if not isinstance(secret, str):
        secret = str(secret)
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=10)
    payload = {
        "sub": user_id,
        "exp": int(exp.timestamp()), 
        "iat": int(now.timestamp())  
    }
    return jwt.encode(payload, secret, algorithm="HS256")

@pytest.fixture
def mock_repo():
    return AsyncMock(spec=UserRepository)

@pytest.fixture
def client(mock_repo):
    test_app = Litestar(
        route_handlers=[AuthController, UsersController],
        on_app_init=[jwt_auth.on_app_init],
        dependencies={"user_repo": Provide(lambda: mock_repo, sync_to_thread=False)}
    )
    with TestClient(app=test_app) as client:
        yield client

@mock_patch("app.api.v1.authController.register_new_user", new_callable=AsyncMock)
def test_register_endpoint(mock_register, client: TestClient) -> None:
    fake_uuid = uuid4()
    
    mock_register.return_value = RegisterResponse(
        message="Usuario registrado exitosamente", 
        email="api@mail.com", 
        id=fake_uuid
    )

    response = client.post(
        "api/v1/auth/register", 
        json={"email": "api@mail.com", "password": "123", "role": "student"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "api@mail.com"
    assert data["id"] == str(fake_uuid)

@mock_patch("app.api.v1.authController.authenticate_user", new_callable=AsyncMock)
def test_login_endpoint(mock_auth, client: TestClient) -> None:
    mock_auth.return_value = TokenResponse(access_token="eyJhbGciOiJIUzI1NiIsInR...")
    
    response = client.post(
        "api/v1/auth/login",
        json={"email": "api@mail.com", "password": "123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@mock_patch("app.api.v1.usersController.update_user_exp", new_callable=AsyncMock)
def test_add_exp_batch_endpoint(mock_update_exp, client: TestClient) -> None:
    test_uuid = str(uuid4())
    
    mock_update_exp.return_value = UpdateExpResponse(
        new_level=2, 
        levels_gained=1, 
        leveled_up=True,
        total_exp=150
    )
    
    auth_headers = {"Authorization": f"Bearer {get_test_token(test_uuid)}"}
    
    response = client.patch(
        "/api/v1/users/me/exp/batch",
        json={"exp_to_add": 150},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["new_level"] == 2
    assert data["leveled_up"] is True
    assert data["levels_gained"] == 1

@mock_patch("app.api.v1.usersController.get_stats_from_user", new_callable=AsyncMock)
def test_get_my_stats_endpoint_success(mock_search_stats, client: TestClient) -> None:
    test_uuid = str(uuid4())
    
    mock_search_stats.return_value = UserStatsResponse(
        total_exp=450,
        current_level=5
    )
    
    auth_headers = {"Authorization": f"Bearer {get_test_token(test_uuid)}"}
    
    response = client.get(
        "/api/v1/users/me/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_exp"] == 450
    assert data["current_level"] == 5

@mock_patch("app.api.v1.usersController.get_stats_from_user", new_callable=AsyncMock)
def test_get_my_stats_endpoint_not_found(mock_search_stats, client: TestClient) -> None:
    test_uuid = str(uuid4())
    
    mock_search_stats.side_effect = NotFoundException("Usuario no encontrado en la base de datos.")
    
    auth_headers = {"Authorization": f"Bearer {get_test_token(test_uuid)}"}
    
    response = client.get(
        "/api/v1/users/me/stats",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Usuario no encontrado" in data["detail"]
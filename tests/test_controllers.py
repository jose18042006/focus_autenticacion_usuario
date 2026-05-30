import os
import jwt
import pytest
from uuid import uuid4
from unittest.mock import patch as mock_patch, AsyncMock
from datetime import datetime, timedelta, timezone

from litestar import Litestar
from litestar.testing import TestClient
from litestar.di import Provide

from app.api.v1.authController import AuthController
from app.api.v1.usersController import UsersController 
from app.core.security import jwt_auth
from app.domain.structs import TokenResponse
from app.models.user import UserModel
from app.domain.structs import UserRole
from app.repositories.user_repository import UserRepository

os.environ["SECRET_KEY"] = "clave_super_secreta"

def get_test_token(user_id: str) -> str:
    secret = jwt_auth.token_secret
    if not isinstance(secret, str):
        secret = str(secret)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "exp": now + timedelta(minutes=10),
        "iat": now
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
    mock_register.return_value = UserModel(id=fake_uuid, email="api@mail.com", role=UserRole.STUDENT)
    
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
    
    mock_update_exp.return_value = {
        "new_level": 2, 
        "levels_gained": 1, 
        "leveled_up": True
    }
    
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
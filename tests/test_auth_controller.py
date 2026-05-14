from litestar.testing import TestClient
from litestar.di import Provide
from unittest.mock import patch as mock_patch, AsyncMock
from uuid import uuid4

from app.main import app
from app.domain.structs import TokenResponse
from app.models.user import UserModel
from app.domain.structs import UserRole

@mock_patch("app.api.v1.authController.register_new_user", new_callable=AsyncMock)
def test_register_endpoint(mock_register) -> None:
    
    app.dependencies["user_repo"] = Provide(lambda: AsyncMock(), sync_to_thread=False)
    
    fake_uuid = uuid4()
    mock_register.return_value = UserModel(id=fake_uuid, email="api@mail.com", role=UserRole.STUDENT)
    
    with TestClient(app=app) as client:
        response = client.post(
            "/auth/register",
            json={"email": "api@mail.com", "password": "123", "role": "student"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "api@mail.com"
        assert data["id"] == str(fake_uuid)

@mock_patch("app.api.v1.authController.authenticate_user", new_callable=AsyncMock)
def test_login_endpoint(mock_auth) -> None:
    
    app.dependencies["user_repo"] = Provide(lambda: AsyncMock(), sync_to_thread=False)
    
    mock_auth.return_value = TokenResponse(access_token="eyJhbGciOiJIUzI1NiIsInR...")
    
    with TestClient(app=app) as client:
        response = client.post(
            "/auth/login",
            json={"email": "api@mail.com", "password": "123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
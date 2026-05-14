from litestar.testing import TestClient
from litestar.di import Provide
from unittest.mock import patch as mock_patch, AsyncMock
from uuid import uuid4
from app.main import app


@mock_patch("app.api.v1.internalController.add_exp_to_user", new_callable=AsyncMock)
def test_add_exp_endpoint(mock_add_exp) -> None:
    app.dependencies["user_repo"] = Provide(lambda: AsyncMock(), sync_to_thread=False)
    
    test_uuid = uuid4()
    mock_add_exp.return_value = {"new_exp": 1150, "current_level": 2, "leveled_up": True}
    
    with TestClient(app=app) as client:
        response = client.post(
            f"/internal/users/{test_uuid}/add-exp",
            json={"exp_to_add": 150}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["new_exp"] == 1150
        assert data["leveled_up"] is True

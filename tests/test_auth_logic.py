import jwt
from uuid import uuid4
from app.services.auth_logic import (
    hash_password, 
    verify_password, 
    create_access_token, 
    SECRET_KEY, 
    ALGORITHM
)
from app.domain.structs import UserRole

def test_password_hashing_and_verification():
    plain_password = "mi_super_secreta_password_123"
    
    hashed = hash_password(plain_password)
    assert hashed != plain_password
    assert hashed.startswith("$argon2") 
    
    assert verify_password(plain_password, hashed) is True
    assert verify_password("password_incorrecta", hashed) is False

def test_create_access_token():
    test_email = "estudiante@focus.com"
    test_id = str(uuid4())
    test_role = UserRole.STUDENT.value
    
    token = create_access_token(test_email, test_id, test_role)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload["sub"] == test_id
    
    assert payload["email"] == test_email
    
    assert payload["role"] == test_role
    assert "exp" in payload
    
    assert "iat" in payload
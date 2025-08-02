from jose import jwt
from app.core.config import settings

def test_token_creation(test_client):
    # تست ایجاد و اعتبارسنجی توکن
    test_data = {"sub": "testuser"}
    token = create_access_token(test_data)
    
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM]
    )
    
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded
import uuid

from app.config.settings import settings
from app.security.password import hash_password, verify_password
from app.security.tokens import create_token_pair, decode_token


def test_password_hashing():
    pwd = "super-secure-password"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_generation_and_decoding():
    user_id = uuid.uuid4()
    email = "researcher@quorix.ai"
    tokens = create_token_pair(user_id=user_id, email=email, settings=settings)

    assert "access_token" in tokens
    assert "refresh_token" in tokens

    payload = decode_token(tokens["access_token"], settings)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["type"] == "access"

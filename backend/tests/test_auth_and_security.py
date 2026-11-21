"""HER AI — Security, Authentication & Data Isolation Tests (Milestone 11)

Tests:
  - Argon2id password hashing & verification
  - JWT creation, decoding, expiration & tamper protection
  - Rejection of unauthenticated requests (HTTP 401)
  - Rejection of invalid tokens & expired tokens (HTTP 401)
  - Rejection of deactivated users (HTTP 403)
  - Strict cross-user data isolation across conversations and memories
  - Rate limiting enforcement (HTTP 429)
"""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.memory import Memory


# ──────────────────────────────────────────────────────────────────────────────
# 1. Argon2id Password Hashing Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_argon2id_hashing_format_and_verification():
    pw = "SuperSecretPassword123!"
    hashed = hash_password(pw)
    assert hashed.startswith("$argon2id$")
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(pw, "") is False


def test_argon2id_empty_password_raises():
    with pytest.raises(ValueError):
        hash_password("")


# ──────────────────────────────────────────────────────────────────────────────
# 2. JWT Access Token Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_jwt_issuance_and_decoding():
    user_id = str(uuid4())
    token = create_access_token(subject=user_id, claims={"username": "test_user"})
    decoded = decode_access_token(token)
    assert decoded["sub"] == user_id
    assert decoded["username"] == "test_user"
    assert "exp" in decoded
    assert "iat" in decoded


def test_jwt_expired_token_raises():
    user_id = str(uuid4())
    # Generate token that expired 1 hour ago
    token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-3600))
    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_jwt_tampered_token_raises():
    user_id = str(uuid4())
    token = create_access_token(subject=user_id)
    tampered_token = token[:-5] + "xxxxx"
    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered_token)


# ──────────────────────────────────────────────────────────────────────────────
# 3. FastAPI Authentication Dependency Tests
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def test_app():
    app = FastAPI()

    @app.get("/protected")
    def protected_route(user: User = Depends(get_current_user)):
        return {"user_id": str(user.id), "username": user.username}

    return app


def test_unauthorized_access_missing_token(test_app):
    client = TestClient(test_app)
    res = client.get("/protected")
    assert res.status_code == 401
    assert "Not authenticated" in res.text or "detail" in res.json()


def test_unauthorized_access_invalid_token(test_app):
    client = TestClient(test_app)
    res = client.get("/protected", headers={"Authorization": "Bearer invalid.fake.token"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials."


def test_unauthorized_access_expired_token(test_app):
    client = TestClient(test_app)
    user_id = str(uuid4())
    expired_token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-60))
    res = client.get("/protected", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Token has expired."


def test_authenticated_user_access(test_app):
    user_id = uuid4()
    mock_user = User(
        id=user_id,
        username="authenticated_hero",
        email="hero@her.ai",
        is_active=True,
    )

    valid_token = create_access_token(subject=str(user_id))

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    from app.core.database import get_db
    test_app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(test_app)
    res = client.get("/protected", headers={"Authorization": f"Bearer {valid_token}"})
    assert res.status_code == 200
    assert res.json()["user_id"] == str(user_id)
    assert res.json()["username"] == "authenticated_hero"

    test_app.dependency_overrides.clear()


def test_deactivated_user_blocked(test_app):
    user_id = uuid4()
    mock_user = User(
        id=user_id,
        username="banned_user",
        email="banned@her.ai",
        is_active=False,
    )

    valid_token = create_access_token(subject=str(user_id))

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    from app.core.database import get_db
    test_app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(test_app)
    res = client.get("/protected", headers={"Authorization": f"Bearer {valid_token}"})
    assert res.status_code == 403
    assert res.json()["detail"] == "User account is deactivated."

    test_app.dependency_overrides.clear()


# ──────────────────────────────────────────────────────────────────────────────
# 4. Strict Cross-User Data Isolation Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_cross_user_conversation_isolation():
    """Verify that User B cannot access or modify User A's conversation."""
    from app.main import app
    from app.core.database import get_db

    user_a_id = uuid4()
    user_b_id = uuid4()

    user_b = User(id=user_b_id, username="user_b", email="b@her.ai", is_active=True)

    token_b = create_access_token(subject=str(user_b_id))

    conv_id = uuid4()

    mock_db = MagicMock()
    # When querying user, return user_b
    mock_db.query.return_value.filter.return_value.first.return_value = user_b
    # When querying conversation with Conversation.user_id == user_b_id, return None (not found!)
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)

    # Attempt to GET User A's conversation with User B's token
    res = client.get(f"/api/conversations/{conv_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Conversation not found."

    # Attempt to DELETE User A's conversation with User B's token
    res = client.delete(f"/api/conversations/{conv_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Conversation not found."

    app.dependency_overrides.clear()


def test_cross_user_memory_isolation():
    """Verify that User B cannot access or modify User A's memory."""
    from app.main import app
    from app.core.database import get_db

    user_b_id = uuid4()
    user_b = User(id=user_b_id, username="user_b", email="b@her.ai", is_active=True)
    token_b = create_access_token(subject=str(user_b_id))
    mem_id = uuid4()

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = user_b

    # Memory service returns None when queried with user_b_id
    with patch("app.api.memories.memory_service.get_memory", return_value=None), \
         patch("app.api.memories.memory_service.delete_memory", return_value=False):
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)

        res = client.get(f"/api/memories/{mem_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res.status_code == 404
        assert res.json()["detail"] == "Memory not found."

        res = client.delete(f"/api/memories/{mem_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res.status_code == 404
        assert res.json()["detail"] == "Memory not found."

        app.dependency_overrides.clear()


# ──────────────────────────────────────────────────────────────────────────────
# 5. Rate Limiting Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_rate_limiting_enforcement():
    """Verify that exceeding configured rate limit triggers HTTP 429 Too Many Requests."""
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    rl_app = FastAPI()
    test_limiter = Limiter(key_func=get_remote_address)
    rl_app.state.limiter = test_limiter
    rl_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @rl_app.get("/rate-limited-endpoint")
    @test_limiter.limit("2/minute")
    def limited_route(request: Request):
        return {"status": "ok"}

    client = TestClient(rl_app)

    # 1st request -> OK
    r1 = client.get("/rate-limited-endpoint")
    assert r1.status_code == 200

    # 2nd request -> OK
    r2 = client.get("/rate-limited-endpoint")
    assert r2.status_code == 200

    # 3rd request -> 429 Too Many Requests!
    r3 = client.get("/rate-limited-endpoint")
    assert r3.status_code == 429
    assert "Too Many Requests" in r3.text or "Rate limit exceeded" in r3.text


# ──────────────────────────────────────────────────────────────────────────────
# 6. User Registration, Login & Account Deletion End-to-End Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_registration_success_and_duplicate_rejection():
    """Verify user registration returns token and duplicate returns 409."""
    from datetime import datetime, timezone
    from app.main import app
    from app.core.database import get_db

    mock_db = MagicMock()
    # First check: user does not exist
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    def mock_refresh(user_obj):
        now = datetime.now(timezone.utc)
        user_obj.id = uuid4()
        user_obj.created_at = now
        user_obj.updated_at = now

    mock_db.refresh.side_effect = mock_refresh

    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)

    reg_payload = {
        "username": "unique_tester",
        "email": "unique@her.ai",
        "password": "Password123!"
    }

    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "unique_tester"

    # Second check: simulate duplicate username/email
    now = datetime.now(timezone.utc)
    existing_user = User(id=uuid4(), username="unique_tester", email="unique@her.ai", created_at=now, updated_at=now)
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing_user

    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 409
    assert "already registered" in res_dup.json()["detail"]

    app.dependency_overrides.clear()


def test_login_success_and_invalid_credentials():
    """Verify valid login returns token and invalid credentials return 401."""
    from datetime import datetime, timezone
    from app.main import app
    from app.core.database import get_db

    now = datetime.now(timezone.utc)
    user_id = uuid4()
    plain_password = "CorrectPassword123!"
    hashed = hash_password(plain_password)
    user = User(
        id=user_id,
        username="active_user",
        email="active@her.ai",
        hashed_password=hashed,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = user

    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)

    # Valid login
    res_ok = client.post("/api/auth/login", json={"username_or_email": "active_user", "password": plain_password})
    assert res_ok.status_code == 200
    assert "access_token" in res_ok.json()

    # Invalid password
    res_bad = client.post("/api/auth/login", json={"username_or_email": "active_user", "password": "WrongPassword!"})
    assert res_bad.status_code == 401
    assert "Incorrect username/email or password." in res_bad.json()["detail"]

    app.dependency_overrides.clear()


def test_account_deletion_and_data_cleanup():
    """Verify that DELETE /api/profile permanently deletes user data and account."""
    from app.main import app
    from app.core.database import get_db

    user_id = uuid4()
    user = User(id=user_id, username="delete_me", email="delete@her.ai", is_active=True)
    token = create_access_token(subject=str(user_id))

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = user

    with patch("app.api.profile.memory_service.delete_all_user_memories", return_value=5):
        app.dependency_overrides[get_db] = lambda: mock_db
        client = TestClient(app)

        res = client.delete("/api/profile", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["deleted"] is True
        assert data["memories_deleted"] == 5
        assert "successfully deleted" in data["message"]

        # Ensure db.delete was called on the user
        mock_db.delete.assert_called_with(user)
        mock_db.commit.assert_called()

        app.dependency_overrides.clear()


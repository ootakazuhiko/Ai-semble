"""
認証サービスのテスト
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.security.models import Base, User, Role, Permission
from src.security.auth import AuthService, AuthError

# テスト用のデータベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """テスト用のデータベースセッションを作成"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_service(db_session):
    """認証サービスのインスタンスを作成"""
    return AuthService(
        db=db_session,
        secret_key="test_secret_key",
        access_token_expire_minutes=30
    )

@pytest.fixture
def test_user(db_session, auth_service):
    """テスト用のユーザーを作成"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=auth_service.get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_role(db_session):
    """テスト用のロールを作成"""
    role = Role(
        name="test_role",
        description="テスト用ロール"
    )
    db_session.add(role)
    db_session.commit()
    return role

@pytest.fixture
def test_permission(db_session):
    """テスト用のパーミッションを作成"""
    permission = Permission(
        name="test_permission",
        description="テスト用パーミッション",
        resource="test_resource",
        action="read"
    )
    db_session.add(permission)
    db_session.commit()
    return permission

def test_password_hashing(auth_service):
    """パスワードハッシュ化のテスト"""
    password = "testpassword"
    hashed = auth_service.get_password_hash(password)
    
    # ハッシュ化されたパスワードは元のパスワードと異なる
    assert hashed != password
    
    # ハッシュ化されたパスワードの検証
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("wrongpassword", hashed)

def test_authenticate_user(auth_service, test_user):
    """ユーザー認証のテスト"""
    # 正しい認証情報
    user = auth_service.authenticate_user("testuser", "testpassword")
    assert user is not None
    assert user.username == "testuser"
    
    # 誤った認証情報
    user = auth_service.authenticate_user("testuser", "wrongpassword")
    assert user is None
    
    # 存在しないユーザー
    user = auth_service.authenticate_user("nonexistent", "testpassword")
    assert user is None

def test_create_access_token(auth_service, test_user):
    """アクセストークン作成のテスト"""
    token_data = auth_service.create_access_token(
        test_user,
        ip_address="127.0.0.1",
        user_agent="test-agent"
    )
    
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "expires_at" in token_data
    
    # トークンの検証
    user = auth_service.verify_token(token_data["access_token"])
    assert user is not None
    assert user.id == test_user.id

def test_verify_token(auth_service, test_user):
    """トークン検証のテスト"""
    # 有効なトークン
    token_data = auth_service.create_access_token(test_user)
    user = auth_service.verify_token(token_data["access_token"])
    assert user is not None
    assert user.id == test_user.id
    
    # 無効なトークン
    user = auth_service.verify_token("invalid_token")
    assert user is None

def test_check_permission(auth_service, test_user, test_role, test_permission):
    """権限チェックのテスト"""
    # ロールとパーミッションの関連付け
    test_role.permissions.append(test_permission)
    test_user.roles.append(test_role)
    
    # 権限がある場合
    assert auth_service.check_permission(test_user, "test_resource", "read")
    
    # 権限がない場合
    assert not auth_service.check_permission(test_user, "test_resource", "write")
    assert not auth_service.check_permission(test_user, "other_resource", "read")
    
    # スーパーユーザーは全ての権限を持つ
    test_user.is_superuser = True
    assert auth_service.check_permission(test_user, "any_resource", "any_action")

def test_invalidate_session(auth_service, test_user):
    """セッション無効化のテスト"""
    # セッションの作成
    token_data = auth_service.create_access_token(test_user)
    token = token_data["access_token"]
    
    # セッションの検証
    user = auth_service.verify_token(token)
    assert user is not None
    
    # セッションの無効化
    assert auth_service.invalidate_session(token)
    
    # 無効化されたセッションの検証
    user = auth_service.verify_token(token)
    assert user is None 
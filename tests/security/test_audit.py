"""
監査ログサービスのテスト
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.security.models import Base, User, AuditLog, AuditLogLevel, AuditLogCategory
from src.security.audit import AuditService, AuditError

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
def audit_service(db_session):
    """監査ログサービスのインスタンスを作成"""
    return AuditService(db=db_session)

@pytest.fixture
def test_user(db_session):
    """テスト用のユーザーを作成"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="dummy_hash",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_log_event(audit_service, test_user):
    """基本的なログイベントの記録テスト"""
    log = audit_service.log_event(
        level=AuditLogLevel.INFO,
        category=AuditLogCategory.SYSTEM,
        action="test_action",
        status="success",
        user_id=test_user.id,
        resource="test_resource",
        ip_address="127.0.0.1",
        user_agent="test-agent",
        details={"key": "value"}
    )
    
    assert log.id is not None
    assert log.level == AuditLogLevel.INFO
    assert log.category == AuditLogCategory.SYSTEM
    assert log.action == "test_action"
    assert log.status == "success"
    assert log.user_id == test_user.id
    assert log.resource == "test_resource"
    assert log.ip_address == "127.0.0.1"
    assert log.user_agent == "test-agent"
    assert log.details == {"key": "value"}

def test_log_auth_event(audit_service, test_user):
    """認証イベントの記録テスト"""
    # 成功したログイン
    log = audit_service.log_auth_event(
        action="login",
        status="success",
        user_id=test_user.id,
        ip_address="127.0.0.1"
    )
    
    assert log.category == AuditLogCategory.AUTHENTICATION
    assert log.level == AuditLogLevel.INFO
    assert log.action == "login"
    assert log.status == "success"
    
    # 失敗したログイン
    log = audit_service.log_auth_event(
        action="login",
        status="failed",
        user_id=test_user.id,
        ip_address="127.0.0.1",
        error_message="Invalid password"
    )
    
    assert log.category == AuditLogCategory.AUTHENTICATION
    assert log.level == AuditLogLevel.ERROR
    assert log.action == "login"
    assert log.status == "failed"
    assert log.error_message == "Invalid password"

def test_log_access_event(audit_service, test_user):
    """アクセスイベントの記録テスト"""
    # 成功したアクセス
    log = audit_service.log_access_event(
        action="read",
        resource="user_profile",
        status="success",
        user_id=test_user.id,
        ip_address="127.0.0.1"
    )
    
    assert log.category == AuditLogCategory.AUTHORIZATION
    assert log.level == AuditLogLevel.INFO
    assert log.action == "read"
    assert log.resource == "user_profile"
    assert log.status == "success"
    
    # 失敗したアクセス
    log = audit_service.log_access_event(
        action="write",
        resource="user_profile",
        status="failed",
        user_id=test_user.id,
        ip_address="127.0.0.1",
        error_message="Permission denied"
    )
    
    assert log.category == AuditLogCategory.AUTHORIZATION
    assert log.level == AuditLogLevel.ERROR
    assert log.action == "write"
    assert log.resource == "user_profile"
    assert log.status == "failed"
    assert log.error_message == "Permission denied"

def test_get_logs(audit_service, test_user):
    """ログ検索のテスト"""
    # テストデータの作成
    audit_service.log_event(
        level=AuditLogLevel.INFO,
        category=AuditLogCategory.SYSTEM,
        action="action1",
        status="success",
        user_id=test_user.id
    )
    audit_service.log_event(
        level=AuditLogLevel.ERROR,
        category=AuditLogCategory.AUTHENTICATION,
        action="action2",
        status="failed",
        user_id=test_user.id
    )
    
    # 全てのログを取得
    logs = audit_service.get_logs()
    assert len(logs) == 2
    
    # レベルでフィルタリング
    logs = audit_service.get_logs(level=AuditLogLevel.ERROR)
    assert len(logs) == 1
    assert logs[0].level == AuditLogLevel.ERROR
    
    # カテゴリでフィルタリング
    logs = audit_service.get_logs(category=AuditLogCategory.SYSTEM)
    assert len(logs) == 1
    assert logs[0].category == AuditLogCategory.SYSTEM
    
    # ステータスでフィルタリング
    logs = audit_service.get_logs(status="failed")
    assert len(logs) == 1
    assert logs[0].status == "failed"

def test_get_user_activity_summary(audit_service, test_user):
    """ユーザーアクティビティサマリーのテスト"""
    # テストデータの作成
    audit_service.log_auth_event(
        action="login",
        status="success",
        user_id=test_user.id
    )
    audit_service.log_access_event(
        action="read",
        resource="profile",
        status="success",
        user_id=test_user.id
    )
    audit_service.log_access_event(
        action="write",
        resource="profile",
        status="failed",
        user_id=test_user.id,
        error_message="Permission denied"
    )
    
    # サマリーの取得
    summary = audit_service.get_user_activity_summary(test_user.id)
    
    assert summary["total_events"] == 3
    assert summary["successful_events"] == 2
    assert summary["failed_events"] == 1
    assert "authentication" in summary["categories"]
    assert "authorization" in summary["categories"]
    assert "profile" in summary["resources"]
    assert len(summary["recent_activities"]) == 3

def test_error_handling(audit_service):
    """エラー処理のテスト"""
    # 無効なデータベースセッション
    with pytest.raises(AuditError):
        audit_service.db = None
        audit_service.log_event(
            level=AuditLogLevel.INFO,
            category=AuditLogCategory.SYSTEM,
            action="test",
            status="success"
        ) 
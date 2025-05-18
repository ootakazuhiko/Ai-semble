"""
セキュリティ設定管理サービスのテスト
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.security.models import Base, User, SecuritySetting
from src.security.setting import SecuritySettingService, SecuritySettingError

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def setting_service(db_session):
    return SecuritySettingService(db=db_session)

@pytest.fixture
def test_user(db_session):
    user = User(
        username="settinguser",
        email="setting@example.com",
        password_hash="dummy_hash",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_set_and_get_setting(setting_service, test_user):
    # 新規作成
    setting = setting_service.set_setting(
        key="password_policy",
        value="min_length:8",
        updated_by=test_user.id,
        description="パスワードの最小長"
    )
    assert setting.key == "password_policy"
    assert setting.value == "min_length:8"
    assert setting.updated_by == test_user.id
    assert setting.description == "パスワードの最小長"

    # 取得
    fetched = setting_service.get_setting("password_policy")
    assert fetched is not None
    assert fetched.value == "min_length:8"

    # 更新
    updated = setting_service.set_setting(
        key="password_policy",
        value="min_length:12",
        updated_by=test_user.id
    )
    assert updated.value == "min_length:12"
    assert updated.updated_by == test_user.id

def test_list_settings(setting_service, test_user):
    setting_service.set_setting("a", "1", updated_by=test_user.id)
    setting_service.set_setting("b", "2", updated_by=test_user.id)
    all_settings = setting_service.list_settings()
    keys = [s.key for s in all_settings]
    assert "a" in keys and "b" in keys
    assert len(all_settings) >= 2

def test_validate_setting(setting_service):
    # 正常系
    assert setting_service.validate_setting("test_key", "test_value")
    # 異常系
    with pytest.raises(SecuritySettingError):
        setting_service.validate_setting("test_key", "") 
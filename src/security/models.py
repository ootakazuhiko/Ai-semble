"""
セキュリティ関連のデータモデル

ユーザー認証とRBAC（ロールベースアクセス制御）のためのデータモデルを定義します。
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, JSON, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.declarative import declared_attr
import enum

Base = declarative_base()

# ユーザーとロールの多対多関係を定義
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# ロールとパーミッションの多対多関係を定義
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class User(Base):
    """ユーザーモデル"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # リレーションシップ
    roles = relationship('Role', secondary=user_role, back_populates='users')
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.username}>"

class Role(Base):
    """ロールモデル"""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    users = relationship('User', secondary=user_role, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permission, back_populates='roles')

    def __repr__(self):
        return f"<Role {self.name}>"

class Permission(Base):
    """パーミッションモデル"""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    resource = Column(String(100), nullable=False)  # リソース（例：'user', 'task'）
    action = Column(String(50), nullable=False)     # アクション（例：'create', 'read', 'update', 'delete'）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    roles = relationship('Role', secondary=role_permission, back_populates='permissions')

    def __repr__(self):
        return f"<Permission {self.name}>"

class Session(Base):
    """セッションモデル"""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String(45))  # IPv6対応
    user_agent = Column(String(200))

    # リレーションシップ
    user = relationship('User', back_populates='sessions')

    def __repr__(self):
        return f"<Session {self.id} for User {self.user_id}>"

class AuditLogLevel(enum.Enum):
    """監査ログの重要度レベル"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditLogCategory(enum.Enum):
    """監査ログのカテゴリ"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION = "configuration"
    SYSTEM = "system"

class AuditLog(Base):
    """監査ログモデル"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(Enum(AuditLogLevel), nullable=False)
    category = Column(Enum(AuditLogCategory), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 匿名アクセスの場合はNULL
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)  # 追加の詳細情報をJSON形式で保存
    ip_address = Column(String(45))  # IPv6対応
    user_agent = Column(String(200))
    status = Column(String(50), nullable=False)  # 成功/失敗などの状態
    error_message = Column(String(500), nullable=True)  # エラーメッセージ（失敗時）

    # リレーションシップ
    user = relationship('User', backref='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.id} - {self.category.value} - {self.action}>"

    @classmethod
    def create_auth_log(cls, user_id: Optional[int], action: str, status: str, 
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                       details: Optional[dict] = None, error_message: Optional[str] = None) -> 'AuditLog':
        """認証関連のログを作成するヘルパーメソッド"""
        level = AuditLogLevel.ERROR if status == "failed" else AuditLogLevel.INFO
        return cls(
            level=level,
            category=AuditLogCategory.AUTHENTICATION,
            user_id=user_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            error_message=error_message
        )

    @classmethod
    def create_access_log(cls, user_id: int, action: str, resource: str, status: str,
                         ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                         details: Optional[dict] = None, error_message: Optional[str] = None) -> 'AuditLog':
        """アクセス制御関連のログを作成するヘルパーメソッド"""
        level = AuditLogLevel.ERROR if status == "failed" else AuditLogLevel.INFO
        return cls(
            level=level,
            category=AuditLogCategory.AUTHORIZATION,
            user_id=user_id,
            action=action,
            resource=resource,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            error_message=error_message
        )

class SecuritySetting(Base):
    """セキュリティ設定モデル"""
    __tablename__ = 'security_settings'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(1000), nullable=False)
    description = Column(String(300), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # 最終更新者

    updater = relationship('User', backref='updated_settings')

    def __repr__(self):
        return f"<SecuritySetting {self.key}={self.value}>" 
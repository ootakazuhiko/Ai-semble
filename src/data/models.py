"""
学習データ管理のデータモデル

このモジュールは、学習データセットとそのメタデータを管理するためのデータモデルを定義します。
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON, String, Text, Table
from sqlalchemy.orm import relationship

from ..security.models import Base, User


class DatasetStatus(str, Enum):
    """データセットの状態を表す列挙型"""
    DRAFT = "draft"  # 編集中
    VALIDATING = "validating"  # 検証中
    VALID = "valid"  # 検証済み
    INVALID = "invalid"  # 検証失敗
    ARCHIVED = "archived"  # アーカイブ済み


class Dataset(Base):
    """学習データセットを表すモデル"""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    status = Column(SQLEnum(DatasetStatus), nullable=False, default=DatasetStatus.DRAFT)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # リレーションシップ
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")
    metadata = relationship("Metadata", back_populates="dataset", uselist=False, cascade="all, delete-orphan")
    access_groups = relationship(
        "UserGroup",
        secondary="dataset_access_association",
        back_populates="dataset_access",
    )


class DatasetVersion(Base):
    """データセットのバージョンを表すモデル"""
    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    version = Column(String(50), nullable=False)  # 例: "1.0.0"
    storage_path = Column(String(1024), nullable=False)  # データファイルの保存パス
    file_hash = Column(String(64), nullable=False)  # ファイルのSHA-256ハッシュ
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quality_metrics = Column(JSON)  # データ品質指標

    # リレーションシップ
    dataset = relationship("Dataset", back_populates="versions")
    created_by = relationship("User")


class Metadata(Base):
    """データセットのメタデータを表すモデル"""
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, unique=True)
    schema = Column(JSON, nullable=False)  # データスキーマ定義
    statistics = Column(JSON)  # データ統計情報
    tags = Column(JSON)  # タグ情報
    custom_fields = Column(JSON)  # カスタムフィールド
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    dataset = relationship("Dataset", back_populates="metadata")


class QualityMetrics(Base):
    """データ品質指標を表すモデル"""
    __tablename__ = "quality_metrics"

    id = Column(Integer, primary_key=True)
    dataset_version_id = Column(Integer, ForeignKey("dataset_versions.id"), nullable=False)
    metrics_type = Column(String(50), nullable=False)  # 指標の種類（例: "completeness", "accuracy"）
    metrics_value = Column(JSON, nullable=False)  # 指標の値
    threshold = Column(JSON)  # 閾値
    status = Column(String(20), nullable=False)  # "pass", "fail", "warning"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    details = Column(JSON)  # 詳細情報

    # リレーションシップ
    dataset_version = relationship("DatasetVersion")


# ユーザーグループの関連テーブル
user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("user_groups.id"), primary_key=True),
)

# データセットアクセス権限の関連テーブル
dataset_access_association = Table(
    "dataset_access_association",
    Base.metadata,
    Column("dataset_id", Integer, ForeignKey("datasets.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("user_groups.id"), primary_key=True),
    Column("access_level", SQLEnum("read", "write", "admin", name="access_level_enum"), nullable=False),
)


class UserGroup(Base):
    """ユーザーグループを表すモデル"""
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # リレーションシップ
    created_by = relationship("User", foreign_keys=[created_by_id])
    users = relationship("User", secondary=user_group_association, back_populates="groups")
    dataset_access = relationship(
        "Dataset",
        secondary=dataset_access_association,
        back_populates="access_groups",
    )


# Userモデルにgroupsリレーションシップを追加
User.groups = relationship("UserGroup", secondary=user_group_association, back_populates="users")

# Datasetモデルにaccess_groupsリレーションシップを追加
Dataset.access_groups = relationship(
    "UserGroup",
    secondary=dataset_access_association,
    back_populates="dataset_access",
)


class AccessLevel(str, Enum):
    """アクセス権限レベルを表す列挙型"""
    READ = "read"  # 読み取り専用
    WRITE = "write"  # 読み書き可能
    ADMIN = "admin"  # 管理者権限


class DatasetAccess(Base):
    """データセットのアクセス権限を表すモデル"""
    __tablename__ = "dataset_access"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("user_groups.id"), nullable=False)
    access_level = Column(SQLEnum(AccessLevel), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # リレーションシップ
    dataset = relationship("Dataset", back_populates="access_controls")
    group = relationship("UserGroup")
    created_by = relationship("User", foreign_keys=[created_by_id])


# Datasetモデルにaccess_controlsリレーションシップを追加
Dataset.access_controls = relationship("DatasetAccess", back_populates="dataset", cascade="all, delete-orphan") 
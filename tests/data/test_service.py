"""
データセット管理サービスのテスト

このモジュールは、データセット管理サービスと検証サービスのテストを提供します。
"""

import os
import tempfile
import tarfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.data.models import Dataset, DatasetStatus, DatasetVersion, Metadata, QualityMetrics
from src.data.service import DatasetError, DatasetService, ValidationError, ValidationService
from src.security.models import Base, User


@pytest.fixture
def db_session():
    """テスト用のデータベースセッションを作成"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # テスト用のユーザーを作成
    user = User(username="testuser", email="test@example.com")
    session.add(user)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def storage_dir():
    """テスト用のストレージディレクトリを作成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def dataset_service(db_session, storage_dir):
    """データセット管理サービスのインスタンスを作成"""
    return DatasetService(db_session, storage_dir)


@pytest.fixture
def validation_service(db_session):
    """検証サービスのインスタンスを作成"""
    return ValidationService(db_session)


@pytest.fixture
def sample_dataset(dataset_service, db_session):
    """サンプルデータセットを作成"""
    user = db_session.query(User).first()
    return dataset_service.create_dataset(
        name="test_dataset",
        description="テスト用データセット",
        created_by_id=user.id,
        schema={"type": "object", "properties": {"value": {"type": "number"}}},
        tags=["test", "sample"],
    )


@pytest.fixture
def sample_file():
    """サンプルデータファイルを作成"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"value": 42}\n{"value": 43}')
    yield Path(f.name)
    os.unlink(f.name)


def test_create_dataset(dataset_service, db_session):
    """データセット作成のテスト"""
    user = db_session.query(User).first()
    dataset = dataset_service.create_dataset(
        name="new_dataset",
        description="新しいデータセット",
        created_by_id=user.id,
        schema={"type": "object"},
    )

    assert dataset.name == "new_dataset"
    assert dataset.description == "新しいデータセット"
    assert dataset.status == DatasetStatus.DRAFT
    assert dataset.created_by_id == user.id
    assert dataset.metadata is not None
    assert dataset.metadata.schema == {"type": "object"}


def test_create_duplicate_dataset(dataset_service, sample_dataset):
    """重複データセット作成のテスト"""
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.create_dataset(
            name="test_dataset",  # 既存の名前
            description="重複データセット",
            created_by_id=sample_dataset.created_by_id,
            schema={},
        )
    assert "既に使用されています" in str(exc_info.value)


def test_add_version(dataset_service, sample_dataset, sample_file, db_session):
    """バージョン追加のテスト"""
    user = db_session.query(User).first()
    version = dataset_service.add_version(
        dataset_id=sample_dataset.id,
        version="1.0.0",
        file_path=sample_file,
        created_by_id=user.id,
    )

    assert version.dataset_id == sample_dataset.id
    assert version.version == "1.0.0"
    assert version.file_hash is not None
    assert version.storage_path is not None
    assert Path(version.storage_path).exists()


def test_add_version_nonexistent_dataset(dataset_service, sample_file, db_session):
    """存在しないデータセットへのバージョン追加のテスト"""
    user = db_session.query(User).first()
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.add_version(
            dataset_id=999,  # 存在しないID
            version="1.0.0",
            file_path=sample_file,
            created_by_id=user.id,
        )
    assert "は存在しません" in str(exc_info.value)


def test_add_version_nonexistent_file(dataset_service, sample_dataset, db_session):
    """存在しないファイルのバージョン追加のテスト"""
    user = db_session.query(User).first()
    with pytest.raises(ValidationError) as exc_info:
        dataset_service.add_version(
            dataset_id=sample_dataset.id,
            version="1.0.0",
            file_path="nonexistent.json",
            created_by_id=user.id,
        )
    assert "が存在しません" in str(exc_info.value)


def test_update_dataset(dataset_service, sample_dataset, db_session):
    """データセット更新のテスト"""
    user = db_session.query(User).first()
    updated = dataset_service.update_dataset(
        dataset_id=sample_dataset.id,
        updated_by_id=user.id,
        description="更新された説明",
        status=DatasetStatus.VALID,
        tags=["updated"],
    )

    assert updated.description == "更新された説明"
    assert updated.status == DatasetStatus.VALID
    assert updated.updated_by_id == user.id
    assert updated.metadata.tags == ["updated"]


def test_validate_dataset_version(validation_service, db_session, sample_dataset):
    """データセットバージョン検証のテスト"""
    # バージョンを作成
    user = db_session.query(User).first()
    version = DatasetVersion(
        dataset_id=sample_dataset.id,
        version="1.0.0",
        storage_path="test.json",
        file_hash="test",
        created_by_id=user.id,
    )
    db_session.add(version)
    db_session.commit()

    # 検証を実行
    metrics = validation_service.validate_dataset_version(
        version_id=version.id,
        metrics_type="accuracy",
        metrics_value={"score": 0.95},
        threshold={"score": 0.9},
    )

    assert metrics.metrics_type == "accuracy"
    assert metrics.metrics_value == {"score": 0.95}
    assert metrics.status == "pass"
    assert sample_dataset.status == DatasetStatus.VALID


def test_validate_dataset_version_fail(validation_service, db_session, sample_dataset):
    """データセットバージョン検証失敗のテスト"""
    # バージョンを作成
    user = db_session.query(User).first()
    version = DatasetVersion(
        dataset_id=sample_dataset.id,
        version="1.0.0",
        storage_path="test.json",
        file_hash="test",
        created_by_id=user.id,
    )
    db_session.add(version)
    db_session.commit()

    # 検証を実行（閾値を下回る）
    metrics = validation_service.validate_dataset_version(
        version_id=version.id,
        metrics_type="accuracy",
        metrics_value={"score": 0.8},
        threshold={"score": 0.9},
    )

    assert metrics.status == "fail"
    assert sample_dataset.status == DatasetStatus.INVALID


def test_get_validation_history(validation_service, db_session, sample_dataset):
    """検証履歴取得のテスト"""
    # バージョンと検証結果を作成
    user = db_session.query(User).first()
    version = DatasetVersion(
        dataset_id=sample_dataset.id,
        version="1.0.0",
        storage_path="test.json",
        file_hash="test",
        created_by_id=user.id,
    )
    db_session.add(version)
    db_session.commit()

    # 複数の検証結果を追加
    validation_service.validate_dataset_version(
        version_id=version.id,
        metrics_type="accuracy",
        metrics_value={"score": 0.95},
    )
    validation_service.validate_dataset_version(
        version_id=version.id,
        metrics_type="precision",
        metrics_value={"score": 0.92},
    )

    # 履歴を取得
    history = validation_service.get_validation_history(sample_dataset.id)
    assert len(history) == 2
    assert history[0].metrics_type == "precision"
    assert history[1].metrics_type == "accuracy"

    # 特定の指標タイプでフィルタリング
    accuracy_history = validation_service.get_validation_history(
        sample_dataset.id, metrics_type="accuracy"
    )
    assert len(accuracy_history) == 1
    assert accuracy_history[0].metrics_type == "accuracy"


def test_export_dataset(dataset_service, sample_dataset, sample_file, db_session):
    """データセットエクスポートのテスト"""
    # バージョンを追加
    user = db_session.query(User).first()
    version = dataset_service.add_version(
        dataset_id=sample_dataset.id,
        version="1.0.0",
        file_path=sample_file,
        created_by_id=user.id,
    )

    # エクスポート
    export_path = dataset_service.export_dataset(
        dataset_id=sample_dataset.id,
        export_path="test_export.tar.gz",
    )

    assert export_path.exists()
    assert export_path.suffix == ".tar.gz"

    # エクスポートファイルを削除
    export_path.unlink()


def test_export_dataset_without_versions(dataset_service, sample_dataset):
    """バージョンなしでのデータセットエクスポートのテスト"""
    export_path = dataset_service.export_dataset(
        dataset_id=sample_dataset.id,
        export_path="test_export.tar.gz",
        include_versions=False,
    )

    assert export_path.exists()
    assert export_path.suffix == ".tar.gz"

    # エクスポートファイルを削除
    export_path.unlink()


def test_import_dataset(dataset_service, sample_dataset, sample_file, db_session):
    """データセットインポートのテスト"""
    # バージョンを追加してエクスポート
    user = db_session.query(User).first()
    version = dataset_service.add_version(
        dataset_id=sample_dataset.id,
        version="1.0.0",
        file_path=sample_file,
        created_by_id=user.id,
    )

    export_path = dataset_service.export_dataset(
        dataset_id=sample_dataset.id,
        export_path="test_export.tar.gz",
    )

    # インポート
    imported_dataset, imported_versions = dataset_service.import_dataset(
        import_path=export_path,
        created_by_id=user.id,
        name="imported_dataset",
    )

    assert imported_dataset.name == "imported_dataset"
    assert imported_dataset.description == sample_dataset.description
    assert imported_dataset.metadata.schema == sample_dataset.metadata.schema
    assert imported_dataset.metadata.tags == sample_dataset.metadata.tags
    assert len(imported_versions) == 1
    assert imported_versions[0].version == "1.0.0"
    assert imported_versions[0].file_hash == version.file_hash

    # エクスポートファイルを削除
    export_path.unlink()


def test_import_dataset_nonexistent_file(dataset_service, db_session):
    """存在しないファイルのインポートテスト"""
    user = db_session.query(User).first()
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.import_dataset(
            import_path="nonexistent.tar.gz",
            created_by_id=user.id,
        )
    assert "が存在しません" in str(exc_info.value)


def test_import_dataset_invalid_archive(dataset_service, db_session):
    """不正なアーカイブのインポートテスト"""
    user = db_session.query(User).first()
    
    # 不正なアーカイブファイルを作成
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
        f.write(b"invalid archive data")
    
    try:
        with pytest.raises(DatasetError) as exc_info:
            dataset_service.import_dataset(
                import_path=f.name,
                created_by_id=user.id,
            )
        assert "アーカイブの展開に失敗しました" in str(exc_info.value)
    finally:
        os.unlink(f.name)


def test_import_dataset_invalid_metadata(dataset_service, db_session):
    """不正なメタデータのインポートテスト"""
    user = db_session.query(User).first()
    
    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 不正なメタデータファイルを作成
        with open(tmpdir / "metadata.json", "w") as f:
            f.write("invalid json data")
        
        # アーカイブを作成
        archive_path = tmpdir / "test.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(tmpdir / "metadata.json", arcname="metadata.json")
        
        # インポートを試行
        with pytest.raises(DatasetError) as exc_info:
            dataset_service.import_dataset(
                import_path=archive_path,
                created_by_id=user.id,
            )
        assert "メタデータの読み込みに失敗しました" in str(exc_info.value) 
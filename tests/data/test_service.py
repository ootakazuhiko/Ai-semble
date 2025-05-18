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
from src.security.service import AccessControlService, AccessLevel


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
def access_control_service(db_session):
    """アクセス制御サービスのインスタンスを作成"""
    return AccessControlService(db_session)


@pytest.fixture
def sample_users(db_session):
    """テスト用のユーザーを作成"""
    users = []
    for i in range(3):
        user = User(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
        )
        db_session.add(user)
        users.append(user)
    db_session.commit()
    return users


@pytest.fixture
def sample_group(access_control_service, sample_users, db_session):
    """テスト用のユーザーグループを作成"""
    return access_control_service.create_user_group(
        name="test_group",
        description="テスト用グループ",
        created_by_id=sample_users[0].id,
        user_ids=[sample_users[0].id, sample_users[1].id],
    )


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


def test_compare_versions(dataset_service, sample_dataset, db_session):
    """バージョン比較のテスト"""
    user = db_session.query(User).first()

    # 2つのバージョンのデータファイルを作成
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f1:
        f1.write('{"value": 42}\n{"value": 43}')
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
        f2.write('{"value": 42}\n{"value": 44}')  # 値を変更

    try:
        # バージョンを追加
        version1 = dataset_service.add_version(
            dataset_id=sample_dataset.id,
            version="1.0.0",
            file_path=f1.name,
            created_by_id=user.id,
            quality_metrics={"accuracy": 0.95},
        )

        # メタデータを更新
        dataset_service.update_dataset(
            dataset_id=sample_dataset.id,
            updated_by_id=user.id,
            tags=["updated"],
        )

        version2 = dataset_service.add_version(
            dataset_id=sample_dataset.id,
            version="1.0.1",
            file_path=f2.name,
            created_by_id=user.id,
            quality_metrics={"accuracy": 0.98},
        )

        # バージョンを比較
        diff = dataset_service.compare_versions(
            dataset_id=sample_dataset.id,
            version1="1.0.0",
            version2="1.0.1",
        )

        assert diff["dataset_id"] == sample_dataset.id
        assert diff["version1"] == "1.0.0"
        assert diff["version2"] == "1.0.1"
        assert "file_diff" in diff
        assert "metadata_diff" in diff
        assert "metrics_diff" in diff
        assert "accuracy" in diff["metrics_diff"]
        assert diff["metrics_diff"]["accuracy"]["from"] == 0.95
        assert diff["metrics_diff"]["accuracy"]["to"] == 0.98

    finally:
        os.unlink(f1.name)
        os.unlink(f2.name)


def test_compare_nonexistent_versions(dataset_service, sample_dataset):
    """存在しないバージョンの比較テスト"""
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.compare_versions(
            dataset_id=sample_dataset.id,
            version1="nonexistent",
            version2="1.0.0",
        )
    assert "指定されたバージョンが存在しません" in str(exc_info.value)


def test_get_version_history(dataset_service, sample_dataset, db_session):
    """バージョン履歴取得のテスト"""
    user = db_session.query(User).first()

    # 複数のバージョンを追加
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"value": 42}')
        try:
            version1 = dataset_service.add_version(
                dataset_id=sample_dataset.id,
                version="1.0.0",
                file_path=f.name,
                created_by_id=user.id,
                quality_metrics={"accuracy": 0.95},
            )

            # メタデータを更新
            dataset_service.update_dataset(
                dataset_id=sample_dataset.id,
                updated_by_id=user.id,
                tags=["updated"],
            )

            version2 = dataset_service.add_version(
                dataset_id=sample_dataset.id,
                version="1.0.1",
                file_path=f.name,
                created_by_id=user.id,
                quality_metrics={"accuracy": 0.98},
            )

            # 履歴を取得
            history = dataset_service.get_version_history(
                dataset_id=sample_dataset.id,
                include_metadata=True,
                include_metrics=True,
            )

            assert len(history) == 2
            assert history[0]["version"] == "1.0.0"
            assert history[1]["version"] == "1.0.1"
            assert "metadata" in history[0]
            assert "quality_metrics" in history[0]
            assert history[0]["quality_metrics"]["accuracy"] == 0.95
            assert history[1]["quality_metrics"]["accuracy"] == 0.98

        finally:
            os.unlink(f.name)


def test_get_version_history_nonexistent_dataset(dataset_service):
    """存在しないデータセットの履歴取得テスト"""
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.get_version_history(dataset_id=999)
    assert "データセットID 999 は存在しません" in str(exc_info.value)


def test_calculate_statistics(dataset_service, sample_dataset, db_session):
    """統計情報計算のテスト"""
    user = db_session.query(User).first()

    # テスト用のデータファイルを作成
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        # 数値型とカテゴリカル型のカラムを含むデータを作成
        f.write('{"numeric": 1, "category": "A"}\n')
        f.write('{"numeric": 2, "category": "B"}\n')
        f.write('{"numeric": 3, "category": "A"}\n')
        f.write('{"numeric": 4, "category": "C"}\n')
        f.write('{"numeric": 5, "category": "B"}\n')

    try:
        # バージョンを追加
        version = dataset_service.add_version(
            dataset_id=sample_dataset.id,
            version="1.0.0",
            file_path=f.name,
            created_by_id=user.id,
        )

        # 統計情報を計算
        stats = dataset_service.calculate_statistics(
            dataset_id=sample_dataset.id,
            version="1.0.0",
        )

        # 基本統計量の検証
        assert stats["statistics"]["row_count"] == 5
        assert stats["statistics"]["column_count"] == 2
        assert "numeric" in stats["statistics"]["numeric_statistics"]
        assert "category" in stats["statistics"]["categorical_statistics"]

        # 数値型カラムの統計量の検証
        numeric_stats = stats["statistics"]["numeric_statistics"]["numeric"]
        assert numeric_stats["mean"] == 3.0
        assert numeric_stats["min"] == 1.0
        assert numeric_stats["max"] == 5.0

        # カテゴリカルカラムの統計量の検証
        categorical_stats = stats["statistics"]["categorical_statistics"]["category"]
        assert categorical_stats["unique_count"] == 3
        assert "A" in categorical_stats["most_common"]
        assert "B" in categorical_stats["most_common"]

        # 品質指標の検証
        assert "completeness" in stats["quality_metrics"]
        assert "uniqueness" in stats["quality_metrics"]
        assert stats["quality_metrics"]["completeness"]["overall"] == 1.0

    finally:
        os.unlink(f.name)


def test_calculate_statistics_with_missing_values(dataset_service, sample_dataset, db_session):
    """欠損値を含むデータの統計情報計算のテスト"""
    user = db_session.query(User).first()

    # 欠損値を含むテストデータを作成
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"numeric": 1, "category": "A"}\n')
        f.write('{"numeric": null, "category": "B"}\n')
        f.write('{"numeric": 3, "category": null}\n')
        f.write('{"numeric": 4, "category": "C"}\n')
        f.write('{"numeric": 5, "category": "B"}\n')

    try:
        # バージョンを追加
        version = dataset_service.add_version(
            dataset_id=sample_dataset.id,
            version="1.0.0",
            file_path=f.name,
            created_by_id=user.id,
        )

        # 統計情報を計算
        stats = dataset_service.calculate_statistics(
            dataset_id=sample_dataset.id,
            version="1.0.0",
        )

        # 欠損値の検証
        assert stats["statistics"]["missing_values"]["numeric"] == 1
        assert stats["statistics"]["missing_values"]["category"] == 1

        # 品質指標の検証
        assert stats["quality_metrics"]["completeness"]["overall"] < 1.0
        assert "numeric" in stats["quality_metrics"]["completeness"]["by_column"]
        assert "category" in stats["quality_metrics"]["completeness"]["by_column"]

    finally:
        os.unlink(f.name)


def test_get_statistics(dataset_service, sample_dataset, db_session):
    """統計情報取得のテスト"""
    user = db_session.query(User).first()

    # テストデータを作成
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"numeric": 1, "category": "A"}\n')
        f.write('{"numeric": 2, "category": "B"}\n')

    try:
        # バージョンを追加
        version = dataset_service.add_version(
            dataset_id=sample_dataset.id,
            version="1.0.0",
            file_path=f.name,
            created_by_id=user.id,
        )

        # 初回の統計情報取得（計算が実行される）
        stats1 = dataset_service.get_statistics(
            dataset_id=sample_dataset.id,
            version="1.0.0",
        )

        # 2回目の統計情報取得（キャッシュから取得）
        stats2 = dataset_service.get_statistics(
            dataset_id=sample_dataset.id,
            version="1.0.0",
        )

        # 結果が一致することを確認
        assert stats1 == stats2

        # 再計算を強制
        stats3 = dataset_service.get_statistics(
            dataset_id=sample_dataset.id,
            version="1.0.0",
            recalculate=True,
        )

        # 結果が一致することを確認
        assert stats1 == stats3

    finally:
        os.unlink(f.name)


def test_get_statistics_nonexistent_dataset(dataset_service):
    """存在しないデータセットの統計情報取得テスト"""
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.get_statistics(dataset_id=999)
    assert "データセットID 999 は存在しません" in str(exc_info.value)


def test_get_statistics_nonexistent_version(dataset_service, sample_dataset):
    """存在しないバージョンの統計情報取得テスト"""
    with pytest.raises(DatasetError) as exc_info:
        dataset_service.get_statistics(
            dataset_id=sample_dataset.id,
            version="nonexistent",
        )
    assert "指定されたバージョンが存在しません" in str(exc_info.value) 
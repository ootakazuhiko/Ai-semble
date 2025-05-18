"""
データセット可視化サービスのテスト

このモジュールは、データセット可視化サービスのテストを提供します。
"""

import os
import tempfile
from pathlib import Path
import pytest
from sqlalchemy.orm import Session

from src.data.service import DatasetService
from src.data.visualization import VisualizationService
from src.data.models import DatasetStatus


@pytest.fixture
def visualization_service(db_session, dataset_service):
    """可視化サービスのインスタンスを作成"""
    return VisualizationService(db_session, dataset_service)


@pytest.fixture
def sample_dataset_with_versions(dataset_service, db_session):
    """テスト用のデータセットとバージョンを作成"""
    user = db_session.query(User).first()

    # データセットを作成
    dataset = dataset_service.create_dataset(
        name="test_dataset",
        description="テスト用データセット",
        created_by_id=user.id,
        schema={
            "type": "object",
            "properties": {
                "numeric": {"type": "number"},
                "category": {"type": "string"},
            },
        },
        tags=["test", "visualization"],
    )

    # バージョン1のデータを作成
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write('{"numeric": 1, "category": "A"}\n')
        f.write('{"numeric": 2, "category": "B"}\n')
        f.write('{"numeric": 3, "category": "A"}\n')
        f.write('{"numeric": 4, "category": "C"}\n')
        f.write('{"numeric": 5, "category": "B"}\n')

    try:
        # バージョン1を追加
        version1 = dataset_service.add_version(
            dataset_id=dataset.id,
            version="1.0.0",
            file_path=f.name,
            created_by_id=user.id,
        )

        # バージョン2のデータを作成（一部の値を変更）
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f2:
            f2.write('{"numeric": 1, "category": "A"}\n')
            f2.write('{"numeric": 2, "category": "B"}\n')
            f2.write('{"numeric": 3, "category": "A"}\n')
            f2.write('{"numeric": 6, "category": "D"}\n')  # 値を変更
            f2.write('{"numeric": 7, "category": "E"}\n')  # 値を変更

        try:
            # バージョン2を追加
            version2 = dataset_service.add_version(
                dataset_id=dataset.id,
                version="1.0.1",
                file_path=f2.name,
                created_by_id=user.id,
            )

            return dataset, version1, version2

        finally:
            os.unlink(f2.name)

    finally:
        os.unlink(f.name)


def test_create_statistics_dashboard(visualization_service, sample_dataset_with_versions):
    """統計情報ダッシュボード作成のテスト"""
    dataset, version1, _ = sample_dataset_with_versions

    # ダッシュボードを作成
    result = visualization_service.create_statistics_dashboard(
        dataset_id=dataset.id,
        version="1.0.0",
    )

    # 結果の検証
    assert "figure" in result
    figure = result["figure"]
    assert "data" in figure
    assert "layout" in figure
    assert figure["layout"]["title"]["text"] == f"データセット統計ダッシュボード: {dataset.name}"

    # 出力ファイルの作成をテスト
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        try:
            result = visualization_service.create_statistics_dashboard(
                dataset_id=dataset.id,
                version="1.0.0",
                output_path=f.name,
            )
            assert "output_path" in result
            assert Path(result["output_path"]).exists()
        finally:
            os.unlink(f.name)


def test_create_version_comparison_dashboard(
    visualization_service,
    sample_dataset_with_versions,
):
    """バージョン比較ダッシュボード作成のテスト"""
    dataset, version1, version2 = sample_dataset_with_versions

    # ダッシュボードを作成
    result = visualization_service.create_version_comparison_dashboard(
        dataset_id=dataset.id,
        version1="1.0.0",
        version2="1.0.1",
    )

    # 結果の検証
    assert "figure" in result
    figure = result["figure"]
    assert "data" in figure
    assert "layout" in figure
    assert figure["layout"]["title"]["text"] == f"バージョン比較ダッシュボード: {dataset.name}"

    # 出力ファイルの作成をテスト
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        try:
            result = visualization_service.create_version_comparison_dashboard(
                dataset_id=dataset.id,
                version1="1.0.0",
                version2="1.0.1",
                output_path=f.name,
            )
            assert "output_path" in result
            assert Path(result["output_path"]).exists()
        finally:
            os.unlink(f.name)


def test_create_quality_metrics_dashboard(
    visualization_service,
    sample_dataset_with_versions,
):
    """品質指標ダッシュボード作成のテスト"""
    dataset, version1, version2 = sample_dataset_with_versions

    # ダッシュボードを作成
    result = visualization_service.create_quality_metrics_dashboard(
        dataset_id=dataset.id,
    )

    # 結果の検証
    assert "figure" in result
    figure = result["figure"]
    assert "data" in figure
    assert "layout" in figure
    assert figure["layout"]["title"]["text"] == f"データ品質指標ダッシュボード: {dataset.name}"

    # 出力ファイルの作成をテスト
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        try:
            result = visualization_service.create_quality_metrics_dashboard(
                dataset_id=dataset.id,
                output_path=f.name,
            )
            assert "output_path" in result
            assert Path(result["output_path"]).exists()
        finally:
            os.unlink(f.name)


def test_create_statistics_dashboard_nonexistent_dataset(visualization_service):
    """存在しないデータセットの統計情報ダッシュボード作成のテスト"""
    with pytest.raises(DatasetError) as exc_info:
        visualization_service.create_statistics_dashboard(dataset_id=999)
    assert "データセットID 999 は存在しません" in str(exc_info.value)


def test_create_version_comparison_dashboard_nonexistent_version(
    visualization_service,
    sample_dataset_with_versions,
):
    """存在しないバージョンの比較ダッシュボード作成のテスト"""
    dataset, _, _ = sample_dataset_with_versions
    with pytest.raises(DatasetError) as exc_info:
        visualization_service.create_version_comparison_dashboard(
            dataset_id=dataset.id,
            version1="nonexistent",
            version2="1.0.0",
        )
    assert "指定されたバージョンが存在しません" in str(exc_info.value)


def test_create_quality_metrics_dashboard_nonexistent_dataset(visualization_service):
    """存在しないデータセットの品質指標ダッシュボード作成のテスト"""
    with pytest.raises(DatasetError) as exc_info:
        visualization_service.create_quality_metrics_dashboard(dataset_id=999)
    assert "データセットID 999 は存在しません" in str(exc_info.value) 
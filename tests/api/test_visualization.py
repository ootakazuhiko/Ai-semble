"""
データセット可視化機能のAPIエンドポイントのテスト

このモジュールは、データセット可視化機能のAPIエンドポイントのテストを提供します。
"""

import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.visualization import router
from src.data.service import DatasetService
from src.data.visualization import VisualizationService
from src.models import User
from tests.conftest import create_test_app, get_test_db


@pytest.fixture
def client(db_session):
    """テスト用のFastAPIクライアントを作成"""
    app = create_test_app()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def auth_headers(test_user, client):
    """認証済みのリクエストヘッダーを作成"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpassword"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_dataset_with_versions(db_session, test_user):
    """テスト用のデータセットとバージョンを作成"""
    dataset_service = DatasetService(db_session)

    # データセットを作成
    dataset = dataset_service.create_dataset(
        name="test_dataset",
        description="テスト用データセット",
        created_by_id=test_user.id,
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
            created_by_id=test_user.id,
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
                created_by_id=test_user.id,
            )

            return dataset, version1, version2

        finally:
            os.unlink(f2.name)

    finally:
        os.unlink(f.name)


def test_get_statistics_dashboard(client, auth_headers, sample_dataset_with_versions):
    """統計情報ダッシュボード取得のテスト"""
    dataset, version1, _ = sample_dataset_with_versions

    # JSON形式で取得
    response = client.get(
        f"/api/v1/visualization/datasets/{dataset.id}/statistics",
        params={"version": "1.0.0"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "figure" in data
    assert "data" in data["figure"]
    assert "layout" in data["figure"]

    # HTML形式で取得
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        try:
            response = client.get(
                f"/api/v1/visualization/datasets/{dataset.id}/statistics",
                params={
                    "version": "1.0.0",
                    "output_format": "html",
                    "output_path": f.name,
                },
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert "output_path" in data
            assert Path(data["output_path"]).exists()
        finally:
            os.unlink(f.name)


def test_get_version_comparison_dashboard(
    client,
    auth_headers,
    sample_dataset_with_versions,
):
    """バージョン比較ダッシュボード取得のテスト"""
    dataset, version1, version2 = sample_dataset_with_versions

    # JSON形式で取得
    response = client.get(
        f"/api/v1/visualization/datasets/{dataset.id}/version-comparison",
        params={"version1": "1.0.0", "version2": "1.0.1"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "figure" in data
    assert "data" in data["figure"]
    assert "layout" in data["figure"]

    # HTML形式で取得
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        try:
            response = client.get(
                f"/api/v1/visualization/datasets/{dataset.id}/version-comparison",
                params={
                    "version1": "1.0.0",
                    "version2": "1.0.1",
                    "output_format": "html",
                    "output_path": f.name,
                },
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert "output_path" in data
            assert Path(data["output_path"]).exists()
        finally:
            os.unlink(f.name)


def test_get_quality_metrics_dashboard(
    client,
    auth_headers,
    sample_dataset_with_versions,
):
    """品質指標ダッシュボード取得のテスト"""
    dataset, version1, version2 = sample_dataset_with_versions

    # JSON形式で取得
    response = client.get(
        f"/api/v1/visualization/datasets/{dataset.id}/quality-metrics",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "figure" in data
    assert "data" in data["figure"]
    assert "layout" in data["figure"]

    # HTML形式で取得
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        try:
            response = client.get(
                f"/api/v1/visualization/datasets/{dataset.id}/quality-metrics",
                params={
                    "output_format": "html",
                    "output_path": f.name,
                },
                headers=auth_headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert "output_path" in data
            assert Path(data["output_path"]).exists()
        finally:
            os.unlink(f.name)


def test_refresh_statistics(client, auth_headers, sample_dataset_with_versions):
    """統計情報の再計算のテスト"""
    dataset, version1, _ = sample_dataset_with_versions

    response = client.post(
        f"/api/v1/visualization/datasets/{dataset.id}/statistics/refresh",
        params={"version": "1.0.0"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "statistics" in data
    assert "quality_metrics" in data


def test_get_statistics_dashboard_nonexistent_dataset(client, auth_headers):
    """存在しないデータセットの統計情報ダッシュボード取得のテスト"""
    response = client.get(
        "/api/v1/visualization/datasets/999/statistics",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "データセットID 999 は存在しません" in response.json()["detail"]


def test_get_version_comparison_dashboard_nonexistent_version(
    client,
    auth_headers,
    sample_dataset_with_versions,
):
    """存在しないバージョンの比較ダッシュボード取得のテスト"""
    dataset, _, _ = sample_dataset_with_versions

    response = client.get(
        f"/api/v1/visualization/datasets/{dataset.id}/version-comparison",
        params={"version1": "nonexistent", "version2": "1.0.0"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "指定されたバージョンが存在しません" in response.json()["detail"]


def test_get_quality_metrics_dashboard_nonexistent_dataset(client, auth_headers):
    """存在しないデータセットの品質指標ダッシュボード取得のテスト"""
    response = client.get(
        "/api/v1/visualization/datasets/999/quality-metrics",
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "データセットID 999 は存在しません" in response.json()["detail"]


def test_get_statistics_dashboard_unauthorized(client, sample_dataset_with_versions):
    """認証なしでの統計情報ダッシュボード取得のテスト"""
    dataset, _, _ = sample_dataset_with_versions

    response = client.get(
        f"/api/v1/visualization/datasets/{dataset.id}/statistics",
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"] 
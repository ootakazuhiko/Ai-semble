"""
データセット可視化機能のAPIエンドポイント

このモジュールは、データセットの可視化機能を提供するAPIエンドポイントを定義します。
"""

from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..data.visualization import VisualizationService
from ..data.service import DatasetService
from ..security.auth import get_current_user
from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api/v1/visualization", tags=["visualization"])


def get_visualization_service(db: Session = Depends(get_db)) -> VisualizationService:
    """可視化サービスのインスタンスを取得"""
    return VisualizationService(db, DatasetService(db))


@router.get("/datasets/{dataset_id}/statistics")
async def get_statistics_dashboard(
    dataset_id: int,
    version: Optional[str] = None,
    output_format: str = Query("json", enum=["json", "html"]),
    output_path: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service),
) -> Dict[str, Any]:
    """
    データセットの統計情報ダッシュボードを取得

    Args:
        dataset_id: データセットID
        version: バージョン（指定しない場合は最新バージョン）
        output_format: 出力形式（json/html）
        output_path: 出力先のパス（指定しない場合はレスポンスとして返す）
        current_user: 現在のユーザー
        visualization_service: 可視化サービス

    Returns:
        ダッシュボードの情報（グラフのJSONデータまたは出力パス）

    Raises:
        HTTPException: データセットが存在しない場合、またはアクセス権限がない場合
    """
    try:
        if output_path:
            output_path = Path(output_path)
            if output_format == "html" and output_path.suffix != ".html":
                output_path = output_path.with_suffix(".html")
            elif output_format == "json" and output_path.suffix != ".json":
                output_path = output_path.with_suffix(".json")

        result = visualization_service.create_statistics_dashboard(
            dataset_id=dataset_id,
            version=version,
            output_path=output_path if output_path else None,
        )

        if output_path:
            return {"output_path": str(output_path)}
        else:
            return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/datasets/{dataset_id}/version-comparison")
async def get_version_comparison_dashboard(
    dataset_id: int,
    version1: str,
    version2: str,
    output_format: str = Query("json", enum=["json", "html"]),
    output_path: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service),
) -> Dict[str, Any]:
    """
    バージョン比較ダッシュボードを取得

    Args:
        dataset_id: データセットID
        version1: 比較元のバージョン
        version2: 比較先のバージョン
        output_format: 出力形式（json/html）
        output_path: 出力先のパス（指定しない場合はレスポンスとして返す）
        current_user: 現在のユーザー
        visualization_service: 可視化サービス

    Returns:
        ダッシュボードの情報（グラフのJSONデータまたは出力パス）

    Raises:
        HTTPException: データセットまたはバージョンが存在しない場合、またはアクセス権限がない場合
    """
    try:
        if output_path:
            output_path = Path(output_path)
            if output_format == "html" and output_path.suffix != ".html":
                output_path = output_path.with_suffix(".html")
            elif output_format == "json" and output_path.suffix != ".json":
                output_path = output_path.with_suffix(".json")

        result = visualization_service.create_version_comparison_dashboard(
            dataset_id=dataset_id,
            version1=version1,
            version2=version2,
            output_path=output_path if output_path else None,
        )

        if output_path:
            return {"output_path": str(output_path)}
        else:
            return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/datasets/{dataset_id}/quality-metrics")
async def get_quality_metrics_dashboard(
    dataset_id: int,
    output_format: str = Query("json", enum=["json", "html"]),
    output_path: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    visualization_service: VisualizationService = Depends(get_visualization_service),
) -> Dict[str, Any]:
    """
    データ品質指標ダッシュボードを取得

    Args:
        dataset_id: データセットID
        output_format: 出力形式（json/html）
        output_path: 出力先のパス（指定しない場合はレスポンスとして返す）
        current_user: 現在のユーザー
        visualization_service: 可視化サービス

    Returns:
        ダッシュボードの情報（グラフのJSONデータまたは出力パス）

    Raises:
        HTTPException: データセットが存在しない場合、またはアクセス権限がない場合
    """
    try:
        if output_path:
            output_path = Path(output_path)
            if output_format == "html" and output_path.suffix != ".html":
                output_path = output_path.with_suffix(".html")
            elif output_format == "json" and output_path.suffix != ".json":
                output_path = output_path.with_suffix(".json")

        result = visualization_service.create_quality_metrics_dashboard(
            dataset_id=dataset_id,
            output_path=output_path if output_path else None,
        )

        if output_path:
            return {"output_path": str(output_path)}
        else:
            return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/datasets/{dataset_id}/statistics/refresh")
async def refresh_statistics(
    dataset_id: int,
    version: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    dataset_service: DatasetService = Depends(lambda db: DatasetService(db)),
) -> Dict[str, Any]:
    """
    データセットの統計情報を再計算

    Args:
        dataset_id: データセットID
        version: バージョン（指定しない場合は最新バージョン）
        current_user: 現在のユーザー
        dataset_service: データセットサービス

    Returns:
        再計算された統計情報

    Raises:
        HTTPException: データセットが存在しない場合、またはアクセス権限がない場合
    """
    try:
        stats = dataset_service.get_statistics(dataset_id, version, force_recalculate=True)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
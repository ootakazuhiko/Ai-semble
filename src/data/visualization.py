"""
データセットの可視化機能を提供するモジュール

このモジュールは、データセットの統計情報や品質指標を可視化するための機能を提供します。
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy.orm import Session

from .models import Dataset, DatasetVersion
from .service import DatasetService, DatasetError


class VisualizationService:
    """データセット可視化サービス"""

    def __init__(self, db_session: Session, dataset_service: DatasetService):
        """
        初期化

        Args:
            db_session: データベースセッション
            dataset_service: データセット管理サービス
        """
        self.db = db_session
        self.dataset_service = dataset_service

    def create_statistics_dashboard(
        self,
        dataset_id: int,
        version: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        データセットの統計情報ダッシュボードを作成

        Args:
            dataset_id: データセットID
            version: バージョン（指定しない場合は最新バージョン）
            output_path: 出力先のパス（指定しない場合はHTMLとして返す）

        Returns:
            ダッシュボードの情報（グラフのJSONデータ）

        Raises:
            DatasetError: データセットまたはバージョンが存在しない場合
        """
        # 統計情報を取得
        stats = self.dataset_service.get_statistics(dataset_id, version)
        dataset = self.dataset_service.get_dataset(dataset_id)

        # サブプロットのレイアウトを作成
        n_plots = 0
        if "numeric_statistics" in stats["statistics"]:
            n_plots += len(stats["statistics"]["numeric_statistics"])
        if "categorical_statistics" in stats["statistics"]:
            n_plots += len(stats["statistics"]["categorical_statistics"])
        n_plots += 2  # 品質指標のグラフ

        fig = make_subplots(
            rows=n_plots,
            cols=1,
            subplot_titles=[
                *[f"{col}の分布" for col in stats["statistics"].get("numeric_statistics", {})],
                *[f"{col}の分布" for col in stats["statistics"].get("categorical_statistics", {})],
                "データ品質指標",
                "欠損値の分布",
            ],
            vertical_spacing=0.1,
        )

        # 数値型カラムの分布をプロット
        row = 1
        for col, col_stats in stats["statistics"].get("numeric_statistics", {}).items():
            # 箱ひげ図
            fig.add_trace(
                go.Box(
                    y=[col_stats["min"], col_stats["q1"], col_stats["median"],
                       col_stats["q3"], col_stats["max"]],
                    name=col,
                    boxpoints="all",
                ),
                row=row,
                col=1,
            )
            row += 1

        # カテゴリカルカラムの分布をプロット
        for col, col_stats in stats["statistics"].get("categorical_statistics", {}).items():
            # 棒グラフ
            categories = list(col_stats["most_common"].keys())
            counts = list(col_stats["most_common"].values())
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=counts,
                    name=col,
                ),
                row=row,
                col=1,
            )
            row += 1

        # 品質指標をプロット
        quality_metrics = stats["quality_metrics"]
        metrics_data = {
            "指標": ["完全性", "一意性"],
            "値": [
                quality_metrics["completeness"]["overall"],
                quality_metrics["uniqueness"]["overall"],
            ],
        }
        fig.add_trace(
            go.Bar(
                x=metrics_data["指標"],
                y=metrics_data["値"],
                name="品質指標",
            ),
            row=row,
            col=1,
        )
        row += 1

        # 欠損値の分布をプロット
        missing_values = stats["statistics"]["missing_values"]
        missing_data = {
            "カラム": list(missing_values.keys()),
            "欠損値数": list(missing_values.values()),
        }
        fig.add_trace(
            go.Bar(
                x=missing_data["カラム"],
                y=missing_data["欠損値数"],
                name="欠損値",
            ),
            row=row,
            col=1,
        )

        # レイアウトを更新
        fig.update_layout(
            title=f"データセット統計ダッシュボード: {dataset.name}",
            height=300 * n_plots,
            showlegend=False,
        )

        # 出力
        if output_path:
            output_path = Path(output_path)
            if output_path.suffix == ".html":
                fig.write_html(str(output_path))
            else:
                fig.write_json(str(output_path))
            return {"output_path": str(output_path)}
        else:
            return {"figure": json.loads(fig.to_json())}

    def create_version_comparison_dashboard(
        self,
        dataset_id: int,
        version1: str,
        version2: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        バージョン比較ダッシュボードを作成

        Args:
            dataset_id: データセットID
            version1: 比較元のバージョン
            version2: 比較先のバージョン
            output_path: 出力先のパス（指定しない場合はHTMLとして返す）

        Returns:
            ダッシュボードの情報（グラフのJSONデータ）

        Raises:
            DatasetError: データセットまたはバージョンが存在しない場合
        """
        # バージョンの統計情報を取得
        stats1 = self.dataset_service.get_statistics(dataset_id, version1)
        stats2 = self.dataset_service.get_statistics(dataset_id, version2)
        dataset = self.dataset_service.get_dataset(dataset_id)

        # サブプロットのレイアウトを作成
        n_plots = 2  # 品質指標の比較と欠損値の比較
        if "numeric_statistics" in stats1["statistics"]:
            n_plots += len(stats1["statistics"]["numeric_statistics"])
        if "categorical_statistics" in stats1["statistics"]:
            n_plots += len(stats1["statistics"]["categorical_statistics"])

        fig = make_subplots(
            rows=n_plots,
            cols=1,
            subplot_titles=[
                "品質指標の比較",
                "欠損値の比較",
                *[f"{col}の比較" for col in stats1["statistics"].get("numeric_statistics", {})],
                *[f"{col}の比較" for col in stats1["statistics"].get("categorical_statistics", {})],
            ],
            vertical_spacing=0.1,
        )

        # 品質指標の比較をプロット
        metrics_data = {
            "指標": ["完全性", "一意性"] * 2,
            "値": [
                stats1["quality_metrics"]["completeness"]["overall"],
                stats1["quality_metrics"]["uniqueness"]["overall"],
                stats2["quality_metrics"]["completeness"]["overall"],
                stats2["quality_metrics"]["uniqueness"]["overall"],
            ],
            "バージョン": [version1, version1, version2, version2],
        }
        fig.add_trace(
            go.Bar(
                x=metrics_data["指標"],
                y=metrics_data["値"],
                name="品質指標",
                text=metrics_data["バージョン"],
            ),
            row=1,
            col=1,
        )

        # 欠損値の比較をプロット
        missing_data = {
            "カラム": list(stats1["statistics"]["missing_values"].keys()) * 2,
            "欠損値数": [
                *list(stats1["statistics"]["missing_values"].values()),
                *list(stats2["statistics"]["missing_values"].values()),
            ],
            "バージョン": [version1] * len(stats1["statistics"]["missing_values"]) +
                        [version2] * len(stats2["statistics"]["missing_values"]),
        }
        fig.add_trace(
            go.Bar(
                x=missing_data["カラム"],
                y=missing_data["欠損値数"],
                name="欠損値",
                text=missing_data["バージョン"],
            ),
            row=2,
            col=1,
        )

        # 数値型カラムの比較をプロット
        row = 3
        for col in stats1["statistics"].get("numeric_statistics", {}):
            stats1_data = stats1["statistics"]["numeric_statistics"][col]
            stats2_data = stats2["statistics"]["numeric_statistics"][col]
            
            fig.add_trace(
                go.Box(
                    y=[stats1_data["min"], stats1_data["q1"], stats1_data["median"],
                       stats1_data["q3"], stats1_data["max"]],
                    name=f"{col} ({version1})",
                ),
                row=row,
                col=1,
            )
            fig.add_trace(
                go.Box(
                    y=[stats2_data["min"], stats2_data["q1"], stats2_data["median"],
                       stats2_data["q3"], stats2_data["max"]],
                    name=f"{col} ({version2})",
                ),
                row=row,
                col=1,
            )
            row += 1

        # カテゴリカルカラムの比較をプロット
        for col in stats1["statistics"].get("categorical_statistics", {}):
            stats1_data = stats1["statistics"]["categorical_statistics"][col]
            stats2_data = stats2["statistics"]["categorical_statistics"][col]
            
            categories = list(set(
                list(stats1_data["most_common"].keys()) +
                list(stats2_data["most_common"].keys())
            ))
            counts1 = [stats1_data["most_common"].get(cat, 0) for cat in categories]
            counts2 = [stats2_data["most_common"].get(cat, 0) for cat in categories]

            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=counts1,
                    name=f"{col} ({version1})",
                ),
                row=row,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=counts2,
                    name=f"{col} ({version2})",
                ),
                row=row,
                col=1,
            )
            row += 1

        # レイアウトを更新
        fig.update_layout(
            title=f"バージョン比較ダッシュボード: {dataset.name}",
            height=300 * n_plots,
            barmode="group",
            showlegend=True,
        )

        # 出力
        if output_path:
            output_path = Path(output_path)
            if output_path.suffix == ".html":
                fig.write_html(str(output_path))
            else:
                fig.write_json(str(output_path))
            return {"output_path": str(output_path)}
        else:
            return {"figure": json.loads(fig.to_json())}

    def create_quality_metrics_dashboard(
        self,
        dataset_id: int,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """
        データ品質指標ダッシュボードを作成

        Args:
            dataset_id: データセットID
            output_path: 出力先のパス（指定しない場合はHTMLとして返す）

        Returns:
            ダッシュボードの情報（グラフのJSONデータ）

        Raises:
            DatasetError: データセットが存在しない場合
        """
        # バージョン履歴を取得
        history = self.dataset_service.get_version_history(
            dataset_id,
            include_metrics=True,
        )
        dataset = self.dataset_service.get_dataset(dataset_id)

        # 品質指標の時系列データを準備
        versions = []
        completeness = []
        uniqueness = []
        for version_info in history:
            if "quality_metrics" in version_info:
                versions.append(version_info["version"])
                metrics = version_info["quality_metrics"]
                completeness.append(metrics["completeness"]["overall"])
                uniqueness.append(metrics["uniqueness"]["overall"])

        # サブプロットのレイアウトを作成
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=[
                "品質指標の推移",
                "カラム別の完全性指標",
            ],
            vertical_spacing=0.2,
        )

        # 品質指標の推移をプロット
        fig.add_trace(
            go.Scatter(
                x=versions,
                y=completeness,
                name="完全性",
                mode="lines+markers",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=versions,
                y=uniqueness,
                name="一意性",
                mode="lines+markers",
            ),
            row=1,
            col=1,
        )

        # 最新バージョンのカラム別完全性指標をプロット
        if history:
            latest_metrics = history[-1]["quality_metrics"]
            columns = list(latest_metrics["completeness"]["by_column"].keys())
            values = list(latest_metrics["completeness"]["by_column"].values())
            
            fig.add_trace(
                go.Bar(
                    x=columns,
                    y=values,
                    name="カラム別完全性",
                ),
                row=2,
                col=1,
            )

        # レイアウトを更新
        fig.update_layout(
            title=f"データ品質指標ダッシュボード: {dataset.name}",
            height=800,
            showlegend=True,
        )

        # 出力
        if output_path:
            output_path = Path(output_path)
            if output_path.suffix == ".html":
                fig.write_html(str(output_path))
            else:
                fig.write_json(str(output_path))
            return {"output_path": str(output_path)}
        else:
            return {"figure": json.loads(fig.to_json())} 
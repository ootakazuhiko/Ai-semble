"""
学習データ管理サービス

このモジュールは、データセットの管理と検証のためのサービスを提供します。
"""

import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from difflib import unified_diff
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from .models import Dataset, DatasetStatus, DatasetVersion, Metadata, QualityMetrics


class DatasetError(Exception):
    """データセット関連のエラーを表す例外クラス"""
    pass


class ValidationError(Exception):
    """データ検証関連のエラーを表す例外クラス"""
    pass


class DatasetService:
    """データセット管理サービス"""

    def __init__(self, db_session: Session, storage_base_path: Union[str, Path]):
        """
        初期化

        Args:
            db_session: データベースセッション
            storage_base_path: データファイルの保存ベースパス
        """
        self.db = db_session
        self.storage_base_path = Path(storage_base_path)
        self.storage_base_path.mkdir(parents=True, exist_ok=True)

    def create_dataset(
        self,
        name: str,
        description: str,
        created_by_id: int,
        schema: Dict,
        tags: Optional[List[str]] = None,
    ) -> Dataset:
        """
        新しいデータセットを作成

        Args:
            name: データセット名
            description: 説明
            created_by_id: 作成者ID
            schema: データスキーマ
            tags: タグリスト

        Returns:
            作成されたデータセット

        Raises:
            DatasetError: データセット名が重複している場合
        """
        if self.db.query(Dataset).filter(Dataset.name == name).first():
            raise DatasetError(f"データセット名 '{name}' は既に使用されています")

        dataset = Dataset(
            name=name,
            description=description,
            status=DatasetStatus.DRAFT,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
        )
        self.db.add(dataset)
        self.db.flush()  # IDを取得するためにフラッシュ

        # メタデータを作成
        metadata = Metadata(
            dataset_id=dataset.id,
            schema=schema,
            tags=tags or [],
            statistics={},
            custom_fields={},
        )
        self.db.add(metadata)
        self.db.commit()

        return dataset

    def add_version(
        self,
        dataset_id: int,
        version: str,
        file_path: Union[str, Path],
        created_by_id: int,
        quality_metrics: Optional[Dict] = None,
    ) -> DatasetVersion:
        """
        データセットに新しいバージョンを追加

        Args:
            dataset_id: データセットID
            version: バージョン番号
            file_path: データファイルのパス
            created_by_id: 作成者ID
            quality_metrics: 品質指標

        Returns:
            作成されたバージョン

        Raises:
            DatasetError: データセットが存在しない場合
            ValidationError: ファイルの検証に失敗した場合
        """
        dataset = self.db.query(Dataset).get(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        # ファイルを検証
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValidationError(f"ファイル {file_path} が存在しません")

        # ファイルをコピーしてハッシュを計算
        storage_path = self.storage_base_path / f"{dataset_id}" / f"{version}{file_path.suffix}"
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "rb") as src, open(storage_path, "wb") as dst:
            content = src.read()
            dst.write(content)
            file_hash = hashlib.sha256(content).hexdigest()

        # バージョンを作成
        version = DatasetVersion(
            dataset_id=dataset_id,
            version=version,
            storage_path=str(storage_path),
            file_hash=file_hash,
            created_by_id=created_by_id,
            quality_metrics=quality_metrics,
        )
        self.db.add(version)
        self.db.commit()

        return version

    def get_dataset(self, dataset_id: int) -> Optional[Dataset]:
        """データセットを取得"""
        return self.db.query(Dataset).get(dataset_id)

    def list_datasets(
        self,
        status: Optional[DatasetStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dataset]:
        """データセット一覧を取得"""
        query = self.db.query(Dataset)
        if status:
            query = query.filter(Dataset.status == status)
        if tags:
            query = query.join(Metadata).filter(Metadata.tags.contains(tags))
        return query.all()

    def update_dataset(
        self,
        dataset_id: int,
        updated_by_id: int,
        description: Optional[str] = None,
        status: Optional[DatasetStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> Dataset:
        """データセットを更新"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        if description is not None:
            dataset.description = description
        if status is not None:
            dataset.status = status
        dataset.updated_by_id = updated_by_id
        dataset.updated_at = datetime.utcnow()

        if tags is not None and dataset.metadata:
            dataset.metadata.tags = tags

        self.db.commit()
        return dataset

    def export_dataset(
        self,
        dataset_id: int,
        export_path: Union[str, Path],
        include_versions: bool = True,
        include_metrics: bool = True,
    ) -> Path:
        """
        データセットをエクスポート

        Args:
            dataset_id: データセットID
            export_path: エクスポート先のパス
            include_versions: バージョンデータを含めるかどうか
            include_metrics: 品質指標を含めるかどうか

        Returns:
            エクスポートされたファイルのパス

        Raises:
            DatasetError: データセットが存在しない場合
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        export_path = Path(export_path)
        if export_path.suffix != ".tar.gz":
            export_path = export_path.with_suffix(".tar.gz")

        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # メタデータをエクスポート
            metadata = {
                "dataset": {
                    "id": dataset.id,
                    "name": dataset.name,
                    "description": dataset.description,
                    "status": dataset.status.value,
                    "created_at": dataset.created_at.isoformat(),
                    "updated_at": dataset.updated_at.isoformat(),
                },
                "metadata": {
                    "schema": dataset.metadata.schema,
                    "statistics": dataset.metadata.statistics,
                    "tags": dataset.metadata.tags,
                    "custom_fields": dataset.metadata.custom_fields,
                }
            }

            # バージョン情報を含める場合
            if include_versions:
                metadata["versions"] = []
                for version in dataset.versions:
                    version_data = {
                        "version": version.version,
                        "created_at": version.created_at.isoformat(),
                        "file_hash": version.file_hash,
                    }
                    if include_metrics and version.quality_metrics:
                        version_data["quality_metrics"] = version.quality_metrics
                    metadata["versions"].append(version_data)

                    # データファイルをコピー
                    if version.storage_path:
                        src_path = Path(version.storage_path)
                        if src_path.exists():
                            dst_path = tmpdir / "versions" / f"{version.version}{src_path.suffix}"
                            dst_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src_path, dst_path)

            # メタデータを保存
            with open(tmpdir / "metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # アーカイブを作成
            with tarfile.open(export_path, "w:gz") as tar:
                tar.add(tmpdir, arcname="")

        return export_path

    def import_dataset(
        self,
        import_path: Union[str, Path],
        created_by_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Tuple[Dataset, List[DatasetVersion]]:
        """
        データセットをインポート

        Args:
            import_path: インポートするファイルのパス
            created_by_id: 作成者ID
            name: 新しいデータセット名（指定しない場合は元の名前を使用）
            description: 新しい説明（指定しない場合は元の説明を使用）

        Returns:
            (作成されたデータセット, 作成されたバージョンのリスト)

        Raises:
            DatasetError: インポートに失敗した場合
        """
        import_path = Path(import_path)
        if not import_path.exists():
            raise DatasetError(f"インポートファイル {import_path} が存在しません")

        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # アーカイブを展開
            try:
                with tarfile.open(import_path, "r:gz") as tar:
                    tar.extractall(tmpdir)
            except Exception as e:
                raise DatasetError(f"アーカイブの展開に失敗しました: {e}")

            # メタデータを読み込み
            try:
                with open(tmpdir / "metadata.json", "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception as e:
                raise DatasetError(f"メタデータの読み込みに失敗しました: {e}")

            # データセットを作成
            dataset = self.create_dataset(
                name=name or metadata["dataset"]["name"],
                description=description or metadata["dataset"]["description"],
                created_by_id=created_by_id,
                schema=metadata["metadata"]["schema"],
                tags=metadata["metadata"]["tags"],
            )

            # バージョンをインポート
            versions = []
            if "versions" in metadata:
                versions_dir = tmpdir / "versions"
                if versions_dir.exists():
                    for version_data in metadata["versions"]:
                        version = version_data["version"]
                        file_pattern = f"{version}.*"
                        matching_files = list(versions_dir.glob(file_pattern))
                        
                        if matching_files:
                            file_path = matching_files[0]
                            version = self.add_version(
                                dataset_id=dataset.id,
                                version=version,
                                file_path=file_path,
                                created_by_id=created_by_id,
                                quality_metrics=version_data.get("quality_metrics"),
                            )
                            versions.append(version)

            return dataset, versions

    def compare_versions(
        self,
        dataset_id: int,
        version1: str,
        version2: str,
        include_metadata: bool = True,
        include_metrics: bool = True,
    ) -> Dict[str, Any]:
        """
        2つのバージョン間の差分を比較

        Args:
            dataset_id: データセットID
            version1: 比較元のバージョン
            version2: 比較先のバージョン
            include_metadata: メタデータの差分を含めるかどうか
            include_metrics: 品質指標の差分を含めるかどうか

        Returns:
            差分情報を含む辞書

        Raises:
            DatasetError: データセットまたはバージョンが存在しない場合
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        # バージョンを取得
        v1 = self.db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version == version1,
        ).first()
        v2 = self.db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version == version2,
        ).first()

        if not v1 or not v2:
            raise DatasetError("指定されたバージョンが存在しません")

        # 差分情報を格納する辞書
        diff_info = {
            "dataset_id": dataset_id,
            "version1": version1,
            "version2": version2,
            "file_diff": None,
            "metadata_diff": None,
            "metrics_diff": None,
        }

        # ファイルの差分を比較
        if v1.storage_path and v2.storage_path:
            try:
                with open(v1.storage_path, "r", encoding="utf-8") as f1, \
                     open(v2.storage_path, "r", encoding="utf-8") as f2:
                    file1_lines = f1.readlines()
                    file2_lines = f2.readlines()
                    diff = list(unified_diff(
                        file1_lines,
                        file2_lines,
                        fromfile=f"version {version1}",
                        tofile=f"version {version2}",
                        lineterm="",
                    ))
                    if diff:
                        diff_info["file_diff"] = "".join(diff)
            except Exception as e:
                diff_info["file_diff"] = f"ファイルの差分比較中にエラーが発生しました: {e}"

        # メタデータの差分を比較
        if include_metadata:
            metadata_diff = {}
            for key in ["schema", "statistics", "tags", "custom_fields"]:
                v1_value = getattr(dataset.metadata, key)
                v2_value = getattr(dataset.metadata, key)
                if v1_value != v2_value:
                    metadata_diff[key] = {
                        "from": v1_value,
                        "to": v2_value,
                    }
            if metadata_diff:
                diff_info["metadata_diff"] = metadata_diff

        # 品質指標の差分を比較
        if include_metrics and v1.quality_metrics and v2.quality_metrics:
            metrics_diff = {}
            for key in set(v1.quality_metrics.keys()) | set(v2.quality_metrics.keys()):
                v1_value = v1.quality_metrics.get(key)
                v2_value = v2.quality_metrics.get(key)
                if v1_value != v2_value:
                    metrics_diff[key] = {
                        "from": v1_value,
                        "to": v2_value,
                    }
            if metrics_diff:
                diff_info["metrics_diff"] = metrics_diff

        return diff_info

    def get_version_history(
        self,
        dataset_id: int,
        include_metadata: bool = False,
        include_metrics: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        データセットのバージョン履歴を取得

        Args:
            dataset_id: データセットID
            include_metadata: メタデータを含めるかどうか
            include_metrics: 品質指標を含めるかどうか

        Returns:
            バージョン履歴のリスト

        Raises:
            DatasetError: データセットが存在しない場合
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        history = []
        for version in sorted(dataset.versions, key=lambda v: v.created_at):
            version_info = {
                "version": version.version,
                "created_at": version.created_at.isoformat(),
                "created_by": version.created_by.username,
                "file_hash": version.file_hash,
            }

            if include_metadata:
                version_info["metadata"] = {
                    "schema": dataset.metadata.schema,
                    "statistics": dataset.metadata.statistics,
                    "tags": dataset.metadata.tags,
                    "custom_fields": dataset.metadata.custom_fields,
                }

            if include_metrics and version.quality_metrics:
                version_info["quality_metrics"] = version.quality_metrics

            history.append(version_info)

        return history

    def calculate_statistics(
        self,
        dataset_id: int,
        version: Optional[str] = None,
        update_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        データセットの統計情報を計算

        Args:
            dataset_id: データセットID
            version: バージョン（指定しない場合は最新バージョン）
            update_metadata: メタデータを更新するかどうか

        Returns:
            計算された統計情報

        Raises:
            DatasetError: データセットまたはバージョンが存在しない場合
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        # バージョンを取得
        if version:
            dataset_version = self.db.query(DatasetVersion).filter(
                DatasetVersion.dataset_id == dataset_id,
                DatasetVersion.version == version,
            ).first()
        else:
            dataset_version = self.db.query(DatasetVersion).filter(
                DatasetVersion.dataset_id == dataset_id,
            ).order_by(DatasetVersion.created_at.desc()).first()

        if not dataset_version:
            raise DatasetError("指定されたバージョンが存在しません")

        # データファイルを読み込み
        try:
            df = pd.read_json(dataset_version.storage_path, lines=True)
        except Exception as e:
            raise DatasetError(f"データファイルの読み込みに失敗しました: {e}")

        # 基本統計量を計算
        statistics = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
        }

        # 数値型カラムの統計量
        numeric_stats = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            numeric_stats[col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "median": float(df[col].median()),
                "q1": float(df[col].quantile(0.25)),
                "q3": float(df[col].quantile(0.75)),
            }
        if numeric_stats:
            statistics["numeric_statistics"] = numeric_stats

        # カテゴリカルカラムの統計量
        categorical_stats = {}
        for col in df.select_dtypes(include=["object", "category"]).columns:
            value_counts = df[col].value_counts()
            categorical_stats[col] = {
                "unique_count": int(value_counts.nunique()),
                "most_common": value_counts.head(5).to_dict(),
                "missing_ratio": float(df[col].isnull().mean()),
            }
        if categorical_stats:
            statistics["categorical_statistics"] = categorical_stats

        # データ品質指標
        quality_metrics = {
            "completeness": {
                "overall": float(1 - df.isnull().mean().mean()),
                "by_column": (1 - df.isnull().mean()).to_dict(),
            },
            "uniqueness": {
                "overall": float(len(df.drop_duplicates()) / len(df)),
                "by_column": (df.nunique() / len(df)).to_dict(),
            },
        }

        # メタデータを更新
        if update_metadata and dataset.metadata:
            dataset.metadata.statistics = statistics
            self.db.commit()

        # 品質指標を更新
        dataset_version.quality_metrics = quality_metrics
        self.db.commit()

        return {
            "statistics": statistics,
            "quality_metrics": quality_metrics,
        }

    def get_statistics(
        self,
        dataset_id: int,
        version: Optional[str] = None,
        recalculate: bool = False,
    ) -> Dict[str, Any]:
        """
        データセットの統計情報を取得

        Args:
            dataset_id: データセットID
            version: バージョン（指定しない場合は最新バージョン）
            recalculate: 統計情報を再計算するかどうか

        Returns:
            統計情報

        Raises:
            DatasetError: データセットまたはバージョンが存在しない場合
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            raise DatasetError(f"データセットID {dataset_id} は存在しません")

        # バージョンを取得
        if version:
            dataset_version = self.db.query(DatasetVersion).filter(
                DatasetVersion.dataset_id == dataset_id,
                DatasetVersion.version == version,
            ).first()
        else:
            dataset_version = self.db.query(DatasetVersion).filter(
                DatasetVersion.dataset_id == dataset_id,
            ).order_by(DatasetVersion.created_at.desc()).first()

        if not dataset_version:
            raise DatasetError("指定されたバージョンが存在しません")

        # 統計情報を再計算するか、既存の情報を返す
        if recalculate or not dataset.metadata.statistics:
            return self.calculate_statistics(dataset_id, version, update_metadata=True)
        else:
            return {
                "statistics": dataset.metadata.statistics,
                "quality_metrics": dataset_version.quality_metrics,
            }


class ValidationService:
    """データ検証サービス"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def validate_dataset_version(
        self,
        version_id: int,
        metrics_type: str,
        metrics_value: Dict,
        threshold: Optional[Dict] = None,
    ) -> QualityMetrics:
        """
        データセットバージョンを検証

        Args:
            version_id: バージョンID
            metrics_type: 指標の種類
            metrics_value: 指標の値
            threshold: 閾値

        Returns:
            作成された品質指標

        Raises:
            ValidationError: バージョンが存在しない場合
        """
        version = self.db.query(DatasetVersion).get(version_id)
        if not version:
            raise ValidationError(f"バージョンID {version_id} は存在しません")

        # 閾値と比較してステータスを決定
        status = "pass"
        if threshold:
            for key, value in threshold.items():
                if key in metrics_value:
                    if metrics_value[key] < value:
                        status = "fail"
                        break

        metrics = QualityMetrics(
            dataset_version_id=version_id,
            metrics_type=metrics_type,
            metrics_value=metrics_value,
            threshold=threshold,
            status=status,
            details={},
        )
        self.db.add(metrics)
        self.db.commit()

        # データセットのステータスを更新
        if status == "fail":
            version.dataset.status = DatasetStatus.INVALID
        elif version.dataset.status == DatasetStatus.DRAFT:
            version.dataset.status = DatasetStatus.VALID
        self.db.commit()

        return metrics

    def get_validation_history(
        self,
        dataset_id: int,
        metrics_type: Optional[str] = None,
    ) -> List[QualityMetrics]:
        """検証履歴を取得"""
        query = self.db.query(QualityMetrics).join(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id
        )
        if metrics_type:
            query = query.filter(QualityMetrics.metrics_type == metrics_type)
        return query.order_by(QualityMetrics.created_at.desc()).all() 
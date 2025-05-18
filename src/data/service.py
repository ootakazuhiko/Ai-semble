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

from .models import (
    AccessLevel,
    Dataset,
    DatasetAccess,
    DatasetStatus,
    DatasetVersion,
    Metadata,
    QualityMetrics,
    UserGroup,
    User,
)


class DatasetError(Exception):
    """データセット関連のエラーを表す例外クラス"""
    pass


class ValidationError(Exception):
    """データ検証関連のエラーを表す例外クラス"""
    pass


class AccessControlError(Exception):
    """アクセス制御関連のエラーを表す例外クラス"""
    pass


class AccessControlService:
    """アクセス制御サービス"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_user_group(
        self,
        name: str,
        description: str,
        created_by_id: int,
        user_ids: Optional[List[int]] = None,
    ) -> UserGroup:
        """
        ユーザーグループを作成

        Args:
            name: グループ名
            description: 説明
            created_by_id: 作成者ID
            user_ids: グループに追加するユーザーIDのリスト

        Returns:
            作成されたユーザーグループ

        Raises:
            AccessControlError: グループ名が重複している場合
        """
        if self.db.query(UserGroup).filter(UserGroup.name == name).first():
            raise AccessControlError(f"グループ名 '{name}' は既に使用されています")

        group = UserGroup(
            name=name,
            description=description,
            created_by_id=created_by_id,
        )
        self.db.add(group)
        self.db.flush()

        # ユーザーをグループに追加
        if user_ids:
            users = self.db.query(User).filter(User.id.in_(user_ids)).all()
            group.users.extend(users)

        self.db.commit()
        return group

    def add_users_to_group(
        self,
        group_id: int,
        user_ids: List[int],
        updated_by_id: int,
    ) -> UserGroup:
        """
        ユーザーグループにユーザーを追加

        Args:
            group_id: グループID
            user_ids: 追加するユーザーIDのリスト
            updated_by_id: 更新者ID

        Returns:
            更新されたユーザーグループ

        Raises:
            AccessControlError: グループが存在しない場合
        """
        group = self.db.query(UserGroup).get(group_id)
        if not group:
            raise AccessControlError(f"グループID {group_id} は存在しません")

        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        group.users.extend(users)
        group.updated_at = datetime.utcnow()
        self.db.commit()

        return group

    def remove_users_from_group(
        self,
        group_id: int,
        user_ids: List[int],
        updated_by_id: int,
    ) -> UserGroup:
        """
        ユーザーグループからユーザーを削除

        Args:
            group_id: グループID
            user_ids: 削除するユーザーIDのリスト
            updated_by_id: 更新者ID

        Returns:
            更新されたユーザーグループ

        Raises:
            AccessControlError: グループが存在しない場合
        """
        group = self.db.query(UserGroup).get(group_id)
        if not group:
            raise AccessControlError(f"グループID {group_id} は存在しません")

        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        for user in users:
            if user in group.users:
                group.users.remove(user)

        group.updated_at = datetime.utcnow()
        self.db.commit()

        return group

    def grant_dataset_access(
        self,
        dataset_id: int,
        group_id: int,
        access_level: AccessLevel,
        granted_by_id: int,
    ) -> DatasetAccess:
        """
        データセットへのアクセス権限を付与

        Args:
            dataset_id: データセットID
            group_id: グループID
            access_level: アクセス権限レベル
            granted_by_id: 権限付与者ID

        Returns:
            作成されたアクセス権限

        Raises:
            AccessControlError: データセットまたはグループが存在しない場合
        """
        dataset = self.db.query(Dataset).get(dataset_id)
        if not dataset:
            raise AccessControlError(f"データセットID {dataset_id} は存在しません")

        group = self.db.query(UserGroup).get(group_id)
        if not group:
            raise AccessControlError(f"グループID {group_id} は存在しません")

        # 既存のアクセス権限を確認
        existing_access = self.db.query(DatasetAccess).filter(
            DatasetAccess.dataset_id == dataset_id,
            DatasetAccess.group_id == group_id,
        ).first()

        if existing_access:
            existing_access.access_level = access_level
            existing_access.updated_at = datetime.utcnow()
            self.db.commit()
            return existing_access

        # 新しいアクセス権限を作成
        access = DatasetAccess(
            dataset_id=dataset_id,
            group_id=group_id,
            access_level=access_level,
            created_by_id=granted_by_id,
        )
        self.db.add(access)
        self.db.commit()

        return access

    def revoke_dataset_access(
        self,
        dataset_id: int,
        group_id: int,
        revoked_by_id: int,
    ) -> None:
        """
        データセットへのアクセス権限を削除

        Args:
            dataset_id: データセットID
            group_id: グループID
            revoked_by_id: 権限削除者ID

        Raises:
            AccessControlError: データセットまたはグループが存在しない場合
        """
        access = self.db.query(DatasetAccess).filter(
            DatasetAccess.dataset_id == dataset_id,
            DatasetAccess.group_id == group_id,
        ).first()

        if access:
            self.db.delete(access)
            self.db.commit()

    def check_dataset_access(
        self,
        dataset_id: int,
        user_id: int,
        required_level: AccessLevel,
    ) -> bool:
        """
        ユーザーのデータセットへのアクセス権限を確認

        Args:
            dataset_id: データセットID
            user_id: ユーザーID
            required_level: 必要なアクセス権限レベル

        Returns:
            アクセスが許可されている場合はTrue

        Raises:
            AccessControlError: データセットまたはユーザーが存在しない場合
        """
        user = self.db.query(User).get(user_id)
        if not user:
            raise AccessControlError(f"ユーザーID {user_id} は存在しません")

        dataset = self.db.query(Dataset).get(dataset_id)
        if not dataset:
            raise AccessControlError(f"データセットID {dataset_id} は存在しません")

        # データセットの作成者は常にアクセス可能
        if dataset.created_by_id == user_id:
            return True

        # ユーザーのグループを取得
        user_groups = user.groups
        if not user_groups:
            return False

        # グループのアクセス権限を確認
        access_levels = {
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
        }

        required_level_value = access_levels[required_level]
        for group in user_groups:
            access = self.db.query(DatasetAccess).filter(
                DatasetAccess.dataset_id == dataset_id,
                DatasetAccess.group_id == group.id,
            ).first()

            if access and access_levels[access.access_level] >= required_level_value:
                return True

        return False

    def get_dataset_access_list(
        self,
        dataset_id: int,
    ) -> List[Dict[str, Any]]:
        """
        データセットのアクセス権限一覧を取得

        Args:
            dataset_id: データセットID

        Returns:
            アクセス権限のリスト

        Raises:
            AccessControlError: データセットが存在しない場合
        """
        dataset = self.db.query(Dataset).get(dataset_id)
        if not dataset:
            raise AccessControlError(f"データセットID {dataset_id} は存在しません")

        access_list = []
        for access in dataset.access_controls:
            access_list.append({
                "group": {
                    "id": access.group.id,
                    "name": access.group.name,
                    "description": access.group.description,
                },
                "access_level": access.access_level.value,
                "granted_at": access.created_at.isoformat(),
                "granted_by": access.created_by.username,
            })

        return access_list

    def get_user_accessible_datasets(
        self,
        user_id: int,
        access_level: Optional[AccessLevel] = None,
    ) -> List[Dataset]:
        """
        ユーザーがアクセス可能なデータセット一覧を取得

        Args:
            user_id: ユーザーID
            access_level: 必要なアクセス権限レベル（指定しない場合は全てのレベル）

        Returns:
            アクセス可能なデータセットのリスト

        Raises:
            AccessControlError: ユーザーが存在しない場合
        """
        user = self.db.query(User).get(user_id)
        if not user:
            raise AccessControlError(f"ユーザーID {user_id} は存在しません")

        # ユーザーが作成したデータセットを取得
        query = self.db.query(Dataset).filter(Dataset.created_by_id == user_id)

        # グループ経由のアクセス権限を持つデータセットを取得
        if user.groups:
            group_ids = [group.id for group in user.groups]
            group_access_query = self.db.query(Dataset).join(DatasetAccess).filter(
                DatasetAccess.group_id.in_(group_ids)
            )

            if access_level:
                group_access_query = group_access_query.filter(
                    DatasetAccess.access_level == access_level
                )

            query = query.union(group_access_query)

        return query.all()


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
        self.access_control = AccessControlService(db_session)

    def create_dataset(
        self,
        name: str,
        description: str,
        created_by_id: int,
        schema: Dict,
        tags: Optional[List[str]] = None,
        initial_access_groups: Optional[List[Dict[str, Any]]] = None,
    ) -> Dataset:
        """
        新しいデータセットを作成

        Args:
            name: データセット名
            description: 説明
            created_by_id: 作成者ID
            schema: データスキーマ
            tags: タグリスト
            initial_access_groups: 初期アクセス権限設定
                [{"group_id": int, "access_level": AccessLevel}, ...]

        Returns:
            作成されたデータセット

        Raises:
            DatasetError: データセット名が重複している場合
            AccessControlError: グループが存在しない場合
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

        # 初期アクセス権限を設定
        if initial_access_groups:
            for access_info in initial_access_groups:
                self.access_control.grant_dataset_access(
                    dataset_id=dataset.id,
                    group_id=access_info["group_id"],
                    access_level=access_info["access_level"],
                    granted_by_id=created_by_id,
                )

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

    def get_dataset(
        self,
        dataset_id: int,
        user_id: int,
        required_level: AccessLevel = AccessLevel.READ,
    ) -> Optional[Dataset]:
        """
        データセットを取得（アクセス権限チェック付き）

        Args:
            dataset_id: データセットID
            user_id: ユーザーID
            required_level: 必要なアクセス権限レベル

        Returns:
            データセット（アクセス権限がない場合はNone）

        Raises:
            AccessControlError: データセットまたはユーザーが存在しない場合
        """
        if not self.access_control.check_dataset_access(dataset_id, user_id, required_level):
            return None

        return self.db.query(Dataset).get(dataset_id)

    def list_datasets(
        self,
        user_id: int,
        status: Optional[DatasetStatus] = None,
        tags: Optional[List[str]] = None,
        access_level: Optional[AccessLevel] = None,
    ) -> List[Dataset]:
        """
        データセット一覧を取得（アクセス権限チェック付き）

        Args:
            user_id: ユーザーID
            status: ステータスでフィルタリング
            tags: タグでフィルタリング
            access_level: 必要なアクセス権限レベル

        Returns:
            アクセス可能なデータセットのリスト

        Raises:
            AccessControlError: ユーザーが存在しない場合
        """
        # アクセス可能なデータセットを取得
        accessible_datasets = self.access_control.get_user_accessible_datasets(
            user_id=user_id,
            access_level=access_level,
        )

        # フィルタリング
        if status:
            accessible_datasets = [d for d in accessible_datasets if d.status == status]
        if tags:
            accessible_datasets = [
                d for d in accessible_datasets
                if all(tag in d.metadata.tags for tag in tags)
            ]

        return accessible_datasets

    def update_dataset(
        self,
        dataset_id: int,
        updated_by_id: int,
        description: Optional[str] = None,
        status: Optional[DatasetStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> Dataset:
        """
        データセットを更新（アクセス権限チェック付き）

        Args:
            dataset_id: データセットID
            updated_by_id: 更新者ID
            description: 新しい説明
            status: 新しいステータス
            tags: 新しいタグリスト

        Returns:
            更新されたデータセット

        Raises:
            DatasetError: データセットが存在しない場合
            AccessControlError: アクセス権限がない場合
        """
        if not self.access_control.check_dataset_access(
            dataset_id, updated_by_id, AccessLevel.WRITE
        ):
            raise AccessControlError("データセットの更新権限がありません")

        dataset = self.get_dataset(dataset_id, updated_by_id)
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

    def search_datasets(
        self,
        user_id: int,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[DatasetStatus] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[Dataset], int]:
        """
        データセットを検索

        Args:
            user_id: ユーザーID
            query: 検索クエリ（名前と説明を検索）
            tags: タグでフィルタリング
            status: ステータスでフィルタリング
            created_after: 作成日時（以降）
            created_before: 作成日時（以前）
            metadata_filters: メタデータフィールドによるフィルタリング
                {
                    "field_name": {
                        "operator": "eq|gt|lt|contains|in",
                        "value": value
                    }
                }
            sort_by: ソート対象フィールド
            sort_order: ソート順序（"asc" or "desc"）
            page: ページ番号
            per_page: 1ページあたりの件数

        Returns:
            (検索結果のデータセットリスト, 総件数)

        Raises:
            AccessControlError: ユーザーが存在しない場合
            DatasetError: 無効な検索パラメータが指定された場合
        """
        # アクセス可能なデータセットを取得
        accessible_datasets = self.access_control.get_user_accessible_datasets(user_id)
        if not accessible_datasets:
            return [], 0

        # 検索条件を構築
        dataset_ids = [d.id for d in accessible_datasets]
        query = self.db.query(Dataset).filter(Dataset.id.in_(dataset_ids))

        # テキスト検索
        if query:
            search_query = f"%{query}%"
            query = query.filter(
                (Dataset.name.ilike(search_query)) |
                (Dataset.description.ilike(search_query))
            )

        # タグでフィルタリング
        if tags:
            for tag in tags:
                query = query.filter(Dataset.metadata.has(tags=tag))

        # ステータスでフィルタリング
        if status:
            query = query.filter(Dataset.status == status)

        # 作成日時でフィルタリング
        if created_after:
            query = query.filter(Dataset.created_at >= created_after)
        if created_before:
            query = query.filter(Dataset.created_at <= created_before)

        # メタデータフィールドでフィルタリング
        if metadata_filters:
            for field_name, filter_info in metadata_filters.items():
                operator = filter_info.get("operator", "eq")
                value = filter_info.get("value")

                if operator == "eq":
                    query = query.filter(Dataset.metadata.has(
                        custom_fields={field_name: value}
                    ))
                elif operator == "gt":
                    query = query.filter(Dataset.metadata.has(
                        custom_fields={field_name: {"$gt": value}}
                    ))
                elif operator == "lt":
                    query = query.filter(Dataset.metadata.has(
                        custom_fields={field_name: {"$lt": value}}
                    ))
                elif operator == "contains":
                    query = query.filter(Dataset.metadata.has(
                        custom_fields={field_name: {"$contains": value}}
                    ))
                elif operator == "in":
                    query = query.filter(Dataset.metadata.has(
                        custom_fields={field_name: {"$in": value}}
                    ))
                else:
                    raise DatasetError(f"無効な演算子: {operator}")

        # 総件数を取得
        total_count = query.count()

        # ソート
        if sort_by:
            if sort_by == "name":
                sort_column = Dataset.name
            elif sort_by == "created_at":
                sort_column = Dataset.created_at
            elif sort_by == "updated_at":
                sort_column = Dataset.updated_at
            elif sort_by == "status":
                sort_column = Dataset.status
            else:
                raise DatasetError(f"無効なソートフィールド: {sort_by}")

            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # ページネーション
        query = query.offset((page - 1) * per_page).limit(per_page)

        return query.all(), total_count

    def get_dataset_tags(
        self,
        user_id: int,
        prefix: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        データセットのタグ一覧を取得

        Args:
            user_id: ユーザーID
            prefix: タグのプレフィックスでフィルタリング
            limit: 取得する最大件数

        Returns:
            タグ情報のリスト
            [
                {
                    "tag": "タグ名",
                    "count": 使用回数,
                    "datasets": [
                        {
                            "id": データセットID,
                            "name": データセット名
                        },
                        ...
                    ]
                },
                ...
            ]

        Raises:
            AccessControlError: ユーザーが存在しない場合
        """
        # アクセス可能なデータセットを取得
        accessible_datasets = self.access_control.get_user_accessible_datasets(user_id)
        if not accessible_datasets:
            return []

        # タグ情報を集計
        tag_info = {}
        for dataset in accessible_datasets:
            if not dataset.metadata or not dataset.metadata.tags:
                continue

            for tag in dataset.metadata.tags:
                if prefix and not tag.startswith(prefix):
                    continue

                if tag not in tag_info:
                    tag_info[tag] = {
                        "tag": tag,
                        "count": 0,
                        "datasets": [],
                    }

                tag_info[tag]["count"] += 1
                tag_info[tag]["datasets"].append({
                    "id": dataset.id,
                    "name": dataset.name,
                })

        # 使用回数でソートして制限
        sorted_tags = sorted(
            tag_info.values(),
            key=lambda x: (-x["count"], x["tag"])
        )[:limit]

        return sorted_tags

    def get_dataset_metadata_fields(
        self,
        user_id: int,
        field_prefix: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        データセットのメタデータフィールド一覧を取得

        Args:
            user_id: ユーザーID
            field_prefix: フィールド名のプレフィックスでフィルタリング
            limit: 取得する最大件数

        Returns:
            メタデータフィールド情報のリスト
            [
                {
                    "field": "フィールド名",
                    "count": 使用回数,
                    "type": "データ型",
                    "datasets": [
                        {
                            "id": データセットID,
                            "name": データセット名,
                            "value": フィールド値
                        },
                        ...
                    ]
                },
                ...
            ]

        Raises:
            AccessControlError: ユーザーが存在しない場合
        """
        # アクセス可能なデータセットを取得
        accessible_datasets = self.access_control.get_user_accessible_datasets(user_id)
        if not accessible_datasets:
            return []

        # フィールド情報を集計
        field_info = {}
        for dataset in accessible_datasets:
            if not dataset.metadata or not dataset.metadata.custom_fields:
                continue

            for field_name, field_value in dataset.metadata.custom_fields.items():
                if field_prefix and not field_name.startswith(field_prefix):
                    continue

                if field_name not in field_info:
                    field_info[field_name] = {
                        "field": field_name,
                        "count": 0,
                        "type": type(field_value).__name__,
                        "datasets": [],
                    }

                field_info[field_name]["count"] += 1
                field_info[field_name]["datasets"].append({
                    "id": dataset.id,
                    "name": dataset.name,
                    "value": field_value,
                })

        # 使用回数でソートして制限
        sorted_fields = sorted(
            field_info.values(),
            key=lambda x: (-x["count"], x["field"])
        )[:limit]

        return sorted_fields


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
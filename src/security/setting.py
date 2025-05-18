"""
セキュリティ設定管理サービス

セキュリティ設定の取得・更新・一覧取得・バリデーションを行うモジュールです。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .models import SecuritySetting, User

class SecuritySettingError(Exception):
    """セキュリティ設定管理の例外"""
    pass

class SecuritySettingService:
    """セキュリティ設定管理サービス"""
    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str) -> Optional[SecuritySetting]:
        """キーで設定を取得"""
        return self.db.query(SecuritySetting).filter_by(key=key).first()

    def set_setting(self, key: str, value: str, updated_by: Optional[int] = None, description: Optional[str] = None) -> SecuritySetting:
        """設定を新規作成または更新"""
        try:
            setting = self.get_setting(key)
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
                if updated_by:
                    setting.updated_by = updated_by
                if description:
                    setting.description = description
            else:
                setting = SecuritySetting(
                    key=key,
                    value=value,
                    updated_by=updated_by,
                    description=description
                )
                self.db.add(setting)
            self.db.commit()
            return setting
        except SQLAlchemyError as e:
            self.db.rollback()
            raise SecuritySettingError(f"設定の保存に失敗: {str(e)}")

    def list_settings(self) -> List[SecuritySetting]:
        """全ての設定を取得"""
        return self.db.query(SecuritySetting).order_by(SecuritySetting.key).all()

    def validate_setting(self, key: str, value: str) -> bool:
        """設定値のバリデーション（例: 必須キーや型チェックなど）"""
        # 必要に応じて個別バリデーションを実装
        # 例: パスワードポリシーや閾値など
        # ここではサンプルとして空文字禁止のみ
        if not value:
            raise SecuritySettingError(f"{key}の値は空にできません")
        return True 
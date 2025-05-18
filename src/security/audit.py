"""
監査ログサービス

セキュリティ関連のイベントを記録し、監査ログを管理するモジュールです。
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from .models import AuditLog, AuditLogLevel, AuditLogCategory, User

class AuditError(Exception):
    """監査ログ関連のエラーを表す例外クラス"""
    pass

class AuditService:
    """監査ログサービスを提供するクラス"""
    
    def __init__(self, db: Session):
        """
        監査ログサービスの初期化

        Args:
            db: データベースセッション
        """
        self.db = db
    
    def log_event(
        self,
        level: AuditLogLevel,
        category: AuditLogCategory,
        action: str,
        status: str,
        user_id: Optional[int] = None,
        resource: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        監査ログイベントを記録

        Args:
            level: ログの重要度レベル
            category: ログのカテゴリ
            action: 実行されたアクション
            status: アクションの状態（success/failed等）
            user_id: 関連するユーザーID（オプション）
            resource: アクセスされたリソース（オプション）
            ip_address: クライアントのIPアドレス（オプション）
            user_agent: クライアントのUser-Agent（オプション）
            details: 追加の詳細情報（オプション）
            error_message: エラーメッセージ（オプション）

        Returns:
            作成されたAuditLogオブジェクト

        Raises:
            AuditError: ログ記録中にエラーが発生した場合
        """
        try:
            log = AuditLog(
                level=level,
                category=category,
                user_id=user_id,
                action=action,
                resource=resource,
                status=status,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                error_message=error_message
            )
            self.db.add(log)
            self.db.commit()
            return log
        except SQLAlchemyError as e:
            self.db.rollback()
            raise AuditError(f"ログの記録中にエラーが発生しました: {str(e)}")
    
    def log_auth_event(
        self,
        action: str,
        status: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        認証関連のイベントを記録

        Args:
            action: 実行されたアクション（login/logout等）
            status: アクションの状態（success/failed）
            その他のパラメータはlog_eventと同様

        Returns:
            作成されたAuditLogオブジェクト
        """
        return self.log_event(
            level=AuditLogLevel.ERROR if status == "failed" else AuditLogLevel.INFO,
            category=AuditLogCategory.AUTHENTICATION,
            action=action,
            status=status,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            error_message=error_message
        )
    
    def log_access_event(
        self,
        action: str,
        resource: str,
        status: str,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        アクセス制御関連のイベントを記録

        Args:
            action: 実行されたアクション（read/write等）
            resource: アクセスされたリソース
            status: アクションの状態（success/failed）
            その他のパラメータはlog_eventと同様

        Returns:
            作成されたAuditLogオブジェクト
        """
        return self.log_event(
            level=AuditLogLevel.ERROR if status == "failed" else AuditLogLevel.INFO,
            category=AuditLogCategory.AUTHORIZATION,
            action=action,
            resource=resource,
            status=status,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            error_message=error_message
        )
    
    def get_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[Union[AuditLogLevel, List[AuditLogLevel]]] = None,
        category: Optional[Union[AuditLogCategory, List[AuditLogCategory]]] = None,
        user_id: Optional[int] = None,
        resource: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        監査ログを検索

        Args:
            start_time: 開始時刻（オプション）
            end_time: 終了時刻（オプション）
            level: ログレベル（オプション）
            category: ログカテゴリ（オプション）
            user_id: ユーザーID（オプション）
            resource: リソース名（オプション）
            status: ステータス（オプション）
            limit: 取得する最大件数
            offset: スキップする件数

        Returns:
            条件に一致するAuditLogオブジェクトのリスト
        """
        query = self.db.query(AuditLog)
        
        # フィルター条件の適用
        if start_time:
            query = query.filter(AuditLog.timestamp >= start_time)
        if end_time:
            query = query.filter(AuditLog.timestamp <= end_time)
        if level:
            if isinstance(level, list):
                query = query.filter(AuditLog.level.in_(level))
            else:
                query = query.filter(AuditLog.level == level)
        if category:
            if isinstance(category, list):
                query = query.filter(AuditLog.category.in_(category))
            else:
                query = query.filter(AuditLog.category == category)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource:
            query = query.filter(AuditLog.resource == resource)
        if status:
            query = query.filter(AuditLog.status == status)
        
        # 結果の取得
        return query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()
    
    def get_user_activity_summary(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        ユーザーのアクティビティサマリーを取得

        Args:
            user_id: ユーザーID
            days: 集計する日数

        Returns:
            アクティビティサマリーを含む辞書
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        
        # ログの取得
        logs = self.get_logs(
            start_time=start_time,
            user_id=user_id,
            limit=1000  # 十分な件数を取得
        )
        
        # サマリーの作成
        summary = {
            "total_events": len(logs),
            "successful_events": len([log for log in logs if log.status == "success"]),
            "failed_events": len([log for log in logs if log.status == "failed"]),
            "categories": {},
            "resources": {},
            "recent_activities": []
        }
        
        # カテゴリとリソースの集計
        for log in logs:
            # カテゴリの集計
            category = log.category.value
            if category not in summary["categories"]:
                summary["categories"][category] = 0
            summary["categories"][category] += 1
            
            # リソースの集計
            if log.resource:
                if log.resource not in summary["resources"]:
                    summary["resources"][log.resource] = 0
                summary["resources"][log.resource] += 1
            
            # 最近のアクティビティ（最新10件）
            if len(summary["recent_activities"]) < 10:
                summary["recent_activities"].append({
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "resource": log.resource,
                    "status": log.status
                })
        
        return summary 
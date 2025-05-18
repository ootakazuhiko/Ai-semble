"""
認証サービス

ユーザー認証、セッション管理、アクセス制御を担当するモジュールです。
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .models import User, Role, Permission, Session as SessionModel
from .encryption import EncryptionService

class AuthError(Exception):
    """認証関連のエラーを表す例外クラス"""
    pass

class AuthService:
    """認証サービスを提供するクラス"""
    
    def __init__(
        self,
        db: Session,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        encryption_service: Optional[EncryptionService] = None
    ):
        """
        認証サービスの初期化

        Args:
            db: データベースセッション
            secret_key: JWT署名用の秘密鍵
            algorithm: JWT署名アルゴリズム
            access_token_expire_minutes: アクセストークンの有効期限（分）
            encryption_service: 暗号化サービス（オプション）
        """
        self.db = db
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.encryption_service = encryption_service or EncryptionService()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        パスワードの検証

        Args:
            plain_password: 平文パスワード
            hashed_password: ハッシュ化されたパスワード

        Returns:
            パスワードが一致する場合はTrue
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        パスワードのハッシュ化

        Args:
            password: 平文パスワード

        Returns:
            ハッシュ化されたパスワード
        """
        return self.pwd_context.hash(password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        ユーザー認証

        Args:
            username: ユーザー名
            password: パスワード

        Returns:
            認証成功時はUserオブジェクト、失敗時はNone

        Raises:
            AuthError: 認証処理中にエラーが発生した場合
        """
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user or not self.verify_password(password, user.password_hash):
                return None
            
            # 最終ログイン時刻を更新
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            raise AuthError(f"認証処理中にエラーが発生しました: {str(e)}")
    
    def create_access_token(self, user: User, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        アクセストークンの作成

        Args:
            user: ユーザーオブジェクト
            ip_address: クライアントのIPアドレス（オプション）
            user_agent: クライアントのUser-Agent（オプション）

        Returns:
            トークン情報を含む辞書

        Raises:
            AuthError: トークン作成中にエラーが発生した場合
        """
        try:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
            expire = datetime.utcnow() + expires_delta
            
            # トークンのペイロードを作成
            to_encode = {
                "sub": str(user.id),
                "exp": expire,
                "username": user.username,
                "roles": [role.name for role in user.roles]
            }
            
            # JWTトークンを生成
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            # セッションをデータベースに保存
            session = SessionModel(
                user_id=user.id,
                token=token,
                expires_at=expire,
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.db.add(session)
            self.db.commit()
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_at": expire.isoformat()
            }
        except (JWTError, SQLAlchemyError) as e:
            self.db.rollback()
            raise AuthError(f"トークン作成中にエラーが発生しました: {str(e)}")
    
    def verify_token(self, token: str) -> Optional[User]:
        """
        トークンの検証

        Args:
            token: 検証するトークン

        Returns:
            トークンが有効な場合はUserオブジェクト、無効な場合はNone

        Raises:
            AuthError: トークン検証中にエラーが発生した場合
        """
        try:
            # トークンを検証
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = int(payload["sub"])
            
            # セッションの有効性を確認
            session = self.db.query(SessionModel).filter(
                SessionModel.token == token,
                SessionModel.is_active == True,
                SessionModel.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                return None
            
            # セッションの最終アクティビティを更新
            session.last_activity = datetime.utcnow()
            self.db.commit()
            
            # ユーザーを取得
            return self.db.query(User).filter(User.id == user_id).first()
        except (JWTError, SQLAlchemyError) as e:
            self.db.rollback()
            raise AuthError(f"トークン検証中にエラーが発生しました: {str(e)}")
    
    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """
        ユーザーの権限をチェック

        Args:
            user: ユーザーオブジェクト
            resource: リソース名
            action: アクション名

        Returns:
            権限がある場合はTrue、ない場合はFalse
        """
        # スーパーユーザーは全ての権限を持つ
        if user.is_superuser:
            return True
        
        # ユーザーのロールに紐づくパーミッションをチェック
        for role in user.roles:
            for permission in role.permissions:
                if permission.resource == resource and permission.action == action:
                    return True
        
        return False
    
    def invalidate_session(self, token: str) -> bool:
        """
        セッションの無効化

        Args:
            token: 無効化するセッションのトークン

        Returns:
            無効化に成功した場合はTrue、失敗した場合はFalse
        """
        try:
            session = self.db.query(SessionModel).filter(SessionModel.token == token).first()
            if session:
                session.is_active = False
                self.db.commit()
                return True
            return False
        except SQLAlchemyError:
            self.db.rollback()
            return False 
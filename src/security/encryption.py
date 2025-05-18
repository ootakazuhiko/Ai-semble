"""
暗号化モジュール

機密情報の暗号化と復号化を担当するモジュールです。
"""

from typing import Optional, Union
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import boto3
from botocore.exceptions import ClientError

class EncryptionError(Exception):
    """暗号化関連のエラーを表す例外クラス"""
    pass

class EncryptionService:
    """暗号化サービスを提供するクラス"""
    
    def __init__(
        self,
        key: Optional[bytes] = None,
        aws_region: Optional[str] = None,
        kms_key_id: Optional[str] = None
    ):
        """
        暗号化サービスの初期化

        Args:
            key: 暗号化キー（指定がない場合は自動生成）
            aws_region: AWSリージョン（KMS使用時）
            kms_key_id: KMSキーID（KMS使用時）
        """
        self._use_kms = bool(aws_region and kms_key_id)
        
        if self._use_kms:
            self._kms_client = boto3.client('kms', region_name=aws_region)
            self._kms_key_id = kms_key_id
        else:
            if key is None:
                key = Fernet.generate_key()
            self._fernet = Fernet(key)
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        データを暗号化

        Args:
            data: 暗号化するデータ

        Returns:
            暗号化されたデータ

        Raises:
            EncryptionError: 暗号化に失敗した場合
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if self._use_kms:
                response = self._kms_client.encrypt(
                    KeyId=self._kms_key_id,
                    Plaintext=data
                )
                return response['CiphertextBlob']
            else:
                return self._fernet.encrypt(data)
        except Exception as e:
            raise EncryptionError(f"暗号化に失敗しました: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        データを復号化

        Args:
            encrypted_data: 復号化するデータ

        Returns:
            復号化されたデータ

        Raises:
            EncryptionError: 復号化に失敗した場合
        """
        try:
            if self._use_kms:
                response = self._kms_client.decrypt(
                    CiphertextBlob=encrypted_data,
                    KeyId=self._kms_key_id
                )
                return response['Plaintext']
            else:
                return self._fernet.decrypt(encrypted_data)
        except Exception as e:
            raise EncryptionError(f"復号化に失敗しました: {str(e)}")
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        パスワードから暗号化キーを導出

        Args:
            password: パスワード
            salt: ソルト

        Returns:
            導出されたキー
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode())) 
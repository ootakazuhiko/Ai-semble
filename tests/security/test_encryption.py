"""
暗号化モジュールのテスト
"""

import pytest
from src.security.encryption import EncryptionService, EncryptionError

def test_encryption_decryption():
    """基本的な暗号化と復号化のテスト"""
    service = EncryptionService()
    original_data = "テストデータ"
    
    # 暗号化
    encrypted = service.encrypt(original_data)
    assert encrypted != original_data.encode()
    
    # 復号化
    decrypted = service.decrypt(encrypted)
    assert decrypted.decode() == original_data

def test_encryption_with_custom_key():
    """カスタムキーを使用した暗号化のテスト"""
    key = b"test_key_32_bytes_long_for_fernet_"
    service = EncryptionService(key=key)
    original_data = "カスタムキーテスト"
    
    encrypted = service.encrypt(original_data)
    decrypted = service.decrypt(encrypted)
    assert decrypted.decode() == original_data

def test_encryption_error():
    """エラー処理のテスト"""
    service = EncryptionService()
    
    # 不正なデータでの復号化
    with pytest.raises(EncryptionError):
        service.decrypt(b"invalid_data")

def test_key_derivation():
    """キー導出のテスト"""
    password = "test_password"
    salt = b"test_salt"
    
    key1 = EncryptionService.derive_key(password, salt)
    key2 = EncryptionService.derive_key(password, salt)
    
    # 同じパスワードとソルトからは同じキーが生成される
    assert key1 == key2
    
    # 異なるソルトからは異なるキーが生成される
    different_salt = b"different_salt"
    key3 = EncryptionService.derive_key(password, different_salt)
    assert key1 != key3

@pytest.mark.skipif(True, reason="AWS認証情報が必要")
def test_kms_encryption():
    """AWS KMSを使用した暗号化のテスト（スキップ）"""
    service = EncryptionService(
        aws_region="ap-northeast-1",
        kms_key_id="test-key-id"
    )
    original_data = "KMSテストデータ"
    
    encrypted = service.encrypt(original_data)
    decrypted = service.decrypt(encrypted)
    assert decrypted.decode() == original_data 
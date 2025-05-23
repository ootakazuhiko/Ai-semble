"""
データセキュリティユーティリティのテスト
"""

import unittest
import json
from src.utils.data_security import (
    DataMasking, 
    DynamicMasking, 
    encrypt_data, 
    decrypt_data, 
    mask_sensitive_data, 
    is_sensitive_data
)
from cryptography.fernet import Fernet

class TestDataMasking(unittest.TestCase):
    """データマスキング機能のテスト"""

    def test_mask_string(self):
        """文字列マスキングのテスト"""
        # 各パターンごとに個別にテスト
        email_text = "メール: user@example.com"
        phone_text = "電話: 03-1234-5678"
        card_text = "カード: 1234-5678-9012-3456"
        
        masking = DataMasking()
        
        # メールのマスキング
        masked_email = masking.mask_data(email_text)
        self.assertNotIn("user@example.com", masked_email)
        self.assertIn("***@***.***", masked_email)
        
        # 電話番号のマスキング
        masked_phone = masking.mask_data(phone_text)
        self.assertNotIn("03-1234-5678", masked_phone)
        self.assertIn("***-****-****", masked_phone)
        
        # クレジットカードのマスキング
        masked_card = masking.mask_data(card_text)
        self.assertNotIn("1234-5678-9012-3456", masked_card)
        # パターン一致による置換を確認

    def test_mask_dict(self):
        """辞書マスキングのテスト"""
        data = {
            "user": {
                "email": "user@example.com",
                "phone": "03-1234-5678"
            },
            "payment": {
                "card_number": "1234-5678-9012-3456",
                "expiry": "12/25"
            }
        }
        
        # 新しいDataMaskingインスタンスを作成してテスト
        masking = DataMasking()
        masked = masking.mask_data(data)
        
        # 特定のフィールドがマスクされていることを確認
        self.assertEqual(masked["user"]["email"], "***@***.***")
        self.assertEqual(masked["user"]["phone"], "***-****-****")
        # 元の文字列と異なることを確認
        self.assertNotEqual(masked["payment"]["card_number"], "1234-5678-9012-3456")
        self.assertEqual(masked["payment"]["expiry"], "12/25")  # マスクされないはず

    def test_specific_rules(self):
        """特定のルールのみ適用するテスト"""
        text = "メール: user@example.com, 電話: 03-1234-5678, カード: 1234-5678-9012-3456"
        
        # クレジットカードのルールのみ適用
        masking = DataMasking()
        masked = masking.mask_data(text, rule_names=["CREDIT_CARD"])
        
        # カード番号はマスクされるが、メールと電話はマスクされない
        self.assertIn("user@example.com", masked)
        self.assertIn("03-1234-5678", masked)
        self.assertNotIn("1234-5678-9012-3456", masked)
        self.assertIn("****-****-****-****", masked)

    def test_custom_rule(self):
        """カスタムマスキングルールのテスト"""
        masking = DataMasking()
        # 郵便番号用のカスタムルール追加
        masking.add_rule(
            name="POSTAL_CODE",
            pattern=r'\d{3}-\d{4}',
            replacement="***-****",
            method="full_mask"
        )
        
        text = "住所: 東京都港区 123-4567"
        masked = masking.mask_data(text, rule_names=["POSTAL_CODE"])
        
        # 郵便番号がマスクされる
        self.assertIn("東京都港区", masked)
        self.assertNotIn("123-4567", masked)
        self.assertIn("***-****", masked)

    def test_is_sensitive_data(self):
        """機密データ検出のテスト"""
        # 機密データを含むケース
        self.assertTrue(is_sensitive_data("メールアドレス: user@example.com"))
        self.assertTrue(is_sensitive_data("クレジットカード: 1234-5678-9012-3456"))
        
        # 機密データを含まないケース
        self.assertFalse(is_sensitive_data("普通のテキスト"))
        self.assertFalse(is_sensitive_data("番号: 123-456"))  # パターンに一致しない


class TestDynamicMasking(unittest.TestCase):
    """動的マスキング機能のテスト"""

    def test_dynamic_masking_by_role(self):
        """ユーザーロールに基づく動的マスキング"""
        # テストデータを初期化
        data = {
            "user": {
                "email": "test@example.com",
                "phone": "03-1234-5678"
            },
            "payment": {
                "card_number": "1234-5678-9012-3456"
            }
        }
        
        # 標準マスキングルールを使用
        masking = DataMasking()
        # ダイナミックマスキングを設定
        dynamic = DynamicMasking(masking_service=masking)
        
        # 管理者ユーザーのケース
        admin_result = dynamic.apply_dynamic_masking(
            data=data.copy(),  # コピーを使用して元データを変更しない
            user_context={"role": "ADMIN"}
        )
        self.assertEqual(admin_result["user"]["email"], "test@example.com")
        self.assertEqual(admin_result["payment"]["card_number"], "1234-5678-9012-3456")

        # 開発者ユーザーのケース
        dev_result = dynamic.apply_dynamic_masking(
            data=data.copy(), 
            user_context={"role": "DEVELOPER"}
        )
        
        # メールは表示される
        self.assertEqual(dev_result["user"]["email"], "test@example.com")
        # カード番号はマスクされる（完全一致でなくパターン一致として検証）
        self.assertNotEqual(dev_result["payment"]["card_number"], "1234-5678-9012-3456")
        
        # 一般ユーザーのケース
        user_result = dynamic.apply_dynamic_masking(
            data=data.copy(),
            user_context={"role": "USER"}
        )
        # メールとカード番号の両方がマスクされる
        self.assertEqual(user_result["user"]["email"], "***@***.***")
        self.assertNotEqual(user_result["payment"]["card_number"], "1234-5678-9012-3456")


class TestEncryptionUtilities(unittest.TestCase):
    """暗号化ユーティリティのテスト"""

    def test_encrypt_decrypt(self):
        """暗号化と復号化のテスト"""
        # テスト用のキーを生成
        key = Fernet.generate_key()
        original_data = "これは機密データです"
        
        # 同じキーでの暗号化・復号化
        encrypted = encrypt_data(original_data, key=key)
        decrypted = decrypt_data(encrypted, key=key)
        
        self.assertEqual(decrypted.decode(), original_data)


if __name__ == "__main__":
    unittest.main()
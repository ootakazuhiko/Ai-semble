"""
データセキュリティユーティリティ

データマスキング、暗号化、その他のデータセキュリティに関する共通機能を提供します。
"""

import re
from typing import Dict, List, Any, Union, Optional, Pattern
import json
from ..security.encryption import EncryptionService, EncryptionError


class MaskingError(Exception):
    """データマスキング関連のエラーを表す例外クラス"""
    pass


class DataMasking:
    """データマスキング機能を提供するクラス"""

    # デフォルトマスキングルール
    DEFAULT_MASKING_RULES = {
        'PERSONAL_ID': {
            'pattern': r'\d{12}',
            'replacement': '********',
            'method': 'full_mask'
        },
        'EMAIL': {
            'pattern': r'[^@]+@[^@]+\.[^@]+',
            'replacement': '***@***.***',
            'method': 'full_mask'
        },
        'PHONE': {
            'pattern': r'\d{2,4}-\d{2,4}-\d{4}',
            'replacement': '***-****-****',
            'method': 'full_mask'
        },
        'CREDIT_CARD': {
            'pattern': r'\d{4}-\d{4}-\d{4}-\d{4}',
            'replacement': '****-****-****-****',
            'method': 'full_mask'
        }
    }

    def __init__(self, custom_rules: Optional[Dict[str, Dict]] = None):
        """
        データマスキングの初期化

        Args:
            custom_rules: カスタムマスキングルール（オプション）
        """
        self.masking_rules = self.DEFAULT_MASKING_RULES.copy()
        
        # カスタムルールがあれば追加または上書き
        if custom_rules:
            for rule_name, rule in custom_rules.items():
                self.masking_rules[rule_name] = rule
        
        # コンパイル済みの正規表現パターンを保持
        self._compiled_patterns = {}
        for rule_name, rule in self.masking_rules.items():
            self._compiled_patterns[rule_name] = re.compile(rule['pattern'])

    def mask_data(self, data: Union[str, Dict, List], rule_names: Optional[List[str]] = None) -> Union[str, Dict, List]:
        """
        データをマスキング

        Args:
            data: マスキングするデータ（文字列、辞書、またはリスト）
            rule_names: 適用するルール名のリスト（指定がない場合はすべてのルールを適用）

        Returns:
            マスキングされたデータ

        Raises:
            MaskingError: マスキング処理中にエラーが発生した場合
        """
        try:
            # 適用するルールのフィルタリング
            rules_to_apply = {}
            if rule_names:
                for name in rule_names:
                    if name in self.masking_rules:
                        rules_to_apply[name] = self.masking_rules[name]
            else:
                rules_to_apply = self.masking_rules
            
            # データ型に応じたマスキング処理
            if isinstance(data, str):
                return self._mask_string(data, rules_to_apply)
            elif isinstance(data, dict):
                return self._mask_dict(data, rules_to_apply)
            elif isinstance(data, list):
                return self._mask_list(data, rules_to_apply)
            else:
                # 対象外の型はそのまま返す
                return data
        except Exception as e:
            raise MaskingError(f"マスキング処理中にエラーが発生しました: {str(e)}")

    def _mask_string(self, text: str, rules: Dict[str, Dict]) -> str:
        """文字列に対してマスキングを適用"""
        result = text
        for rule_name, rule in rules.items():
            pattern = self._compiled_patterns[rule_name]
            # 全置換のみをサポート
            result = pattern.sub(rule['replacement'], result)
        return result

    def _mask_dict(self, data: Dict, rules: Dict[str, Dict]) -> Dict:
        """辞書に対してマスキングを適用"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._mask_string(value, rules)
            elif isinstance(value, dict):
                result[key] = self._mask_dict(value, rules)
            elif isinstance(value, list):
                result[key] = self._mask_list(value, rules)
            else:
                result[key] = value
        return result

    def _mask_list(self, data: List, rules: Dict[str, Dict]) -> List:
        """リストに対してマスキングを適用"""
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self._mask_string(item, rules))
            elif isinstance(item, dict):
                result.append(self._mask_dict(item, rules))
            elif isinstance(item, list):
                result.append(self._mask_list(item, rules))
            else:
                result.append(item)
        return result

    def add_rule(self, name: str, pattern: Union[str, Pattern], replacement: str, method: str = 'full_mask') -> None:
        """
        新しいマスキングルールを追加

        Args:
            name: ルール名
            pattern: マスキングするパターン（文字列または正規表現オブジェクト）
            replacement: 置換文字列
            method: マスキング方法（'full_mask'または'partial_mask'）
        """
        if method not in ['full_mask', 'partial_mask']:
            raise ValueError("マスキング方法は'full_mask'または'partial_mask'である必要があります")
        
        pattern_str = pattern if isinstance(pattern, str) else pattern.pattern
        self.masking_rules[name] = {
            'pattern': pattern_str,
            'replacement': replacement,
            'method': method
        }
        self._compiled_patterns[name] = re.compile(pattern_str) if isinstance(pattern, str) else pattern


class DynamicMasking:
    """コンテキスト依存の動的マスキング機能を提供するクラス"""
    
    def __init__(self, masking_service: Optional[DataMasking] = None):
        """
        動的マスキングの初期化

        Args:
            masking_service: 使用するDataMaskingインスタンス（オプション）
        """
        self.masking_service = masking_service if masking_service else DataMasking()
        self.masking_policies = {
            'REAL_TIME': {
                'enabled': True,
                'context_based': True
            },
            'BATCH': {
                'enabled': True,
                'schedule': 'daily'
            }
        }
    
    def apply_dynamic_masking(self, data: Union[str, Dict, List], user_context: Dict[str, Any]) -> Union[str, Dict, List]:
        """
        ユーザーのコンテキストに基づいて動的マスキングを適用

        Args:
            data: マスキングするデータ
            user_context: ユーザーのコンテキスト情報（ロール、権限など）

        Returns:
            マスキングされたデータ
        """
        if not self.masking_policies['REAL_TIME']['enabled']:
            return data
        
        # コンテキストに基づいてマスキングルールを決定
        masking_level = self._determine_masking_level(user_context)
        
        # NONEレベルの場合はマスキングなし
        if masking_level == 'NONE':
            return data
            
        # マスキングルールを取得して適用
        rule_names = self._get_rules_for_level(masking_level)
        return self.masking_service.mask_data(data, rule_names)
    
    def _determine_masking_level(self, user_context: Dict[str, Any]) -> str:
        """
        ユーザーのコンテキストに基づいてマスキングレベルを決定
        
        Args:
            user_context: ユーザーコンテキスト情報
            
        Returns:
            マスキングレベル（'HIGH', 'MEDIUM', 'LOW', 'NONE'）
        """
        # ロールベースのマスキングレベル決定
        # 実際のアプリケーションに合わせて拡張可能
        role = user_context.get('role', '').upper()
        
        if role == 'ADMIN' or role == 'SECURITY_ADMIN':
            return 'NONE'  # 管理者は未マスキング
        elif role == 'DATA_ANALYST':
            return 'LOW'   # データアナリストは一部マスキング
        elif role == 'DEVELOPER':
            return 'MEDIUM'  # 開発者は中程度マスキング
        else:
            return 'HIGH'  # デフォルトは高度マスキング
    
    def _get_rules_for_level(self, level: str) -> List[str]:
        """
        マスキングレベルに基づいて適用するルール名のリストを取得
        
        Args:
            level: マスキングレベル
            
        Returns:
            適用するルール名のリスト
        """
        # レベルに基づくルールの選択
        # アプリケーションの要件に応じてカスタマイズ可能
        if level == 'NONE':
            return []  # マスキングなし
        elif level == 'LOW':
            return ['CREDIT_CARD']  # クレジットカードのみマスク
        elif level == 'MEDIUM':
            return ['CREDIT_CARD', 'PHONE']  # カードと電話番号をマスク
        else:  # HIGH
            return list(self.masking_service.masking_rules.keys())  # すべてマスク


# 既存の暗号化機能をエクスポート
def encrypt_data(data: Union[str, bytes], key: Optional[bytes] = None) -> bytes:
    """
    データを暗号化する便利関数
    
    Args:
        data: 暗号化するデータ
        key: 暗号化キー（オプション、指定がない場合は自動生成）
        
    Returns:
        暗号化されたデータ
        
    Raises:
        EncryptionError: 暗号化に失敗した場合
    """
    service = EncryptionService(key=key)
    
    # サービスを一度生成したら、そのキーを使って暗号化
    return service.encrypt(data)


def decrypt_data(encrypted_data: bytes, key: Optional[bytes] = None) -> bytes:
    """
    データを復号化する便利関数
    
    Args:
        encrypted_data: 復号化するデータ
        key: 復号化キー（encrypt_dataで使用したものと同じキーが必要）
        
    Returns:
        復号化されたデータ
        
    Raises:
        EncryptionError: 復号化に失敗した場合
    """
    service = EncryptionService(key=key)
    return service.decrypt(encrypted_data)


def mask_sensitive_data(data: Union[str, Dict, List], rules: Optional[List[str]] = None) -> Union[str, Dict, List]:
    """
    機密データをマスキングする便利関数
    
    Args:
        data: マスキングするデータ
        rules: 適用するルール名のリスト（指定がない場合はすべてのルールを適用）
        
    Returns:
        マスキングされたデータ
        
    Raises:
        MaskingError: マスキング処理中にエラーが発生した場合
    """
    masking_service = DataMasking()
    return masking_service.mask_data(data, rules)


def is_sensitive_data(text: str) -> bool:
    """
    テキストに機密データが含まれているかを確認
    
    Args:
        text: チェックするテキスト
        
    Returns:
        機密データが含まれている場合はTrue、そうでない場合はFalse
    """
    masking_service = DataMasking()
    
    for rule_name, pattern in masking_service._compiled_patterns.items():
        if pattern.search(text):
            return True
    
    return False
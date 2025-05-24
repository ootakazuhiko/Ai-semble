# 共通セキュリティパターン

このドキュメントはプロジェクト全体で参照される共通のセキュリティパターンと実装方針をまとめたものです。
各モジュールやサービスの実装では、ここで定義されたパターンを一貫して使用してください。

## 1. データ保護

### 1.1 データマスキング

データマスキングは、機密情報を適切に保護するために使用されます。すべてのサービスは `src/utils/data_security.py` の機能を利用してください。

```python
# 標準的なデータマスキングの例
from src.utils.data_security import mask_sensitive_data

# 文字列、辞書、リストに対応
masked_data = mask_sensitive_data(data)

# 特定のルールのみ適用
masked_data = mask_sensitive_data(data, rules=['CREDIT_CARD', 'PERSONAL_ID'])
```

### 1.2 データ暗号化

機密データの保存や転送時には適切な暗号化を適用してください。すべての暗号化操作は `src/utils/data_security.py` の関数を使用します。

```python
# 暗号化と復号化の標準的な使用例
from src.utils.data_security import encrypt_data, decrypt_data

# データの暗号化
encrypted = encrypt_data("機密情報")

# データの復号化
decrypted = decrypt_data(encrypted)
```

## 2. セキュリティガイドライン

### 2.1 入力検証

すべての外部入力は検証されるべきです。

- ホワイトリスト方式を優先
- すべての入力に対して型チェックを実施
- エスケープ処理を適切に行う

### 2.2 認証・認可

アプリケーション内の認証・認可は一貫したアプローチで実装する必要があります。

- 認証には多要素認証を推奨
- セッション管理は適切なタイムアウト設定を行う
- 権限管理は最小権限の原則に従う

### 2.3 エラーハンドリング

セキュアなエラーハンドリングを実装してください。

- 詳細なエラー情報をユーザーに表示しない
- エラーログには適切なコンテキスト情報を含める
- エラーハンドリングの不備によりセキュリティを損なわないこと

## 3. セキュリティコンポーネント

### 3.1 暗号化コンポーネント

```python
# 暗号化コンポーネント
class EncryptionComponents:
    def __init__(self):
        self.encryption_components = {
            'key_management': {
                'type': 'HSM',
                'features': [
                    '鍵の生成',
                    '鍵の保存',
                    '鍵のローテーション'
                ],
                'policies': {
                    'key_rotation': '90日',
                    'key_backup': '自動',
                    'key_archival': '1年'
                }
            },
            'data_encryption': {
                'algorithms': {
                    'symmetric': 'AES-256-GCM',
                    'asymmetric': 'RSA-4096',
                    'hashing': 'SHA-256'
                },
                'implementations': {
                    'at_rest': '透過的暗号化',
                    'in_transit': 'TLS 1.3',
                    'in_use': '準同型暗号'
                }
            }
        }
```

### 3.2 監査コンポーネント

セキュリティ関連のイベントは監査ログに記録する必要があります。

```python
# 監査ログの標準的な使用例
from src.security.audit import AuditService

# イベントの記録
audit_service.log_event(
    level=AuditLogLevel.INFO,
    category=AuditLogCategory.DATA_ACCESS,
    action="data_export",
    status="success",
    user_id=user.id,
    resource=f"dataset/{dataset_id}"
)
```

## 4. セキュリティパターン

### 4.1 アプリケーションパターン

```python
# アプリケーションセキュリティパターン
class SecurityPatterns:
    def __init__(self):
        self.application_patterns = {
            'secure_communication': {
                'pattern': 'TLS Everywhere',
                'implementation': {
                    'protocol': 'TLS 1.3',
                    'certificates': 'Let\'s Encrypt',
                    'ciphers': '強力な暗号スイート'
                }
            },
            'secure_storage': {
                'pattern': 'Encrypted Storage',
                'implementation': {
                    'encryption': 'AES-256-GCM',
                    'key_management': 'HSM',
                    'access_control': 'RBAC'
                }
            },
            'secure_authentication': {
                'pattern': 'Multi-Factor Authentication',
                'implementation': {
                    'factors': [
                        'パスワード',
                        'ワンタイムパスワード',
                        '生体認証'
                    ],
                    'session_management': 'セキュアセッション'
                }
            }
        }
```

## 5. APIエラー応答

エラー応答は以下の形式に統一してください：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "ユーザー向けエラーメッセージ",
    "details": {
      "field": "エラーが発生したフィールド（該当する場合）",
      "reason": "詳細な理由（該当する場合）"
    }
  },
  "request_id": "リクエスト識別子"
}
```
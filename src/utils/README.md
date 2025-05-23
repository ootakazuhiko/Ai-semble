# ユーティリティモジュール

このディレクトリには、プロジェクト全体で共有される汎用的なユーティリティ機能が含まれています。各モジュールは特定の機能セットを提供し、他のサービスやコンポーネントから再利用できます。

## モジュール一覧

### data_security.py

データセキュリティに関連するユーティリティを提供します。

#### 主な機能

- **データマスキング**: 機密データを自動的にマスキングするための機能
  ```python
  from src.utils.data_security import mask_sensitive_data
  
  # 機密データのマスキング
  masked_data = mask_sensitive_data(sensitive_data)
  ```

- **暗号化ユーティリティ**: データの暗号化と復号化のための便利な関数
  ```python
  from src.utils.data_security import encrypt_data, decrypt_data
  
  # データの暗号化
  encrypted = encrypt_data(original_data)
  
  # データの復号化
  decrypted = decrypt_data(encrypted)
  ```

- **機密データ検出**: テキストに機密情報が含まれているかを確認
  ```python
  from src.utils.data_security import is_sensitive_data
  
  if is_sensitive_data(text):
      print("機密情報が含まれています")
  ```

- **動的マスキング**: ユーザーのコンテキスト（ロールなど）に基づいてマスキングレベルを調整
  ```python
  from src.utils.data_security import DynamicMasking
  
  dynamic_masking = DynamicMasking()
  masked_for_user = dynamic_masking.apply_dynamic_masking(data, user_context)
  ```

## 使用方法

### 推奨されるインポート方法

```python
# 特定の関数だけをインポート（推奨）
from src.utils.data_security import mask_sensitive_data, encrypt_data

# または特定のクラスをインポート
from src.utils.data_security import DataMasking
```

### セキュリティのベストプラクティス

ユーティリティを使用する際は、[共通セキュリティパターン](../../docs/security/common_security_patterns.md)のガイドラインに従うことをお勧めします。

## 拡張方法

新しいユーティリティモジュールを追加する場合は、以下のガイドラインに従ってください：

1. 単一の責任を持つモジュールを作成する
2. 明確なドキュメントとタイプヒントを提供する
3. 適切な例外処理を実装する
4. ユニットテストを作成する
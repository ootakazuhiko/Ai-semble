# クイックスタートガイド

## はじめに

このガイドでは、データセット管理システムの基本的な使用方法を説明します。システムの主要機能を素早く理解し、すぐに使い始めることができます。

## 前提条件

- システムへのアクセス権限
- 有効なユーザーアカウント
- インターネット接続
- モダンブラウザ（Chrome、Firefox、Safari、Edgeの最新版）

## 1. システムへのログイン

1. ブラウザでシステムのURLにアクセスします
2. ユーザー名とパスワードを入力します
3. 「ログイン」ボタンをクリックします

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

## 2. 最初のデータセットの作成

### 2.1 基本的なデータセットの作成

1. 「新規データセット作成」ボタンをクリックします
2. 以下の情報を入力します：
   - データセット名
   - 説明
   - スキーマ情報
   - メタデータ

```http
POST /api/v1/datasets
Content-Type: application/json

{
    "name": "my_first_dataset",
    "description": "初めてのデータセット",
    "schema": {
        "columns": [
            {
                "name": "id",
                "type": "integer",
                "nullable": false,
                "description": "主キー"
            },
            {
                "name": "name",
                "type": "string",
                "nullable": false,
                "description": "名前"
            }
        ]
    },
    "metadata": {
        "tags": ["サンプル", "テスト"],
        "owner": "your_username",
        "access_level": "private"
    }
}
```

### 2.2 データセットの検索

作成したデータセットを検索するには：

```http
GET /api/v1/datasets?query=my_first_dataset
```

## 3. データセットの管理

### 3.1 バージョン管理

データセットの新しいバージョンを作成：

```http
POST /api/v1/datasets/{dataset_id}/versions
Content-Type: application/json

{
    "version": "1.1.0",
    "description": "初回アップデート",
    "changes": "スキーマの更新"
}
```

### 3.2 メタデータの管理

データセットのメタデータを更新：

```http
PUT /api/v1/datasets/{dataset_id}
Content-Type: application/json

{
    "metadata": {
        "tags": ["サンプル", "テスト", "更新済み"],
        "access_level": "public"
    }
}
```

## 4. データ品質の確認

データセットの品質指標を確認：

```http
GET /api/v1/datasets/{dataset_id}/quality
```

## 5. よくある操作

### 5.1 データセットの共有

他のユーザーとデータセットを共有：

```http
POST /api/v1/datasets/{dataset_id}/access
Content-Type: application/json

{
    "user_id": "target_user",
    "permission": "read",
    "expires_at": "2024-12-31T23:59:59Z"
}
```

### 5.2 監査ログの確認

自分の操作履歴を確認：

```http
GET /api/v1/audit-logs?user_id=your_username
```

## 6. トラブルシューティング

### 6.1 よくある問題

1. ログインできない場合
   - パスワードが正しいか確認
   - アカウントがロックされていないか確認
   - 管理者に連絡

2. データセットが表示されない場合
   - アクセス権限を確認
   - 検索条件を確認
   - ページネーションを確認

3. アップロードが失敗する場合
   - ファイルサイズの制限を確認
   - スキーマ定義を確認
   - ネットワーク接続を確認

### 6.2 サポートへの連絡

問題が解決しない場合は、以下の情報を添えてサポートに連絡してください：

- エラーメッセージ
- 操作手順
- 発生時刻
- ブラウザ情報
- スクリーンショット（可能な場合）

## 7. 次のステップ

- [詳細なユーザーガイド](guide.md)を読む
- [トラブルシューティングガイド](troubleshooting.md)を参照
- 管理者に連絡して追加の権限をリクエスト
- 定期的なバックアップの設定を確認

## 8. 便利なショートカット

| 操作 | ショートカット |
|------|----------------|
| 新規データセット作成 | Ctrl + N |
| 検索 | Ctrl + F |
| 更新 | Ctrl + R |
| ヘルプ | F1 |

## 9. 制限事項

- 1つのデータセットの最大サイズ: 1GB
- 同時アップロード可能なファイル数: 5
- 1分あたりの最大リクエスト数: 60
- セッションタイムアウト: 30分

## 10. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-20 | 1.0.0 | 初版リリース |
| 2024-03-21 | 1.0.1 | トラブルシューティングセクション追加 | 
# データセット管理機能 API仕様書

## 概要

このAPIは、データセットの作成、更新、削除、検索、バージョン管理などの基本操作を提供します。各エンドポイントは認証が必要で、JSON形式での入出力をサポートしています。

## 共通仕様

### 認証

すべてのエンドポイントは認証が必要です。認証にはBearerトークンを使用します：

```http
Authorization: Bearer <access_token>
```

### エラーレスポンス

エラーが発生した場合、以下の形式でレスポンスが返されます：

```json
{
    "detail": "エラーメッセージ"
}
```

主なステータスコード：
- 200: 成功
- 201: 作成成功
- 400: リクエストエラー
- 401: 認証エラー
- 403: アクセス権限エラー
- 404: リソースが見つからない
- 409: 競合エラー

## エンドポイント

### 1. データセット作成

新しいデータセットを作成します。

```http
POST /api/v1/datasets
```

#### リクエストボディ

```json
{
    "name": "string",
    "description": "string",
    "schema": {
        "columns": [
            {
                "name": "string",
                "type": "string",
                "nullable": boolean,
                "description": "string"
            }
        ]
    },
    "metadata": {
        "tags": ["string"],
        "owner": "string",
        "access_level": "string"
    }
}
```

#### レスポンス

```json
{
    "id": "integer",
    "name": "string",
    "version": "string",
    "created_at": "string",
    "updated_at": "string",
    "status": "string"
}
```

### 2. データセット更新

既存のデータセットを更新します。

```http
PUT /api/v1/datasets/{dataset_id}
```

#### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

#### リクエストボディ

```json
{
    "name": "string",
    "description": "string",
    "metadata": {
        "tags": ["string"],
        "access_level": "string"
    }
}
```

### 3. データセット削除

データセットを削除します。

```http
DELETE /api/v1/datasets/{dataset_id}
```

#### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

### 4. データセット検索

データセットを検索します。

```http
GET /api/v1/datasets
```

#### クエリパラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| query | string | いいえ | 検索クエリ |
| tags | string[] | いいえ | タグによるフィルタリング |
| owner | string | いいえ | 所有者によるフィルタリング |
| access_level | string | いいえ | アクセスレベルによるフィルタリング |
| page | integer | いいえ | ページ番号（デフォルト: 1） |
| per_page | integer | いいえ | 1ページあたりの件数（デフォルト: 20） |

#### レスポンス

```json
{
    "items": [
        {
            "id": "integer",
            "name": "string",
            "version": "string",
            "description": "string",
            "metadata": {
                "tags": ["string"],
                "owner": "string",
                "access_level": "string"
            },
            "created_at": "string",
            "updated_at": "string"
        }
    ],
    "total": "integer",
    "page": "integer",
    "per_page": "integer"
}
```

### 5. バージョン管理

#### 5.1 バージョン作成

データセットの新しいバージョンを作成します。

```http
POST /api/v1/datasets/{dataset_id}/versions
```

#### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

#### リクエストボディ

```json
{
    "version": "string",
    "description": "string",
    "changes": "string"
}
```

#### 5.2 バージョン一覧取得

データセットのバージョン一覧を取得します。

```http
GET /api/v1/datasets/{dataset_id}/versions
```

#### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

#### レスポンス

```json
{
    "versions": [
        {
            "version": "string",
            "description": "string",
            "created_at": "string",
            "created_by": "string",
            "status": "string"
        }
    ]
}
```

## 制限事項

1. リクエスト制限
   - 1分あたり最大60リクエスト
   - 同時実行は最大10リクエスト

2. データセットサイズ
   - 1つのデータセットの最大サイズは1GB
   - 1つのバージョンの最大行数は1,000,000行

3. メタデータ
   - タグは最大10個まで
   - 説明文は最大1,000文字まで

## エラーコード一覧

| エラーコード | 説明 | 対処方法 |
|------------|------|------------|
| 400 | リクエストが不正です | リクエストボディを確認してください |
| 400 | スキーマが不正です | スキーマ定義を確認してください |
| 401 | 認証が必要です | 有効なアクセストークンを設定してください |
| 403 | アクセス権限がありません | データセットへのアクセス権限を確認してください |
| 404 | データセットが存在しません | 正しいデータセットIDを指定してください |
| 409 | バージョンが競合しています | 最新のバージョンを確認してください |
| 413 | リクエストが大きすぎます | データセットのサイズを確認してください |
| 429 | リクエストが多すぎます | リクエスト頻度を下げてください | 
# メタデータ管理機能 API仕様書

## 概要

このAPIは、データセットのメタデータ管理機能を提供します。スキーマ定義、データ品質情報、データ系譜（データの由来や変換履歴）などの管理を含みます。

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

## エンドポイント

### 1. スキーマ管理

#### 1.1 スキーマ定義の取得

データセットのスキーマ定義を取得します。

```http
GET /api/v1/datasets/{dataset_id}/schema
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| version | string | いいえ | バージョン（指定がない場合は最新版） |

##### レスポンス

```json
{
    "version": "string",
    "columns": [
        {
            "name": "string",
            "type": "string",
            "nullable": "boolean",
            "description": "string",
            "constraints": {
                "unique": "boolean",
                "primary_key": "boolean",
                "foreign_key": {
                    "reference_table": "string",
                    "reference_column": "string"
                }
            },
            "statistics": {
                "distinct_count": "integer",
                "null_count": "integer",
                "min_value": "any",
                "max_value": "any"
            }
        }
    ],
    "created_at": "string",
    "updated_at": "string"
}
```

#### 1.2 スキーマ定義の更新

データセットのスキーマ定義を更新します。

```http
PUT /api/v1/datasets/{dataset_id}/schema
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

##### リクエストボディ

```json
{
    "columns": [
        {
            "name": "string",
            "type": "string",
            "nullable": "boolean",
            "description": "string",
            "constraints": {
                "unique": "boolean",
                "primary_key": "boolean",
                "foreign_key": {
                    "reference_table": "string",
                    "reference_column": "string"
                }
            }
        }
    ]
}
```

### 2. データ品質管理

#### 2.1 品質指標の取得

データセットの品質指標を取得します。

```http
GET /api/v1/datasets/{dataset_id}/quality
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| version | string | いいえ | バージョン（指定がない場合は最新版） |

##### レスポンス

```json
{
    "version": "string",
    "metrics": {
        "completeness": {
            "score": "float",
            "details": {
                "null_ratio": "float",
                "empty_ratio": "float"
            }
        },
        "consistency": {
            "score": "float",
            "details": {
                "constraint_violations": "integer",
                "data_type_errors": "integer"
            }
        },
        "accuracy": {
            "score": "float",
            "details": {
                "format_errors": "integer",
                "range_violations": "integer"
            }
        },
        "timeliness": {
            "score": "float",
            "details": {
                "last_updated": "string",
                "update_frequency": "string"
            }
        }
    },
    "created_at": "string",
    "updated_at": "string"
}
```

#### 2.2 品質チェックの実行

データセットの品質チェックを実行します。

```http
POST /api/v1/datasets/{dataset_id}/quality/check
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

##### リクエストボディ

```json
{
    "checks": [
        {
            "type": "string",
            "parameters": "object"
        }
    ]
}
```

### 3. データ系譜管理

#### 3.1 系譜情報の取得

データセットの系譜情報を取得します。

```http
GET /api/v1/datasets/{dataset_id}/lineage
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| depth | integer | いいえ | 取得する系譜の深さ（デフォルト: 1） |

##### レスポンス

```json
{
    "dataset_id": "integer",
    "lineage": {
        "upstream": [
            {
                "dataset_id": "integer",
                "relationship": "string",
                "transformation": "string",
                "timestamp": "string"
            }
        ],
        "downstream": [
            {
                "dataset_id": "integer",
                "relationship": "string",
                "transformation": "string",
                "timestamp": "string"
            }
        ]
    }
}
```

#### 3.2 系譜情報の更新

データセットの系譜情報を更新します。

```http
POST /api/v1/datasets/{dataset_id}/lineage
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

##### リクエストボディ

```json
{
    "upstream": [
        {
            "dataset_id": "integer",
            "relationship": "string",
            "transformation": "string"
        }
    ],
    "downstream": [
        {
            "dataset_id": "integer",
            "relationship": "string",
            "transformation": "string"
        }
    ]
}
```

### 4. メタデータ検索

#### 4.1 メタデータ検索

メタデータに基づいてデータセットを検索します。

```http
GET /api/v1/metadata/search
```

##### クエリパラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| query | string | いいえ | 検索クエリ |
| schema | object | いいえ | スキーマ条件 |
| quality | object | いいえ | 品質指標条件 |
| lineage | object | いいえ | 系譜条件 |
| page | integer | いいえ | ページ番号（デフォルト: 1） |
| per_page | integer | いいえ | 1ページあたりの件数（デフォルト: 20） |

##### レスポンス

```json
{
    "items": [
        {
            "dataset_id": "integer",
            "name": "string",
            "version": "string",
            "schema": "object",
            "quality_metrics": "object",
            "lineage": "object",
            "created_at": "string",
            "updated_at": "string"
        }
    ],
    "total": "integer",
    "page": "integer",
    "per_page": "integer"
}
```

## 制限事項

1. スキーマ定義
   - カラム名の最大長: 64文字
   - カラム説明の最大長: 1,000文字
   - 1つのデータセットの最大カラム数: 1,000

2. 品質指標
   - 品質チェックの最大実行時間: 30分
   - 品質指標の保持期間: 90日
   - 同時実行可能な品質チェック数: 5

3. データ系譜
   - 系譜の最大深さ: 10
   - 1つのデータセットの最大関連数: 100
   - 系譜情報の保持期間: 365日

## エラーコード一覧

| エラーコード | 説明 | 対処方法 |
|------------|------|------------|
| 400 | リクエストが不正です | リクエストボディを確認してください |
| 400 | スキーマ定義が不正です | スキーマ定義を確認してください |
| 400 | 品質チェックのパラメーターが不正です | パラメーターを確認してください |
| 401 | 認証が必要です | 有効なアクセストークンを設定してください |
| 403 | アクセス権限がありません | データセットへのアクセス権限を確認してください |
| 404 | データセットが存在しません | 正しいデータセットIDを指定してください |
| 409 | スキーマの競合があります | 最新のスキーマを確認してください |
| 413 | リクエストが大きすぎます | リクエストのサイズを確認してください |
| 429 | リクエストが多すぎます | リクエスト頻度を下げてください | 
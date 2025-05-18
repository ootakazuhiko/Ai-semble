# データセット可視化機能 API仕様書

## 概要

このAPIは、データセットの統計情報、バージョン比較、品質指標を可視化するためのエンドポイントを提供します。各エンドポイントは認証が必要で、JSONまたはHTML形式での出力をサポートしています。

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
- 400: リクエストエラー（データセットが存在しない、バージョンが無効など）
- 401: 認証エラー
- 403: アクセス権限エラー

### 出力形式

各エンドポイントは以下の出力形式をサポートしています：

- `json`: PlotlyのJSON形式でグラフデータを返す
- `html`: インタラクティブなHTMLファイルとして出力

## エンドポイント

### 1. 統計情報ダッシュボード取得

データセットの統計情報を可視化したダッシュボードを取得します。

```http
GET /api/v1/visualization/datasets/{dataset_id}/statistics
```

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| version | string | いいえ | バージョン（指定しない場合は最新バージョン） |
| output_format | string | いいえ | 出力形式（"json" または "html"、デフォルト: "json"） |
| output_path | string | いいえ | 出力先のパス（指定しない場合はレスポンスとして返す） |

#### レスポンス

JSON形式の場合：
```json
{
    "figure": {
        "data": [...],
        "layout": {...}
    }
}
```

HTML形式の場合：
```json
{
    "output_path": "/path/to/output.html"
}
```

#### 使用例

```bash
# JSON形式で取得
curl -X GET "http://localhost:8000/api/v1/visualization/datasets/1/statistics" \
     -H "Authorization: Bearer <token>"

# HTML形式で取得
curl -X GET "http://localhost:8000/api/v1/visualization/datasets/1/statistics?output_format=html&output_path=/tmp/dashboard.html" \
     -H "Authorization: Bearer <token>"
```

### 2. バージョン比較ダッシュボード取得

2つのバージョン間の統計情報と品質指標を比較したダッシュボードを取得します。

```http
GET /api/v1/visualization/datasets/{dataset_id}/version-comparison
```

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| version1 | string | はい | 比較元のバージョン |
| version2 | string | はい | 比較先のバージョン |
| output_format | string | いいえ | 出力形式（"json" または "html"、デフォルト: "json"） |
| output_path | string | いいえ | 出力先のパス（指定しない場合はレスポンスとして返す） |

#### レスポンス

JSON形式の場合：
```json
{
    "figure": {
        "data": [...],
        "layout": {...}
    }
}
```

HTML形式の場合：
```json
{
    "output_path": "/path/to/output.html"
}
```

#### 使用例

```bash
# JSON形式で取得
curl -X GET "http://localhost:8000/api/v1/visualization/datasets/1/version-comparison?version1=1.0.0&version2=1.0.1" \
     -H "Authorization: Bearer <token>"

# HTML形式で取得
curl -X GET "http://localhost:8000/api/v1/visualization/datasets/1/version-comparison?version1=1.0.0&version2=1.0.1&output_format=html&output_path=/tmp/comparison.html" \
     -H "Authorization: Bearer <token>"
```

### 3. 品質指標ダッシュボード取得

データセットの品質指標の時系列推移と列ごとの完全性指標を可視化したダッシュボードを取得します。

```http
GET /api/v1/visualization/datasets/{dataset_id}/quality-metrics
```

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| output_format | string | いいえ | 出力形式（"json" または "html"、デフォルト: "json"） |
| output_path | string | いいえ | 出力先のパス（指定しない場合はレスポンスとして返す） |

#### レスポンス

JSON形式の場合：
```json
{
    "figure": {
        "data": [...],
        "layout": {...}
    }
}
```

HTML形式の場合：
```json
{
    "output_path": "/path/to/output.html"
}
```

#### 使用例

```bash
# JSON形式で取得
curl -X GET "http://localhost:8000/api/v1/visualization/datasets/1/quality-metrics" \
     -H "Authorization: Bearer <token>"

# HTML形式で取得
curl -X GET "http://localhost:8000/api/v1/visualization/datasets/1/quality-metrics?output_format=html&output_path=/tmp/quality.html" \
     -H "Authorization: Bearer <token>"
```

### 4. 統計情報の再計算

データセットの統計情報と品質指標を再計算します。

```http
POST /api/v1/visualization/datasets/{dataset_id}/statistics/refresh
```

#### パラメータ

| パラメータ | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| version | string | いいえ | バージョン（指定しない場合は最新バージョン） |

#### レスポンス

```json
{
    "statistics": {
        "numeric": {...},
        "categorical": {...}
    },
    "quality_metrics": {
        "completeness": {...},
        "uniqueness": {...}
    }
}
```

#### 使用例

```bash
# 統計情報を再計算
curl -X POST "http://localhost:8000/api/v1/visualization/datasets/1/statistics/refresh?version=1.0.0" \
     -H "Authorization: Bearer <token>"
```

## 制限事項

1. 出力ファイルサイズ
   - HTML形式の出力ファイルは最大10MBまで
   - JSON形式のレスポンスは最大5MBまで

2. リクエスト制限
   - 1分あたり最大60リクエスト
   - 同時実行は最大10リクエスト

3. データセットサイズ
   - 1つのデータセットの最大サイズは1GB
   - 1つのバージョンの最大行数は1,000,000行

## エラーコード一覧

| エラーコード | 説明 | 対処方法 |
|------------|------|------------|
| 400 | データセットが存在しません | 正しいデータセットIDを指定してください |
| 400 | 指定されたバージョンが存在しません | 正しいバージョンを指定してください |
| 400 | 出力パスが無効です | 書き込み可能なパスを指定してください |
| 401 | 認証が必要です | 有効なアクセストークンを設定してください |
| 403 | アクセス権限がありません | データセットへのアクセス権限を確認してください |
| 413 | リクエストが大きすぎます | データセットのサイズを確認してください |
| 429 | リクエストが多すぎます | リクエスト頻度を下げてください | 
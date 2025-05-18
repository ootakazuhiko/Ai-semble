# セキュリティ機能 API仕様書

## 概要

このAPIは、データセット管理システムのセキュリティ機能を提供します。認証、認可、アクセス制御、監査ログなどの機能を含みます。

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

### 1. 認証

#### 1.1 ログイン

ユーザー認証を行い、アクセストークンを取得します。

```http
POST /api/v1/auth/login
```

##### リクエストボディ

```json
{
    "username": "string",
    "password": "string"
}
```

##### レスポンス

```json
{
    "access_token": "string",
    "token_type": "Bearer",
    "expires_in": "integer",
    "refresh_token": "string"
}
```

#### 1.2 トークン更新

リフレッシュトークンを使用して新しいアクセストークンを取得します。

```http
POST /api/v1/auth/refresh
```

##### リクエストボディ

```json
{
    "refresh_token": "string"
}
```

##### レスポンス

```json
{
    "access_token": "string",
    "token_type": "Bearer",
    "expires_in": "integer"
}
```

### 2. アクセス制御

#### 2.1 アクセス権限の付与

データセットへのアクセス権限を付与します。

```http
POST /api/v1/datasets/{dataset_id}/access
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |

##### リクエストボディ

```json
{
    "user_id": "string",
    "permission": "string",
    "expires_at": "string"
}
```

#### 2.2 アクセス権限の削除

データセットへのアクセス権限を削除します。

```http
DELETE /api/v1/datasets/{dataset_id}/access/{user_id}
```

##### パラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| dataset_id | integer | はい | データセットID |
| user_id | string | はい | ユーザーID |

### 3. 監査ログ

#### 3.1 監査ログの取得

システムの監査ログを取得します。

```http
GET /api/v1/audit-logs
```

##### クエリパラメーター

| パラメーター | 型 | 必須 | 説明 |
|------------|------|--------|------------|
| start_date | string | いいえ | 開始日時 |
| end_date | string | いいえ | 終了日時 |
| user_id | string | いいえ | ユーザーID |
| action | string | いいえ | アクション種別 |
| resource_type | string | いいえ | リソース種別 |
| resource_id | string | いいえ | リソースID |
| page | integer | いいえ | ページ番号（デフォルト: 1） |
| per_page | integer | いいえ | 1ページあたりの件数（デフォルト: 20） |

##### レスポンス

```json
{
    "items": [
        {
            "id": "integer",
            "timestamp": "string",
            "user_id": "string",
            "action": "string",
            "resource_type": "string",
            "resource_id": "string",
            "details": "object",
            "ip_address": "string"
        }
    ],
    "total": "integer",
    "page": "integer",
    "per_page": "integer"
}
```

### 4. セキュリティ設定

#### 4.1 パスワードポリシーの取得

現在のパスワードポリシーを取得します。

```http
GET /api/v1/security/password-policy
```

##### レスポンス

```json
{
    "min_length": "integer",
    "require_uppercase": "boolean",
    "require_lowercase": "boolean",
    "require_numbers": "boolean",
    "require_special_chars": "boolean",
    "max_age_days": "integer",
    "history_count": "integer"
}
```

#### 4.2 セッション設定の取得

現在のセッション設定を取得します。

```http
GET /api/v1/security/session-settings
```

##### レスポンス

```json
{
    "session_timeout_minutes": "integer",
    "max_failed_attempts": "integer",
    "lockout_duration_minutes": "integer",
    "require_mfa": "boolean"
}
```

## セキュリティ要件

1. パスワード要件
   - 最小長: 12文字
   - 大文字必須
   - 小文字必須
   - 数字必須
   - 特殊文字必須
   - 90日ごとの変更必須
   - 過去5回分のパスワードは再利用不可

2. セッション管理
   - セッションタイムアウト: 30分
   - 最大ログイン試行回数: 5回
   - アカウントロックアウト時間: 30分
   - 重要な操作にはMFA必須

3. アクセス制御
   - 最小権限の原則に基づく権限管理
   - ロールベースのアクセス制御（RBAC）
   - リソースベースのアクセス制御

4. 監査ログ
   - すべての認証試行を記録
   - 重要な操作の監査ログを保持（90日間）
   - ログの改ざん防止

## エラーコード一覧

| エラーコード | 説明 | 対処方法 |
|------------|------|------------|
| 400 | リクエストが不正です | リクエストボディを確認してください |
| 401 | 認証が必要です | 有効なアクセストークンを設定してください |
| 401 | トークンが無効です | 再ログインしてください |
| 401 | トークンの有効期限が切れています | トークンを更新してください |
| 403 | アクセス権限がありません | 必要な権限を確認してください |
| 403 | アカウントがロックされています | 管理者に連絡してください |
| 429 | ログイン試行回数が多すぎます | しばらく待ってから再試行してください | 
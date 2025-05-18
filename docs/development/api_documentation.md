# APIドキュメント

## 目次

1. [はじめに](#1-はじめに)
2. [API概要](#2-api概要)
3. [認証と認可](#3-認証と認可)
4. [エンドポイント](#4-エンドポイント)
5. [データモデル](#5-データモデル)
6. [エラーハンドリング](#6-エラーハンドリング)
7. [レート制限](#7-レート制限)

## 1. はじめに

このドキュメントは、データセット管理システムのAPI仕様を定義するものです。システムの機能にアクセスするためのインターフェースを提供します。

### 1.1 目的

- APIの標準化
- 開発者向けガイドラインの提供
- システム間連携の促進
- セキュリティの確保
- 運用性の向上

### 1.2 適用範囲

- RESTful API
- GraphQL API
- WebSocket API
- バッチ処理API

## 2. API概要

### 2.1 基本情報

```python
# API基本情報
class APIOverview:
    def __init__(self):
        self.overview = {
            'base_url': {
                'production': 'https://api.example.com/v1',
                'staging': 'https://api-staging.example.com/v1',
                'development': 'https://api-dev.example.com/v1'
            },
            'versions': {
                'current': 'v1',
                'supported': ['v1'],
                'deprecated': [],
                'sunset': []
            },
            'formats': {
                'request': [
                    'application/json',
                    'multipart/form-data'
                ],
                'response': [
                    'application/json'
                ]
            },
            'character_encoding': 'UTF-8',
            'timezone': 'Asia/Tokyo'
        }
```

### 2.2 API設計原則

```python
# API設計原則
class APIDesignPrinciples:
    def __init__(self):
        self.principles = {
            'restful': {
                'methods': {
                    'GET': 'リソースの取得',
                    'POST': 'リソースの作成',
                    'PUT': 'リソースの更新',
                    'PATCH': 'リソースの部分更新',
                    'DELETE': 'リソースの削除'
                },
                'url_structure': {
                    'pattern': '/{resource}/{id}/{sub-resource}',
                    'examples': [
                        '/datasets',
                        '/datasets/{id}',
                        '/datasets/{id}/versions'
                    ]
                }
            },
            'graphql': {
                'operations': {
                    'query': 'データの取得',
                    'mutation': 'データの変更',
                    'subscription': 'リアルタイム更新'
                },
                'schema': {
                    'types': '強力な型システム',
                    'introspection': '自己文書化',
                    'validation': '実行前検証'
                }
            },
            'websocket': {
                'events': {
                    'connection': '接続管理',
                    'message': 'メッセージング',
                    'disconnection': '切断処理'
                },
                'protocols': [
                    'ws://',
                    'wss://'
                ]
            }
        }
```

## 3. 認証と認可

### 3.1 認証方式

```python
# 認証方式
class AuthenticationMethods:
    def __init__(self):
        self.methods = {
            'oauth2': {
                'flows': {
                    'authorization_code': {
                        'use_case': 'Webアプリケーション',
                        'security': '高',
                        'refresh_token': '有効'
                    },
                    'client_credentials': {
                        'use_case': 'サーバー間通信',
                        'security': '中',
                        'refresh_token': '無効'
                    },
                    'password': {
                        'use_case': '信頼できるクライアント',
                        'security': '中',
                        'refresh_token': '有効'
                    }
                },
                'tokens': {
                    'access_token': {
                        'type': 'JWT',
                        'lifetime': '1時間',
                        'claims': [
                            'sub',
                            'exp',
                            'scope'
                        ]
                    },
                    'refresh_token': {
                        'type': '不透明トークン',
                        'lifetime': '30日',
                        'storage': '安全なデータベース'
                    }
                }
            },
            'api_key': {
                'format': 'X-API-Key: {key}',
                'storage': '環境変数',
                'rotation': '90日',
                'scope': '特定のAPI'
            },
            'jwt': {
                'format': 'Bearer {token}',
                'algorithm': 'RS256',
                'claims': [
                    'iss',
                    'sub',
                    'exp',
                    'iat'
                ],
                'verification': '公開鍵'
            }
        }
```

### 3.2 認可モデル

```python
# 認可モデル
class AuthorizationModel:
    def __init__(self):
        self.model = {
            'rbac': {
                'roles': {
                    'admin': {
                        'permissions': [
                            'all'
                        ],
                        'scope': 'システム全体'
                    },
                    'user': {
                        'permissions': [
                            'read:own',
                            'write:own'
                        ],
                        'scope': '自身のリソース'
                    },
                    'viewer': {
                        'permissions': [
                            'read:public'
                        ],
                        'scope': '公開リソース'
                    }
                },
                'permissions': {
                    'read': [
                        'GET',
                        'HEAD',
                        'OPTIONS'
                    ],
                    'write': [
                        'POST',
                        'PUT',
                        'PATCH',
                        'DELETE'
                    ]
                }
            },
            'scopes': {
                'dataset': [
                    'dataset:read',
                    'dataset:write',
                    'dataset:delete'
                ],
                'user': [
                    'user:read',
                    'user:write',
                    'user:delete'
                ],
                'system': [
                    'system:read',
                    'system:write',
                    'system:delete'
                ]
            }
        }
```

## 4. エンドポイント

### 4.1 データセットAPI

```python
# データセットAPI
class DatasetAPI:
    def __init__(self):
        self.endpoints = {
            'datasets': {
                'GET /datasets': {
                    'description': 'データセット一覧の取得',
                    'parameters': {
                        'query': {
                            'page': 'ページ番号',
                            'limit': '1ページあたりの件数',
                            'sort': 'ソート順',
                            'filter': 'フィルター条件'
                        }
                    },
                    'responses': {
                        '200': {
                            'description': '成功',
                            'schema': 'DatasetList'
                        },
                        '400': {
                            'description': '不正なリクエスト',
                            'schema': 'Error'
                        },
                        '401': {
                            'description': '未認証',
                            'schema': 'Error'
                        }
                    }
                },
                'POST /datasets': {
                    'description': 'データセットの作成',
                    'parameters': {
                        'body': {
                            'name': 'データセット名',
                            'description': '説明',
                            'metadata': 'メタデータ'
                        }
                    },
                    'responses': {
                        '201': {
                            'description': '作成成功',
                            'schema': 'Dataset'
                        },
                        '400': {
                            'description': '不正なリクエスト',
                            'schema': 'Error'
                        },
                        '401': {
                            'description': '未認証',
                            'schema': 'Error'
                        }
                    }
                }
            },
            'dataset': {
                'GET /datasets/{id}': {
                    'description': 'データセットの取得',
                    'parameters': {
                        'path': {
                            'id': 'データセットID'
                        }
                    },
                    'responses': {
                        '200': {
                            'description': '成功',
                            'schema': 'Dataset'
                        },
                        '404': {
                            'description': 'リソース未検出',
                            'schema': 'Error'
                        }
                    }
                },
                'PUT /datasets/{id}': {
                    'description': 'データセットの更新',
                    'parameters': {
                        'path': {
                            'id': 'データセットID'
                        },
                        'body': {
                            'name': 'データセット名',
                            'description': '説明',
                            'metadata': 'メタデータ'
                        }
                    },
                    'responses': {
                        '200': {
                            'description': '更新成功',
                            'schema': 'Dataset'
                        },
                        '404': {
                            'description': 'リソース未検出',
                            'schema': 'Error'
                        }
                    }
                }
            }
        }
```

### 4.2 ユーザーAPI

```python
# ユーザーAPI
class UserAPI:
    def __init__(self):
        self.endpoints = {
            'users': {
                'GET /users': {
                    'description': 'ユーザー一覧の取得',
                    'parameters': {
                        'query': {
                            'page': 'ページ番号',
                            'limit': '1ページあたりの件数',
                            'role': 'ロールフィルター'
                        }
                    },
                    'responses': {
                        '200': {
                            'description': '成功',
                            'schema': 'UserList'
                        },
                        '403': {
                            'description': '権限なし',
                            'schema': 'Error'
                        }
                    }
                },
                'POST /users': {
                    'description': 'ユーザーの作成',
                    'parameters': {
                        'body': {
                            'username': 'ユーザー名',
                            'email': 'メールアドレス',
                            'password': 'パスワード',
                            'role': 'ロール'
                        }
                    },
                    'responses': {
                        '201': {
                            'description': '作成成功',
                            'schema': 'User'
                        },
                        '400': {
                            'description': '不正なリクエスト',
                            'schema': 'Error'
                        }
                    }
                }
            },
            'user': {
                'GET /users/{id}': {
                    'description': 'ユーザー情報の取得',
                    'parameters': {
                        'path': {
                            'id': 'ユーザーID'
                        }
                    },
                    'responses': {
                        '200': {
                            'description': '成功',
                            'schema': 'User'
                        },
                        '404': {
                            'description': 'リソース未検出',
                            'schema': 'Error'
                        }
                    }
                },
                'PUT /users/{id}': {
                    'description': 'ユーザー情報の更新',
                    'parameters': {
                        'path': {
                            'id': 'ユーザーID'
                        },
                        'body': {
                            'email': 'メールアドレス',
                            'role': 'ロール',
                            'status': 'ステータス'
                        }
                    },
                    'responses': {
                        '200': {
                            'description': '更新成功',
                            'schema': 'User'
                        },
                        '404': {
                            'description': 'リソース未検出',
                            'schema': 'Error'
                        }
                    }
                }
            }
        }
```

## 5. データモデル

### 5.1 共通モデル

```python
# データモデル
class DataModels:
    def __init__(self):
        self.models = {
            'dataset': {
                'id': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'データセットID'
                },
                'name': {
                    'type': 'string',
                    'maxLength': 100,
                    'description': 'データセット名'
                },
                'description': {
                    'type': 'string',
                    'maxLength': 1000,
                    'description': '説明'
                },
                'metadata': {
                    'type': 'object',
                    'properties': {
                        'version': 'string',
                        'created_at': 'datetime',
                        'updated_at': 'datetime',
                        'owner': 'string',
                        'tags': ['string']
                    }
                },
                'status': {
                    'type': 'string',
                    'enum': [
                        'draft',
                        'published',
                        'archived'
                    ]
                }
            },
            'user': {
                'id': {
                    'type': 'string',
                    'format': 'uuid',
                    'description': 'ユーザーID'
                },
                'username': {
                    'type': 'string',
                    'maxLength': 50,
                    'description': 'ユーザー名'
                },
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'description': 'メールアドレス'
                },
                'role': {
                    'type': 'string',
                    'enum': [
                        'admin',
                        'user',
                        'viewer'
                    ]
                },
                'status': {
                    'type': 'string',
                    'enum': [
                        'active',
                        'inactive',
                        'suspended'
                    ]
                }
            }
        }
```

## 6. エラーハンドリング

### 6.1 エラー定義

```python
# エラーハンドリング
class ErrorHandling:
    def __init__(self):
        self.errors = {
            'error_codes': {
                '400': {
                    'code': 'BAD_REQUEST',
                    'message': '不正なリクエストです',
                    'details': 'リクエストの形式が正しくありません'
                },
                '401': {
                    'code': 'UNAUTHORIZED',
                    'message': '認証が必要です',
                    'details': '有効な認証情報を提供してください'
                },
                '403': {
                    'code': 'FORBIDDEN',
                    'message': 'アクセス権限がありません',
                    'details': 'このリソースへのアクセス権限がありません'
                },
                '404': {
                    'code': 'NOT_FOUND',
                    'message': 'リソースが見つかりません',
                    'details': '指定されたリソースは存在しません'
                },
                '429': {
                    'code': 'TOO_MANY_REQUESTS',
                    'message': 'リクエスト制限を超えました',
                    'details': 'レート制限に達しました。しばらく待ってから再試行してください'
                },
                '500': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'サーバーエラーが発生しました',
                    'details': '予期せぬエラーが発生しました'
                }
            },
            'error_response': {
                'format': {
                    'error': {
                        'code': 'エラーコード',
                        'message': 'エラーメッセージ',
                        'details': '詳細情報',
                        'request_id': 'リクエストID'
                    }
                },
                'example': {
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'リソースが見つかりません',
                        'details': '指定されたデータセットは存在しません',
                        'request_id': 'req-123456'
                    }
                }
            }
        }
```

## 7. レート制限

### 7.1 制限設定

```python
# レート制限
class RateLimiting:
    def __init__(self):
        self.limits = {
            'tiers': {
                'free': {
                    'requests_per_minute': 60,
                    'requests_per_hour': 1000,
                    'requests_per_day': 10000
                },
                'standard': {
                    'requests_per_minute': 120,
                    'requests_per_hour': 5000,
                    'requests_per_day': 50000
                },
                'premium': {
                    'requests_per_minute': 300,
                    'requests_per_hour': 15000,
                    'requests_per_day': 150000
                }
            },
            'headers': {
                'X-RateLimit-Limit': '制限値',
                'X-RateLimit-Remaining': '残りリクエスト数',
                'X-RateLimit-Reset': 'リセット時刻'
            },
            'response': {
                '429': {
                    'code': 'TOO_MANY_REQUESTS',
                    'message': 'レート制限を超えました',
                    'retry_after': '再試行までの待機時間（秒）'
                }
            }
        }
```

## 8. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | レート制限セクションの追加 | 
# API仕様書

## 目次

1. [はじめに](#1-はじめに)
2. [API概要](#2-api概要)
3. [認証と認可](#3-認証と認可)
4. [エンドポイント](#4-エンドポイント)
5. [データモデル](#5-データモデル)
6. [エラーハンドリング](#6-エラーハンドリング)
7. [レート制限](#7-レート制限)
8. [更新履歴](#8-更新履歴)

## 1. はじめに

このドキュメントは、データセット管理システムのAPI仕様を定義します。

### 1.1 目的

- APIの標準化
- 開発者向けガイドラインの提供
- システム間連携の促進
- セキュリティ要件の明確化

### 1.2 対象読者

- 開発者
- システムインテグレーター
- セキュリティ担当者
- 運用担当者

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
            'versioning': {
                'current': 'v1',
                'supported': ['v1'],
                'deprecated': [],
                'sunset_policy': '6ヶ月前通知'
            },
            'format': {
                'request': 'JSON',
                'response': 'JSON',
                'encoding': 'UTF-8'
            },
            'documentation': {
                'swagger': '/api-docs',
                'redoc': '/redoc',
                'postman': '/postman-collection'
            }
        }
```

## 3. 認証と認可

### 3.1 認証方式

```python
# 認証と認可
class Authentication:
    def __init__(self):
        self.auth = {
            'methods': {
                'oauth2': {
                    'grant_types': [
                        'authorization_code',
                        'client_credentials',
                        'refresh_token'
                    ],
                    'endpoints': {
                        'authorize': '/oauth/authorize',
                        'token': '/oauth/token',
                        'revoke': '/oauth/revoke'
                    },
                    'scopes': [
                        'read:datasets',
                        'write:datasets',
                        'admin:datasets'
                    ]
                },
                'api_key': {
                    'header': 'X-API-Key',
                    'format': 'UUID',
                    'rotation': '90日'
                }
            },
            'security': {
                'transport': 'TLS 1.2以上',
                'token_lifetime': {
                    'access_token': '1時間',
                    'refresh_token': '30日'
                },
                'password_policy': {
                    'min_length': 12,
                    'complexity': '必須',
                    'history': '5世代'
                }
            },
            'authorization': {
                'rbac': {
                    'roles': [
                        'admin',
                        'editor',
                        'viewer'
                    ],
                    'permissions': [
                        'create',
                        'read',
                        'update',
                        'delete'
                    ]
                },
                'policies': {
                    'ip_restriction': 'オプション',
                    'time_restriction': 'オプション',
                    'mfa': '管理者必須'
                }
            }
        }
```

## 4. エンドポイント

### 4.1 データセット管理

```python
# エンドポイント
class Endpoints:
    def __init__(self):
        self.endpoints = {
            'datasets': {
                'base_path': '/datasets',
                'operations': {
                    'list': {
                        'method': 'GET',
                        'path': '/',
                        'query_params': {
                            'page': 'integer',
                            'per_page': 'integer',
                            'sort': 'string',
                            'filter': 'object'
                        },
                        'response': {
                            '200': {
                                'type': 'array',
                                'items': 'Dataset'
                            }
                        }
                    },
                    'create': {
                        'method': 'POST',
                        'path': '/',
                        'body': 'DatasetCreate',
                        'response': {
                            '201': 'Dataset',
                            '400': 'Error',
                            '401': 'Error',
                            '403': 'Error'
                        }
                    },
                    'get': {
                        'method': 'GET',
                        'path': '/{id}',
                        'path_params': {
                            'id': 'string'
                        },
                        'response': {
                            '200': 'Dataset',
                            '404': 'Error'
                        }
                    },
                    'update': {
                        'method': 'PUT',
                        'path': '/{id}',
                        'path_params': {
                            'id': 'string'
                        },
                        'body': 'DatasetUpdate',
                        'response': {
                            '200': 'Dataset',
                            '400': 'Error',
                            '404': 'Error'
                        }
                    },
                    'delete': {
                        'method': 'DELETE',
                        'path': '/{id}',
                        'path_params': {
                            'id': 'string'
                        },
                        'response': {
                            '204': None,
                            '404': 'Error'
                        }
                    }
                }
            },
            'metadata': {
                'base_path': '/metadata',
                'operations': {
                    'list': {
                        'method': 'GET',
                        'path': '/',
                        'query_params': {
                            'dataset_id': 'string',
                            'type': 'string'
                        },
                        'response': {
                            '200': {
                                'type': 'array',
                                'items': 'Metadata'
                            }
                        }
                    },
                    'update': {
                        'method': 'PUT',
                        'path': '/{id}',
                        'path_params': {
                            'id': 'string'
                        },
                        'body': 'MetadataUpdate',
                        'response': {
                            '200': 'Metadata',
                            '400': 'Error',
                            '404': 'Error'
                        }
                    }
                }
            },
            'search': {
                'base_path': '/search',
                'operations': {
                    'query': {
                        'method': 'POST',
                        'path': '/',
                        'body': 'SearchQuery',
                        'response': {
                            '200': 'SearchResults',
                            '400': 'Error'
                        }
                    },
                    'suggest': {
                        'method': 'GET',
                        'path': '/suggest',
                        'query_params': {
                            'q': 'string',
                            'limit': 'integer'
                        },
                        'response': {
                            '200': {
                                'type': 'array',
                                'items': 'string'
                            }
                        }
                    }
                }
            }
        }
```

## 5. データモデル

### 5.1 モデル定義

```python
# データモデル
class DataModels:
    def __init__(self):
        self.models = {
            'Dataset': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                        'description': 'データセットの一意識別子'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'データセット名'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'データセットの説明'
                    },
                    'version': {
                        'type': 'string',
                        'format': 'semver',
                        'description': 'バージョン番号'
                    },
                    'status': {
                        'type': 'string',
                        'enum': [
                            'draft',
                            'published',
                            'archived'
                        ],
                        'description': 'データセットの状態'
                    },
                    'metadata': {
                        'type': 'object',
                        'properties': {
                            'created_at': {
                                'type': 'string',
                                'format': 'date-time'
                            },
                            'updated_at': {
                                'type': 'string',
                                'format': 'date-time'
                            },
                            'owner': {
                                'type': 'string'
                            },
                            'tags': {
                                'type': 'array',
                                'items': {
                                    'type': 'string'
                                }
                            }
                        }
                    }
                },
                'required': [
                    'id',
                    'name',
                    'version',
                    'status'
                ]
            },
            'Metadata': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'dataset_id': {
                        'type': 'string',
                        'format': 'uuid'
                    },
                    'key': {
                        'type': 'string'
                    },
                    'value': {
                        'type': 'string'
                    },
                    'type': {
                        'type': 'string',
                        'enum': [
                            'string',
                            'number',
                            'boolean',
                            'date'
                        ]
                    }
                },
                'required': [
                    'id',
                    'dataset_id',
                    'key',
                    'value',
                    'type'
                ]
            },
            'SearchQuery': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string'
                    },
                    'filters': {
                        'type': 'object'
                    },
                    'sort': {
                        'type': 'object'
                    },
                    'page': {
                        'type': 'integer',
                        'minimum': 1
                    },
                    'per_page': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 100
                    }
                },
                'required': [
                    'query'
                ]
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
            'codes': {
                '400': {
                    'name': 'Bad Request',
                    'description': 'リクエストの形式が不正'
                },
                '401': {
                    'name': 'Unauthorized',
                    'description': '認証が必要'
                },
                '403': {
                    'name': 'Forbidden',
                    'description': 'アクセス権限がない'
                },
                '404': {
                    'name': 'Not Found',
                    'description': 'リソースが存在しない'
                },
                '409': {
                    'name': 'Conflict',
                    'description': 'リソースの競合'
                },
                '422': {
                    'name': 'Unprocessable Entity',
                    'description': 'バリデーションエラー'
                },
                '429': {
                    'name': 'Too Many Requests',
                    'description': 'レート制限超過'
                },
                '500': {
                    'name': 'Internal Server Error',
                    'description': 'サーバー内部エラー'
                }
            },
            'format': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'string'
                    },
                    'message': {
                        'type': 'string'
                    },
                    'details': {
                        'type': 'object'
                    },
                    'request_id': {
                        'type': 'string'
                    }
                }
            },
            'handling': {
                'retry': {
                    'eligible_codes': [
                        429,
                        500,
                        502,
                        503,
                        504
                    ],
                    'max_attempts': 3,
                    'backoff': 'exponential'
                },
                'logging': {
                    'level': {
                        '4xx': 'warn',
                        '5xx': 'error'
                    },
                    'fields': [
                        'request_id',
                        'error_code',
                        'message',
                        'stack_trace'
                    ]
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
                'basic': {
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
                'limit': 'X-RateLimit-Limit',
                'remaining': 'X-RateLimit-Remaining',
                'reset': 'X-RateLimit-Reset'
            },
            'response': {
                'status_code': 429,
                'body': {
                    'code': 'rate_limit_exceeded',
                    'message': 'レート制限を超過しました',
                    'retry_after': 'integer'
                }
            },
            'exemptions': {
                'endpoints': [
                    '/health',
                    '/metrics'
                ],
                'ips': [
                    '内部ネットワーク',
                    '管理用IP'
                ]
            }
        }
```

## 8. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | レート制限の追加 | 
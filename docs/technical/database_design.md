# データベース設計書

## 目次

1. [はじめに](#1-はじめに)
2. [データベース概要](#2-データベース概要)
3. [論理設計](#3-論理設計)
4. [物理設計](#4-物理設計)
5. [インデックス設計](#5-インデックス設計)
6. [バックアップとリカバリ](#6-バックアップとリカバリ)
7. [更新履歴](#7-更新履歴)

## 1. はじめに

このドキュメントは、データセット管理システムのデータベース設計を定義します。

### 1.1 目的

- データベース構造の標準化
- データモデルの明確な定義
- パフォーマンス要件の達成
- データ整合性の確保

### 1.2 対象読者

- データベース管理者
- アプリケーション開発者
- システムアーキテクト
- 運用担当者

## 2. データベース概要

### 2.1 システム構成

```python
# データベースシステム構成
class DatabaseSystem:
    def __init__(self):
        self.configuration = {
            'primary': {
                'type': 'PostgreSQL',
                'version': '15.0',
                'purpose': 'メインデータベース',
                'features': [
                    'トランザクション管理',
                    'ACID準拠',
                    'JSONサポート',
                    'パーティショニング'
                ]
            },
            'cache': {
                'type': 'Redis',
                'version': '7.0',
                'purpose': 'キャッシュ層',
                'features': [
                    'インメモリキャッシュ',
                    'セッション管理',
                    'ジョブキュー'
                ]
            },
            'search': {
                'type': 'Elasticsearch',
                'version': '8.0',
                'purpose': '検索エンジン',
                'features': [
                    'フルテキスト検索',
                    'アグリゲーション',
                    'リアルタイム分析'
                ]
            }
        }
```

## 3. 論理設計

### 3.1 エンティティ定義

```python
# エンティティ定義
class EntityDefinitions:
    def __init__(self):
        self.entities = {
            'users': {
                'description': 'システムユーザー情報',
                'attributes': {
                    'id': {
                        'type': 'UUID',
                        'constraint': 'PRIMARY KEY',
                        'description': 'ユーザーID'
                    },
                    'username': {
                        'type': 'VARCHAR(50)',
                        'constraint': 'UNIQUE NOT NULL',
                        'description': 'ユーザー名'
                    },
                    'email': {
                        'type': 'VARCHAR(255)',
                        'constraint': 'UNIQUE NOT NULL',
                        'description': 'メールアドレス'
                    },
                    'password_hash': {
                        'type': 'VARCHAR(255)',
                        'constraint': 'NOT NULL',
                        'description': 'パスワードハッシュ'
                    },
                    'role': {
                        'type': 'VARCHAR(20)',
                        'constraint': 'NOT NULL',
                        'description': 'ユーザーロール'
                    },
                    'status': {
                        'type': 'VARCHAR(20)',
                        'constraint': 'NOT NULL',
                        'description': 'アカウント状態'
                    },
                    'created_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '作成日時'
                    },
                    'updated_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '更新日時'
                    }
                }
            },
            'datasets': {
                'description': 'データセット情報',
                'attributes': {
                    'id': {
                        'type': 'UUID',
                        'constraint': 'PRIMARY KEY',
                        'description': 'データセットID'
                    },
                    'name': {
                        'type': 'VARCHAR(255)',
                        'constraint': 'NOT NULL',
                        'description': 'データセット名'
                    },
                    'description': {
                        'type': 'TEXT',
                        'constraint': 'NULL',
                        'description': '説明'
                    },
                    'format': {
                        'type': 'VARCHAR(20)',
                        'constraint': 'NOT NULL',
                        'description': 'データフォーマット'
                    },
                    'owner_id': {
                        'type': 'UUID',
                        'constraint': 'FOREIGN KEY',
                        'description': '所有者ID'
                    },
                    'metadata': {
                        'type': 'JSONB',
                        'constraint': 'NULL',
                        'description': 'メタデータ'
                    },
                    'status': {
                        'type': 'VARCHAR(20)',
                        'constraint': 'NOT NULL',
                        'description': 'データセット状態'
                    },
                    'created_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '作成日時'
                    },
                    'updated_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '更新日時'
                    }
                }
            },
            'versions': {
                'description': 'データセットバージョン情報',
                'attributes': {
                    'id': {
                        'type': 'UUID',
                        'constraint': 'PRIMARY KEY',
                        'description': 'バージョンID'
                    },
                    'dataset_id': {
                        'type': 'UUID',
                        'constraint': 'FOREIGN KEY',
                        'description': 'データセットID'
                    },
                    'version': {
                        'type': 'VARCHAR(20)',
                        'constraint': 'NOT NULL',
                        'description': 'バージョン番号'
                    },
                    'description': {
                        'type': 'TEXT',
                        'constraint': 'NULL',
                        'description': 'バージョン説明'
                    },
                    'file_path': {
                        'type': 'VARCHAR(255)',
                        'constraint': 'NOT NULL',
                        'description': 'ファイルパス'
                    },
                    'file_size': {
                        'type': 'BIGINT',
                        'constraint': 'NOT NULL',
                        'description': 'ファイルサイズ'
                    },
                    'hash': {
                        'type': 'VARCHAR(64)',
                        'constraint': 'NOT NULL',
                        'description': 'ファイルハッシュ'
                    },
                    'created_by': {
                        'type': 'UUID',
                        'constraint': 'FOREIGN KEY',
                        'description': '作成者ID'
                    },
                    'created_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '作成日時'
                    }
                }
            },
            'analysis_jobs': {
                'description': '分析ジョブ情報',
                'attributes': {
                    'id': {
                        'type': 'UUID',
                        'constraint': 'PRIMARY KEY',
                        'description': 'ジョブID'
                    },
                    'dataset_id': {
                        'type': 'UUID',
                        'constraint': 'FOREIGN KEY',
                        'description': 'データセットID'
                    },
                    'version_id': {
                        'type': 'UUID',
                        'constraint': 'FOREIGN KEY',
                        'description': 'バージョンID'
                    },
                    'type': {
                        'type': 'VARCHAR(50)',
                        'constraint': 'NOT NULL',
                        'description': '分析タイプ'
                    },
                    'parameters': {
                        'type': 'JSONB',
                        'constraint': 'NOT NULL',
                        'description': '分析パラメータ'
                    },
                    'status': {
                        'type': 'VARCHAR(20)',
                        'constraint': 'NOT NULL',
                        'description': 'ジョブ状態'
                    },
                    'result': {
                        'type': 'JSONB',
                        'constraint': 'NULL',
                        'description': '分析結果'
                    },
                    'error': {
                        'type': 'TEXT',
                        'constraint': 'NULL',
                        'description': 'エラー情報'
                    },
                    'created_by': {
                        'type': 'UUID',
                        'constraint': 'FOREIGN KEY',
                        'description': '作成者ID'
                    },
                    'created_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '作成日時'
                    },
                    'updated_at': {
                        'type': 'TIMESTAMP',
                        'constraint': 'NOT NULL',
                        'description': '更新日時'
                    }
                }
            }
        }
```

### 3.2 リレーションシップ

```python
# リレーションシップ定義
class Relationships:
    def __init__(self):
        self.relationships = {
            'datasets_owner': {
                'from': 'datasets',
                'to': 'users',
                'type': 'many-to-one',
                'from_key': 'owner_id',
                'to_key': 'id',
                'constraint': 'ON DELETE RESTRICT'
            },
            'versions_dataset': {
                'from': 'versions',
                'to': 'datasets',
                'type': 'many-to-one',
                'from_key': 'dataset_id',
                'to_key': 'id',
                'constraint': 'ON DELETE CASCADE'
            },
            'versions_creator': {
                'from': 'versions',
                'to': 'users',
                'type': 'many-to-one',
                'from_key': 'created_by',
                'to_key': 'id',
                'constraint': 'ON DELETE RESTRICT'
            },
            'analysis_jobs_dataset': {
                'from': 'analysis_jobs',
                'to': 'datasets',
                'type': 'many-to-one',
                'from_key': 'dataset_id',
                'to_key': 'id',
                'constraint': 'ON DELETE CASCADE'
            },
            'analysis_jobs_version': {
                'from': 'analysis_jobs',
                'to': 'versions',
                'type': 'many-to-one',
                'from_key': 'version_id',
                'to_key': 'id',
                'constraint': 'ON DELETE RESTRICT'
            },
            'analysis_jobs_creator': {
                'from': 'analysis_jobs',
                'to': 'users',
                'type': 'many-to-one',
                'from_key': 'created_by',
                'to_key': 'id',
                'constraint': 'ON DELETE RESTRICT'
            }
        }
```

## 4. 物理設計

### 4.1 テーブル定義

```python
# テーブル定義
class TableDefinitions:
    def __init__(self):
        self.tables = {
            'users': {
                'storage': {
                    'engine': 'InnoDB',
                    'charset': 'utf8mb4',
                    'collation': 'utf8mb4_unicode_ci',
                    'partitioning': None
                },
                'constraints': {
                    'primary_key': ['id'],
                    'unique_keys': [
                        ['username'],
                        ['email']
                    ],
                    'foreign_keys': []
                }
            },
            'datasets': {
                'storage': {
                    'engine': 'InnoDB',
                    'charset': 'utf8mb4',
                    'collation': 'utf8mb4_unicode_ci',
                    'partitioning': {
                        'type': 'RANGE',
                        'column': 'created_at',
                        'intervals': 'MONTH'
                    }
                },
                'constraints': {
                    'primary_key': ['id'],
                    'unique_keys': [
                        ['name', 'owner_id']
                    ],
                    'foreign_keys': [
                        {
                            'columns': ['owner_id'],
                            'references': {
                                'table': 'users',
                                'columns': ['id']
                            }
                        }
                    ]
                }
            },
            'versions': {
                'storage': {
                    'engine': 'InnoDB',
                    'charset': 'utf8mb4',
                    'collation': 'utf8mb4_unicode_ci',
                    'partitioning': {
                        'type': 'RANGE',
                        'column': 'created_at',
                        'intervals': 'MONTH'
                    }
                },
                'constraints': {
                    'primary_key': ['id'],
                    'unique_keys': [
                        ['dataset_id', 'version']
                    ],
                    'foreign_keys': [
                        {
                            'columns': ['dataset_id'],
                            'references': {
                                'table': 'datasets',
                                'columns': ['id']
                            }
                        },
                        {
                            'columns': ['created_by'],
                            'references': {
                                'table': 'users',
                                'columns': ['id']
                            }
                        }
                    ]
                }
            },
            'analysis_jobs': {
                'storage': {
                    'engine': 'InnoDB',
                    'charset': 'utf8mb4',
                    'collation': 'utf8mb4_unicode_ci',
                    'partitioning': {
                        'type': 'RANGE',
                        'column': 'created_at',
                        'intervals': 'MONTH'
                    }
                },
                'constraints': {
                    'primary_key': ['id'],
                    'unique_keys': [],
                    'foreign_keys': [
                        {
                            'columns': ['dataset_id'],
                            'references': {
                                'table': 'datasets',
                                'columns': ['id']
                            }
                        },
                        {
                            'columns': ['version_id'],
                            'references': {
                                'table': 'versions',
                                'columns': ['id']
                            }
                        },
                        {
                            'columns': ['created_by'],
                            'references': {
                                'table': 'users',
                                'columns': ['id']
                            }
                        }
                    ]
                }
            }
        }
```

## 5. インデックス設計

### 5.1 インデックス定義

```python
# インデックス定義
class IndexDefinitions:
    def __init__(self):
        self.indexes = {
            'users': {
                'idx_username': {
                    'columns': ['username'],
                    'type': 'BTREE',
                    'unique': True
                },
                'idx_email': {
                    'columns': ['email'],
                    'type': 'BTREE',
                    'unique': True
                },
                'idx_role_status': {
                    'columns': ['role', 'status'],
                    'type': 'BTREE',
                    'unique': False
                }
            },
            'datasets': {
                'idx_owner_status': {
                    'columns': ['owner_id', 'status'],
                    'type': 'BTREE',
                    'unique': False
                },
                'idx_created_at': {
                    'columns': ['created_at'],
                    'type': 'BTREE',
                    'unique': False
                },
                'idx_metadata': {
                    'columns': ['metadata'],
                    'type': 'GIN',
                    'unique': False
                }
            },
            'versions': {
                'idx_dataset_version': {
                    'columns': ['dataset_id', 'version'],
                    'type': 'BTREE',
                    'unique': True
                },
                'idx_created_at': {
                    'columns': ['created_at'],
                    'type': 'BTREE',
                    'unique': False
                }
            },
            'analysis_jobs': {
                'idx_dataset_status': {
                    'columns': ['dataset_id', 'status'],
                    'type': 'BTREE',
                    'unique': False
                },
                'idx_created_by_status': {
                    'columns': ['created_by', 'status'],
                    'type': 'BTREE',
                    'unique': False
                },
                'idx_created_at': {
                    'columns': ['created_at'],
                    'type': 'BTREE',
                    'unique': False
                }
            }
        }
```

## 6. バックアップとリカバリ

### 6.1 バックアップ戦略

```python
# バックアップ戦略
class BackupStrategy:
    def __init__(self):
        self.strategy = {
            'full_backup': {
                'frequency': 'daily',
                'time': '02:00',
                'retention': '30 days',
                'type': 'physical',
                'compression': True
            },
            'incremental_backup': {
                'frequency': 'hourly',
                'retention': '24 hours',
                'type': 'logical',
                'compression': True
            },
            'archive_logs': {
                'frequency': 'continuous',
                'retention': '7 days',
                'type': 'logical',
                'compression': True
            },
            'verification': {
                'frequency': 'weekly',
                'type': 'restore_test',
                'automated': True
            }
        }
```

### 6.2 リカバリ手順

```python
# リカバリ手順
class RecoveryProcedures:
    def __init__(self):
        self.procedures = {
            'point_in_time_recovery': {
                'description': '特定時点へのリカバリ',
                'steps': [
                    'バックアップの特定',
                    'リストアの実行',
                    'アーカイブログの適用',
                    '整合性チェック',
                    'サービス再開'
                ],
                'estimated_time': '2-4 hours'
            },
            'disaster_recovery': {
                'description': '災害復旧',
                'steps': [
                    'セカンダリサイトの起動',
                    '最新バックアップのリストア',
                    'レプリケーションの再確立',
                    '整合性チェック',
                    'サービス移行'
                ],
                'estimated_time': '4-8 hours'
            },
            'partial_recovery': {
                'description': '部分的なリカバリ',
                'steps': [
                    '影響範囲の特定',
                    '該当テーブルのバックアップ特定',
                    'テーブル単位のリストア',
                    '整合性チェック',
                    'サービス再開'
                ],
                'estimated_time': '1-2 hours'
            }
        }
```

## 7. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | バックアップとリカバリセクションの追加 | 
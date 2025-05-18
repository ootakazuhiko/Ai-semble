# 開発環境セットアップガイド

## 目次

1. [はじめに](#1-はじめに)
2. [必要要件](#2-必要要件)
3. [環境構築手順](#3-環境構築手順)
4. [開発ツール](#4-開発ツール)
5. [設定ファイル](#5-設定ファイル)
6. [トラブルシューティング](#6-トラブルシューティング)
7. [更新履歴](#7-更新履歴)

## 1. はじめに

このドキュメントは、データセット管理システムの開発環境構築手順を定義します。

### 1.1 目的

- 開発環境の標準化
- 環境構築手順の明確化
- 開発効率の向上
- トラブルシューティングの効率化

### 1.2 対象読者

- 開発者
- システム管理者
- 新規チームメンバー
- インフラエンジニア

## 2. 必要要件

### 2.1 システム要件

```python
# システム要件
class SystemRequirements:
    def __init__(self):
        self.requirements = {
            'hardware': {
                'cpu': {
                    'minimum': '4コア',
                    'recommended': '8コア以上'
                },
                'memory': {
                    'minimum': '8GB',
                    'recommended': '16GB以上'
                },
                'storage': {
                    'minimum': '50GB',
                    'recommended': '100GB以上'
                }
            },
            'software': {
                'os': {
                    'windows': 'Windows 10/11 Pro',
                    'macos': 'macOS 12.0以上',
                    'linux': 'Ubuntu 22.04 LTS以上'
                },
                'virtualization': {
                    'docker': '24.0以上',
                    'docker_compose': '2.20以上'
                }
            }
        }
```

### 2.2 開発ツール要件

```python
# 開発ツール要件
class DevelopmentTools:
    def __init__(self):
        self.tools = {
            'version_control': {
                'git': {
                    'version': '2.40.0以上',
                    'config': {
                        'user.name': '必須',
                        'user.email': '必須',
                        'core.autocrlf': 'input'
                    }
                }
            },
            'ide': {
                'vscode': {
                    'version': '1.85.0以上',
                    'extensions': [
                        'Python',
                        'Docker',
                        'GitLens',
                        'ESLint',
                        'Prettier'
                    ]
                }
            },
            'runtime': {
                'python': {
                    'version': '3.11.0以上',
                    'packages': [
                        'poetry>=1.7.0',
                        'black>=23.0.0',
                        'flake8>=6.0.0',
                        'mypy>=1.0.0'
                    ]
                },
                'node': {
                    'version': '20.0.0以上',
                    'packages': [
                        'npm>=10.0.0',
                        'yarn>=1.22.0'
                    ]
                }
            }
        }
```

## 3. 環境構築手順

### 3.1 基本環境のセットアップ

```python
# 環境構築手順
class SetupProcedures:
    def __init__(self):
        self.procedures = {
            'initial_setup': {
                'steps': [
                    {
                        'name': 'リポジトリのクローン',
                        'command': 'git clone https://github.com/example/ai-semble.git',
                        'description': 'プロジェクトリポジトリの取得'
                    },
                    {
                        'name': 'Python仮想環境の作成',
                        'command': 'poetry install',
                        'description': '依存パッケージのインストール'
                    },
                    {
                        'name': 'Node.jsパッケージのインストール',
                        'command': 'yarn install',
                        'description': 'フロントエンド依存パッケージのインストール'
                    },
                    {
                        'name': '環境変数の設定',
                        'command': 'cp .env.example .env',
                        'description': '環境変数ファイルの作成'
                    }
                ]
            },
            'database_setup': {
                'steps': [
                    {
                        'name': 'PostgreSQLの起動',
                        'command': 'docker-compose up -d postgres',
                        'description': 'データベースコンテナの起動'
                    },
                    {
                        'name': 'データベースの作成',
                        'command': 'poetry run python scripts/create_db.py',
                        'description': '開発用データベースの作成'
                    },
                    {
                        'name': 'マイグレーションの実行',
                        'command': 'poetry run alembic upgrade head',
                        'description': 'データベーススキーマの適用'
                    }
                ]
            },
            'service_setup': {
                'steps': [
                    {
                        'name': 'Redisの起動',
                        'command': 'docker-compose up -d redis',
                        'description': 'キャッシュサーバーの起動'
                    },
                    {
                        'name': 'Elasticsearchの起動',
                        'command': 'docker-compose up -d elasticsearch',
                        'description': '検索エンジンの起動'
                    },
                    {
                        'name': 'APIサーバーの起動',
                        'command': 'poetry run uvicorn app.main:app --reload',
                        'description': '開発用APIサーバーの起動'
                    },
                    {
                        'name': 'フロントエンドの起動',
                        'command': 'yarn dev',
                        'description': '開発用Webサーバーの起動'
                    }
                ]
            }
        }
```

## 4. 開発ツール

### 4.1 開発ツールの設定

```python
# 開発ツール設定
class ToolConfigurations:
    def __init__(self):
        self.configurations = {
            'vscode': {
                'settings': {
                    'editor.formatOnSave': True,
                    'editor.codeActionsOnSave': {
                        'source.fixAll': True,
                        'source.organizeImports': True
                    },
                    'python.linting.enabled': True,
                    'python.linting.flake8Enabled': True,
                    'python.formatting.provider': 'black'
                },
                'extensions': {
                    'required': [
                        'ms-python.python',
                        'ms-python.vscode-pylance',
                        'ms-azuretools.vscode-docker',
                        'eamodio.gitlens',
                        'dbaeumer.vscode-eslint',
                        'esbenp.prettier-vscode'
                    ]
                }
            },
            'git': {
                'hooks': {
                    'pre-commit': [
                        'poetry run black .',
                        'poetry run flake8',
                        'poetry run mypy .',
                        'yarn lint',
                        'yarn test'
                    ]
                },
                'ignore': [
                    '.env',
                    '.venv',
                    '__pycache__',
                    '*.pyc',
                    'node_modules',
                    'dist'
                ]
            },
            'docker': {
                'compose': {
                    'version': '3.8',
                    'services': {
                        'postgres': {
                            'image': 'postgres:15.0',
                            'ports': ['5432:5432'],
                            'volumes': ['postgres_data:/var/lib/postgresql/data']
                        },
                        'redis': {
                            'image': 'redis:7.0',
                            'ports': ['6379:6379']
                        },
                        'elasticsearch': {
                            'image': 'elasticsearch:8.0',
                            'ports': ['9200:9200'],
                            'environment': {
                                'discovery.type': 'single-node',
                                'xpack.security.enabled': 'false'
                            }
                        }
                    }
                }
            }
        }
```

## 5. 設定ファイル

### 5.1 環境変数

```python
# 環境変数設定
class EnvironmentVariables:
    def __init__(self):
        self.variables = {
            'database': {
                'POSTGRES_HOST': 'localhost',
                'POSTGRES_PORT': '5432',
                'POSTGRES_DB': 'ai_semble_dev',
                'POSTGRES_USER': 'postgres',
                'POSTGRES_PASSWORD': 'postgres'
            },
            'redis': {
                'REDIS_HOST': 'localhost',
                'REDIS_PORT': '6379',
                'REDIS_DB': '0'
            },
            'elasticsearch': {
                'ELASTICSEARCH_HOST': 'localhost',
                'ELASTICSEARCH_PORT': '9200'
            },
            'api': {
                'API_HOST': 'localhost',
                'API_PORT': '8000',
                'DEBUG': 'true',
                'ENVIRONMENT': 'development'
            },
            'frontend': {
                'NEXT_PUBLIC_API_URL': 'http://localhost:8000',
                'NEXT_PUBLIC_ENV': 'development'
            }
        }
```

## 6. トラブルシューティング

### 6.1 一般的な問題と解決方法

```python
# トラブルシューティング
class Troubleshooting:
    def __init__(self):
        self.solutions = {
            'database': {
                'connection_error': {
                    'symptom': 'データベースに接続できない',
                    'solutions': [
                        'Dockerコンテナが起動しているか確認',
                        'ポートが正しく設定されているか確認',
                        '環境変数が正しく設定されているか確認'
                    ]
                },
                'migration_error': {
                    'symptom': 'マイグレーションが失敗する',
                    'solutions': [
                        'データベースが最新の状態か確認',
                        'マイグレーションファイルに問題がないか確認',
                        'ログを確認して具体的なエラーを特定'
                    ]
                }
            },
            'api': {
                'startup_error': {
                    'symptom': 'APIサーバーが起動しない',
                    'solutions': [
                        '依存パッケージが正しくインストールされているか確認',
                        '環境変数が正しく設定されているか確認',
                        'ポートが他のプロセスで使用されていないか確認'
                    ]
                },
                'dependency_error': {
                    'symptom': '依存関係のエラーが発生する',
                    'solutions': [
                        'poetry.lockファイルを削除して再インストール',
                        '仮想環境を再作成',
                        'キャッシュをクリアして再インストール'
                    ]
                }
            },
            'frontend': {
                'build_error': {
                    'symptom': 'フロントエンドのビルドが失敗する',
                    'solutions': [
                        'node_modulesを削除して再インストール',
                        'キャッシュをクリアして再ビルド',
                        '依存関係のバージョンを確認'
                    ]
                },
                'api_connection_error': {
                    'symptom': 'APIに接続できない',
                    'solutions': [
                        'APIサーバーが起動しているか確認',
                        'CORS設定を確認',
                        '環境変数が正しく設定されているか確認'
                    ]
                }
            }
        }
```

## 7. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | トラブルシューティングセクションの追加 | 
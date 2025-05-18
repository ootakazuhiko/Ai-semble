# 開発環境

## 目次

1. [はじめに](#1-はじめに)
2. [環境構築](#2-環境構築)
3. [開発ツール](#3-開発ツール)
4. [依存関係管理](#4-依存関係管理)
5. [デバッグ環境](#5-デバッグ環境)
6. [CI/CD](#6-cicd)

## 1. はじめに

このドキュメントは、データセット管理システムの開発環境の構築と管理に関する情報を提供します。

### 1.1 目的

- 開発環境の標準化
- 開発効率の向上
- 品質の確保
- チーム間の協業促進
- 運用性の向上

### 1.2 適用範囲

- ローカル開発環境
- 開発サーバー環境
- テスト環境
- CI/CD環境

## 2. 環境構築

### 2.1 必要条件

```python
# 環境要件
class EnvironmentRequirements:
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
                    'minimum': '256GB SSD',
                    'recommended': '512GB SSD以上'
                }
            },
            'software': {
                'os': {
                    'windows': 'Windows 10/11',
                    'macos': 'macOS 12.0以上',
                    'linux': 'Ubuntu 22.04 LTS以上'
                },
                'python': {
                    'version': '3.10以上',
                    'packages': [
                        'pip',
                        'virtualenv',
                        'poetry'
                    ]
                },
                'node': {
                    'version': '18.0以上',
                    'packages': [
                        'npm',
                        'yarn'
                    ]
                },
                'database': {
                    'postgresql': '14.0以上',
                    'redis': '6.0以上'
                },
                'docker': {
                    'version': '20.10以上',
                    'compose': '2.0以上'
                }
            }
        }
```

### 2.2 セットアップ手順

```python
# セットアップ手順
class SetupProcedure:
    def __init__(self):
        self.procedures = {
            'repository': {
                'clone': {
                    'command': 'git clone https://github.com/example/dataset-management.git',
                    'branch': 'develop'
                },
                'configuration': {
                    'git_config': {
                        'user.name': '設定が必要',
                        'user.email': '設定が必要',
                        'core.autocrlf': 'input'
                    }
                }
            },
            'python': {
                'virtualenv': {
                    'create': 'python -m venv .venv',
                    'activate': {
                        'windows': '.venv\\Scripts\\activate',
                        'unix': 'source .venv/bin/activate'
                    }
                },
                'dependencies': {
                    'install': 'poetry install',
                    'update': 'poetry update'
                }
            },
            'node': {
                'dependencies': {
                    'install': 'yarn install',
                    'update': 'yarn upgrade'
                }
            },
            'database': {
                'postgresql': {
                    'create': 'createdb dataset_management',
                    'migrate': 'alembic upgrade head'
                },
                'redis': {
                    'start': 'redis-server'
                }
            },
            'docker': {
                'build': 'docker-compose build',
                'start': 'docker-compose up -d',
                'stop': 'docker-compose down'
            }
        }
```

## 3. 開発ツール

### 3.1 エディタ設定

```python
# エディタ設定
class EditorSettings:
    def __init__(self):
        self.settings = {
            'vscode': {
                'extensions': [
                    'Python',
                    'Pylance',
                    'Python Test Explorer',
                    'Python Docstring Generator',
                    'Python Type Hint',
                    'Python Indent',
                    'Python Environment Manager',
                    'Python Extension Pack',
                    'GitLens',
                    'Docker',
                    'Remote - Containers',
                    'ESLint',
                    'Prettier',
                    'EditorConfig'
                ],
                'settings': {
                    'python.linting.enabled': True,
                    'python.linting.pylintEnabled': True,
                    'python.formatting.provider': 'black',
                    'editor.formatOnSave': True,
                    'editor.rulers': [88],
                    'files.trimTrailingWhitespace': True,
                    'files.insertFinalNewline': True
                }
            },
            'pycharm': {
                'plugins': [
                    'Python',
                    'Database Tools and SQL',
                    'Docker',
                    'Git Integration',
                    'Markdown',
                    '.env files support'
                ],
                'settings': {
                    'code_style': {
                        'python': {
                            'indent_size': 4,
                            'continuation_indent_size': 4,
                            'max_line_length': 88
                        }
                    },
                    'inspections': {
                        'python': {
                            'pep8': True,
                            'pylint': True
                        }
                    }
                }
            }
        }
```

### 3.2 開発支援ツール

```python
# 開発支援ツール
class DevelopmentTools:
    def __init__(self):
        self.tools = {
            'code_quality': {
                'linters': {
                    'python': [
                        'pylint',
                        'flake8',
                        'mypy'
                    ],
                    'javascript': [
                        'eslint',
                        'prettier'
                    ]
                },
                'formatters': {
                    'python': [
                        'black',
                        'isort'
                    ],
                    'javascript': [
                        'prettier'
                    ]
                },
                'type_checkers': {
                    'python': 'mypy',
                    'javascript': 'typescript'
                }
            },
            'testing': {
                'frameworks': {
                    'python': [
                        'pytest',
                        'pytest-cov',
                        'pytest-mock'
                    ],
                    'javascript': [
                        'jest',
                        'react-testing-library'
                    ]
                },
                'coverage': {
                    'python': 'coverage.py',
                    'javascript': 'istanbul'
                }
            },
            'documentation': {
                'generators': {
                    'python': [
                        'sphinx',
                        'pdoc'
                    ],
                    'javascript': [
                        'jsdoc',
                        'typedoc'
                    ]
                },
                'api': [
                    'swagger',
                    'openapi'
                ]
            },
            'version_control': {
                'git': {
                    'hooks': 'pre-commit',
                    'workflow': 'git-flow'
                },
                'tools': [
                    'git-lfs',
                    'git-secrets'
                ]
            }
        }
```

## 4. 依存関係管理

### 4.1 Python依存関係

```python
# Python依存関係
class PythonDependencies:
    def __init__(self):
        self.dependencies = {
            'poetry': {
                'version': '1.4.0以上',
                'configuration': {
                    'pyproject.toml': {
                        'tool.poetry': {
                            'name': 'dataset-management',
                            'version': '0.1.0',
                            'description': 'データセット管理システム',
                            'python': '^3.10'
                        }
                    }
                }
            },
            'packages': {
                'main': [
                    'fastapi>=0.95.0',
                    'uvicorn>=0.21.0',
                    'sqlalchemy>=2.0.0',
                    'alembic>=1.10.0',
                    'pydantic>=2.0.0',
                    'python-jose>=3.3.0',
                    'passlib>=1.7.4',
                    'python-multipart>=0.0.6',
                    'redis>=4.5.0',
                    'celery>=5.3.0'
                ],
                'dev': [
                    'pytest>=7.3.0',
                    'pytest-cov>=4.1.0',
                    'pytest-mock>=3.10.0',
                    'black>=23.3.0',
                    'isort>=5.12.0',
                    'flake8>=6.0.0',
                    'mypy>=1.3.0',
                    'pre-commit>=3.3.0'
                ],
                'docs': [
                    'sphinx>=6.1.0',
                    'sphinx-rtd-theme>=1.2.0',
                    'sphinx-autodoc-typehints>=1.23.0'
                ]
            }
        }
```

### 4.2 Node.js依存関係

```python
# Node.js依存関係
class NodeDependencies:
    def __init__(self):
        self.dependencies = {
            'package_manager': {
                'yarn': {
                    'version': '1.22.0以上',
                    'configuration': {
                        'package.json': {
                            'name': 'dataset-management-frontend',
                            'version': '0.1.0',
                            'private': True,
                            'engines': {
                                'node': '>=18.0.0'
                            }
                        }
                    }
                }
            },
            'packages': {
                'main': [
                    'react>=18.2.0',
                    'react-dom>=18.2.0',
                    'next>=13.4.0',
                    'typescript>=5.0.0',
                    'axios>=1.4.0',
                    'swr>=2.1.0',
                    'tailwindcss>=3.3.0',
                    'daisyui>=3.0.0'
                ],
                'dev': [
                    '@types/react>=18.2.0',
                    '@types/node>=18.16.0',
                    'eslint>=8.40.0',
                    'prettier>=2.8.0',
                    'jest>=29.5.0',
                    '@testing-library/react>=14.0.0',
                    'cypress>=12.13.0'
                ]
            }
        }
```

## 5. デバッグ環境

### 5.1 デバッグ設定

```python
# デバッグ設定
class DebugSettings:
    def __init__(self):
        self.settings = {
            'python': {
                'debugger': {
                    'tool': 'debugpy',
                    'port': 5678,
                    'configuration': {
                        'launch.json': {
                            'version': '0.2.0',
                            'configurations': [
                                {
                                    'name': 'Python: FastAPI',
                                    'type': 'python',
                                    'request': 'launch',
                                    'module': 'uvicorn',
                                    'args': [
                                        'app.main:app',
                                        '--reload',
                                        '--port',
                                        '8000'
                                    ],
                                    'jinja': True,
                                    'justMyCode': False
                                }
                            ]
                        }
                    }
                },
                'logging': {
                    'level': 'DEBUG',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'handlers': [
                        'console',
                        'file'
                    ]
                }
            },
            'javascript': {
                'debugger': {
                    'tool': 'chrome-devtools',
                    'port': 9222,
                    'configuration': {
                        'launch.json': {
                            'version': '0.2.0',
                            'configurations': [
                                {
                                    'name': 'Next.js: debug',
                                    'type': 'chrome',
                                    'request': 'launch',
                                    'url': 'http://localhost:3000',
                                    'webRoot': '${workspaceFolder}'
                                }
                            ]
                        }
                    }
                },
                'logging': {
                    'level': 'debug',
                    'format': '%c %t %l: %m',
                    'handlers': [
                        'console',
                        'file'
                    ]
                }
            }
        }
```

### 5.2 テスト環境

```python
# テスト環境
class TestEnvironment:
    def __init__(self):
        self.environment = {
            'python': {
                'pytest': {
                    'configuration': {
                        'pytest.ini': {
                            'testpaths': ['tests'],
                            'python_files': 'test_*.py',
                            'python_classes': 'Test*',
                            'python_functions': 'test_*',
                            'addopts': [
                                '-v',
                                '--cov=app',
                                '--cov-report=term-missing',
                                '--cov-report=html'
                            ]
                        }
                    },
                    'fixtures': {
                        'conftest.py': {
                            'database': 'テスト用DB',
                            'redis': 'テスト用Redis',
                            'celery': 'テスト用Celery'
                        }
                    }
                }
            },
            'javascript': {
                'jest': {
                    'configuration': {
                        'jest.config.js': {
                            'testEnvironment': 'jsdom',
                            'setupFilesAfterEnv': [
                                '<rootDir>/jest.setup.js'
                            ],
                            'moduleNameMapper': {
                                '^@/(.*)$': '<rootDir>/src/$1'
                            },
                            'collectCoverageFrom': [
                                'src/**/*.{js,jsx,ts,tsx}'
                            ]
                        }
                    },
                    'mocks': {
                        'api': 'MSW',
                        'components': 'jest.mock'
                    }
                },
                'cypress': {
                    'configuration': {
                        'cypress.config.ts': {
                            'e2e': {
                                'baseUrl': 'http://localhost:3000',
                                'supportFile': 'cypress/support/e2e.ts'
                            }
                        }
                    }
                }
            }
        }
```

## 6. CI/CD

### 6.1 パイプライン設定

```python
# CI/CD設定
class CICDConfiguration:
    def __init__(self):
        self.configuration = {
            'github_actions': {
                'workflows': {
                    'ci': {
                        'triggers': [
                            'push',
                            'pull_request'
                        ],
                        'jobs': [
                            'lint',
                            'test',
                            'build',
                            'security'
                        ]
                    },
                    'cd': {
                        'triggers': [
                            'release'
                        ],
                        'jobs': [
                            'deploy_staging',
                            'deploy_production'
                        ]
                    }
                },
                'environments': {
                    'staging': {
                        'url': 'https://staging.example.com',
                        'secrets': [
                            'DB_PASSWORD',
                            'API_KEY'
                        ]
                    },
                    'production': {
                        'url': 'https://example.com',
                        'secrets': [
                            'DB_PASSWORD',
                            'API_KEY'
                        ]
                    }
                }
            },
            'docker': {
                'images': {
                    'backend': {
                        'dockerfile': 'Dockerfile.backend',
                        'context': './backend',
                        'targets': [
                            'development',
                            'production'
                        ]
                    },
                    'frontend': {
                        'dockerfile': 'Dockerfile.frontend',
                        'context': './frontend',
                        'targets': [
                            'development',
                            'production'
                        ]
                    }
                },
                'compose': {
                    'development': 'docker-compose.dev.yml',
                    'staging': 'docker-compose.staging.yml',
                    'production': 'docker-compose.prod.yml'
                }
            }
        }
```

## 7. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | CI/CDセクションの追加 | 
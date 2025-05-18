# インフラストラクチャ設計書

## 目次

1. [はじめに](#1-はじめに)
2. [アーキテクチャ概要](#2-アーキテクチャ概要)
3. [コンピューティング](#3-コンピューティング)
4. [ネットワーク](#4-ネットワーク)
5. [ストレージ](#5-ストレージ)
6. [セキュリティ](#6-セキュリティ)
7. [監視と運用](#7-監視と運用)
8. [更新履歴](#8-更新履歴)

## 1. はじめに

このドキュメントは、データセット管理システムのインフラストラクチャ設計を定義します。

### 1.1 目的

- インフラ構成の標準化
- スケーラビリティの確保
- セキュリティの強化
- 運用効率の向上

### 1.2 対象読者

- インフラエンジニア
- システム管理者
- セキュリティ担当者
- 運用担当者

## 2. アーキテクチャ概要

### 2.1 システム構成

```python
# アーキテクチャ概要
class ArchitectureOverview:
    def __init__(self):
        self.architecture = {
            'environment': {
                'production': {
                    'region': 'ap-northeast-1',
                    'availability_zones': [
                        'ap-northeast-1a',
                        'ap-northeast-1c'
                    ],
                    'multi_az': True
                },
                'staging': {
                    'region': 'ap-northeast-1',
                    'availability_zones': [
                        'ap-northeast-1a'
                    ],
                    'multi_az': False
                },
                'development': {
                    'region': 'ap-northeast-1',
                    'availability_zones': [
                        'ap-northeast-1a'
                    ],
                    'multi_az': False
                }
            },
            'components': {
                'compute': {
                    'application': {
                        'type': 'ECS Fargate',
                        'scaling': 'Auto Scaling',
                        'capacity': {
                            'min': 2,
                            'max': 10,
                            'desired': 4
                        }
                    },
                    'batch': {
                        'type': 'AWS Batch',
                        'compute_environment': 'Fargate',
                        'job_queues': [
                            'high-priority',
                            'default',
                            'low-priority'
                        ]
                    }
                },
                'database': {
                    'primary': {
                        'type': 'RDS PostgreSQL',
                        'engine': 'PostgreSQL 14.0',
                        'instance': 'db.r5.large',
                        'storage': {
                            'type': 'gp3',
                            'size': 1000,
                            'iops': 3000
                        }
                    },
                    'replica': {
                        'type': 'Read Replica',
                        'instance': 'db.r5.large',
                        'count': 2
                    },
                    'cache': {
                        'type': 'ElastiCache',
                        'engine': 'Redis 6.0',
                        'instance': 'cache.r5.large',
                        'cluster': {
                            'nodes': 3,
                            'shards': 2
                        }
                    }
                },
                'storage': {
                    'object': {
                        'type': 'S3',
                        'classes': [
                            'STANDARD',
                            'STANDARD_IA',
                            'GLACIER'
                        ],
                        'lifecycle': {
                            'transition': {
                                'STANDARD_IA': '30日',
                                'GLACIER': '90日'
                            },
                            'expiration': '365日'
                        }
                    },
                    'backup': {
                        'type': 'S3',
                        'class': 'STANDARD_IA',
                        'retention': '90日'
                    }
                },
                'network': {
                    'vpc': {
                        'cidr': '10.0.0.0/16',
                        'subnets': {
                            'public': [
                                '10.0.1.0/24',
                                '10.0.2.0/24'
                            ],
                            'private': [
                                '10.0.11.0/24',
                                '10.0.12.0/24'
                            ],
                            'database': [
                                '10.0.21.0/24',
                                '10.0.22.0/24'
                            ]
                        }
                    },
                    'load_balancer': {
                        'type': 'Application Load Balancer',
                        'scheme': 'internet-facing',
                        'listeners': [
                            {
                                'port': 443,
                                'protocol': 'HTTPS'
                            }
                        ]
                    }
                }
            }
        }
```

## 3. コンピューティング

### 3.1 コンピューティングリソース

```python
# コンピューティング
class ComputingResources:
    def __init__(self):
        self.computing = {
            'application': {
                'containers': {
                    'api': {
                        'image': 'api-server:latest',
                        'resources': {
                            'cpu': 1024,
                            'memory': 2048
                        },
                        'scaling': {
                            'cpu_threshold': 70,
                            'memory_threshold': 80,
                            'cooldown': 300
                        }
                    },
                    'worker': {
                        'image': 'worker:latest',
                        'resources': {
                            'cpu': 2048,
                            'memory': 4096
                        },
                        'scaling': {
                            'queue_threshold': 1000,
                            'cooldown': 300
                        }
                    }
                },
                'auto_scaling': {
                    'target_tracking': {
                        'cpu_utilization': {
                            'target': 70,
                            'scale_in_cooldown': 300,
                            'scale_out_cooldown': 60
                        },
                        'memory_utilization': {
                            'target': 80,
                            'scale_in_cooldown': 300,
                            'scale_out_cooldown': 60
                        }
                    },
                    'scheduled': {
                        'weekday': {
                            'min': 4,
                            'max': 10,
                            'desired': 6
                        },
                        'weekend': {
                            'min': 2,
                            'max': 6,
                            'desired': 3
                        }
                    }
                }
            },
            'batch': {
                'compute_environment': {
                    'type': 'Fargate',
                    'max_vcpus': 100,
                    'subnets': [
                        'private-1',
                        'private-2'
                    ]
                },
                'job_queues': {
                    'high_priority': {
                        'priority': 1,
                        'compute_environments': [
                            'high-performance'
                        ]
                    },
                    'default': {
                        'priority': 2,
                        'compute_environments': [
                            'standard'
                        ]
                    },
                    'low_priority': {
                        'priority': 3,
                        'compute_environments': [
                            'cost-optimized'
                        ]
                    }
                }
            }
        }
```

## 4. ネットワーク

### 4.1 ネットワーク構成

```python
# ネットワーク
class NetworkConfiguration:
    def __init__(self):
        self.network = {
            'vpc': {
                'cidr': '10.0.0.0/16',
                'subnets': {
                    'public': {
                        'ap-northeast-1a': {
                            'cidr': '10.0.1.0/24',
                            'az': 'ap-northeast-1a'
                        },
                        'ap-northeast-1c': {
                            'cidr': '10.0.2.0/24',
                            'az': 'ap-northeast-1c'
                        }
                    },
                    'private': {
                        'ap-northeast-1a': {
                            'cidr': '10.0.11.0/24',
                            'az': 'ap-northeast-1a'
                        },
                        'ap-northeast-1c': {
                            'cidr': '10.0.12.0/24',
                            'az': 'ap-northeast-1c'
                        }
                    },
                    'database': {
                        'ap-northeast-1a': {
                            'cidr': '10.0.21.0/24',
                            'az': 'ap-northeast-1a'
                        },
                        'ap-northeast-1c': {
                            'cidr': '10.0.22.0/24',
                            'az': 'ap-northeast-1c'
                        }
                    }
                },
                'route_tables': {
                    'public': {
                        'routes': [
                            {
                                'destination': '0.0.0.0/0',
                                'target': 'internet_gateway'
                            }
                        ]
                    },
                    'private': {
                        'routes': [
                            {
                                'destination': '0.0.0.0/0',
                                'target': 'nat_gateway'
                            }
                        ]
                    }
                }
            },
            'security': {
                'security_groups': {
                    'alb': {
                        'inbound': [
                            {
                                'port': 443,
                                'source': '0.0.0.0/0',
                                'description': 'HTTPS'
                            }
                        ],
                        'outbound': [
                            {
                                'port': 'all',
                                'destination': '0.0.0.0/0'
                            }
                        ]
                    },
                    'application': {
                        'inbound': [
                            {
                                'port': 8080,
                                'source': 'alb',
                                'description': 'API'
                            }
                        ],
                        'outbound': [
                            {
                                'port': 'all',
                                'destination': '0.0.0.0/0'
                            }
                        ]
                    },
                    'database': {
                        'inbound': [
                            {
                                'port': 5432,
                                'source': 'application',
                                'description': 'PostgreSQL'
                            }
                        ],
                        'outbound': [
                            {
                                'port': 'all',
                                'destination': '0.0.0.0/0'
                            }
                        ]
                    }
                },
                'nacls': {
                    'public': {
                        'inbound': [
                            {
                                'rule': 100,
                                'port': 443,
                                'source': '0.0.0.0/0',
                                'action': 'allow'
                            }
                        ],
                        'outbound': [
                            {
                                'rule': 100,
                                'port': 'all',
                                'destination': '0.0.0.0/0',
                                'action': 'allow'
                            }
                        ]
                    },
                    'private': {
                        'inbound': [
                            {
                                'rule': 100,
                                'port': 'all',
                                'source': '10.0.0.0/16',
                                'action': 'allow'
                            }
                        ],
                        'outbound': [
                            {
                                'rule': 100,
                                'port': 'all',
                                'destination': '0.0.0.0/0',
                                'action': 'allow'
                            }
                        ]
                    }
                }
            },
            'load_balancer': {
                'type': 'Application Load Balancer',
                'scheme': 'internet-facing',
                'listeners': {
                    'https': {
                        'port': 443,
                        'protocol': 'HTTPS',
                        'certificate': 'arn:aws:acm:...',
                        'ssl_policy': 'ELBSecurityPolicy-2016-08'
                    }
                },
                'target_groups': {
                    'api': {
                        'port': 8080,
                        'protocol': 'HTTP',
                        'health_check': {
                            'path': '/health',
                            'interval': 30,
                            'timeout': 5,
                            'healthy_threshold': 2,
                            'unhealthy_threshold': 3
                        }
                    }
                }
            }
        }
```

## 5. ストレージ

### 5.1 ストレージ構成

```python
# ストレージ
class StorageConfiguration:
    def __init__(self):
        self.storage = {
            'database': {
                'primary': {
                    'type': 'RDS PostgreSQL',
                    'instance': 'db.r5.large',
                    'storage': {
                        'type': 'gp3',
                        'size': 1000,
                        'iops': 3000,
                        'throughput': 125
                    },
                    'backup': {
                        'automated': {
                            'retention': 7,
                            'window': '03:00-04:00'
                        },
                        'snapshot': {
                            'frequency': 'daily',
                            'retention': 30
                        }
                    }
                },
                'replica': {
                    'instance': 'db.r5.large',
                    'count': 2,
                    'storage': {
                        'type': 'gp3',
                        'size': 1000,
                        'iops': 3000
                    }
                }
            },
            'cache': {
                'type': 'ElastiCache Redis',
                'engine': 'Redis 6.0',
                'instance': 'cache.r5.large',
                'cluster': {
                    'nodes': 3,
                    'shards': 2,
                    'replicas': 1
                },
                'parameters': {
                    'maxmemory-policy': 'volatile-lru',
                    'appendonly': 'yes'
                }
            },
            'object': {
                'type': 'S3',
                'buckets': {
                    'datasets': {
                        'class': 'STANDARD',
                        'lifecycle': {
                            'transition': [
                                {
                                    'days': 30,
                                    'storage_class': 'STANDARD_IA'
                                },
                                {
                                    'days': 90,
                                    'storage_class': 'GLACIER'
                                }
                            ],
                            'expiration': {
                                'days': 365
                            }
                        },
                        'versioning': True,
                        'encryption': 'AES-256'
                    },
                    'backups': {
                        'class': 'STANDARD_IA',
                        'lifecycle': {
                            'expiration': {
                                'days': 90
                            }
                        },
                        'versioning': True,
                        'encryption': 'AES-256'
                    }
                }
            }
        }
```

## 6. セキュリティ

### 6.1 セキュリティ構成

```python
# セキュリティ
class SecurityConfiguration:
    def __init__(self):
        self.security = {
            'network': {
                'vpc': {
                    'flow_logs': {
                        'enabled': True,
                        'retention': 30
                    },
                    'endpoints': {
                        's3': {
                            'type': 'Gateway',
                            'policy': 'FullAccess'
                        },
                        'dynamodb': {
                            'type': 'Gateway',
                            'policy': 'FullAccess'
                        }
                    }
                },
                'waf': {
                    'rules': {
                        'rate_limit': {
                            'rate': 2000,
                            'period': 300
                        },
                        'sql_injection': {
                            'action': 'block'
                        },
                        'xss': {
                            'action': 'block'
                        }
                    }
                }
            },
            'encryption': {
                'at_rest': {
                    'database': {
                        'type': 'AES-256',
                        'kms_key': 'arn:aws:kms:...'
                    },
                    'cache': {
                        'type': 'AES-256',
                        'kms_key': 'arn:aws:kms:...'
                    },
                    'storage': {
                        'type': 'AES-256',
                        'kms_key': 'arn:aws:kms:...'
                    }
                },
                'in_transit': {
                    'protocol': 'TLS 1.2',
                    'certificates': {
                        'api': 'arn:aws:acm:...',
                        'console': 'arn:aws:acm:...'
                    }
                }
            },
            'access_control': {
                'iam': {
                    'roles': {
                        'application': {
                            'policies': [
                                'AmazonS3ReadOnly',
                                'AmazonRDSReadOnly'
                            ]
                        },
                        'batch': {
                            'policies': [
                                'AmazonS3FullAccess',
                                'AmazonRDSFullAccess'
                            ]
                        }
                    },
                    'users': {
                        'admin': {
                            'groups': ['Administrators'],
                            'mfa': True
                        },
                        'developer': {
                            'groups': ['Developers'],
                            'mfa': True
                        }
                    }
                },
                'secrets': {
                    'rotation': {
                        'database': 30,
                        'api_keys': 90
                    },
                    'storage': 'AWS Secrets Manager'
                }
            }
        }
```

## 7. 監視と運用

### 7.1 監視構成

```python
# 監視と運用
class MonitoringConfiguration:
    def __init__(self):
        self.monitoring = {
            'metrics': {
                'application': {
                    'cpu': {
                        'threshold': 70,
                        'period': 300,
                        'evaluation_periods': 2
                    },
                    'memory': {
                        'threshold': 80,
                        'period': 300,
                        'evaluation_periods': 2
                    },
                    'latency': {
                        'threshold': 1000,
                        'period': 300,
                        'evaluation_periods': 2
                    }
                },
                'database': {
                    'cpu': {
                        'threshold': 80,
                        'period': 300,
                        'evaluation_periods': 2
                    },
                    'connections': {
                        'threshold': 1000,
                        'period': 300,
                        'evaluation_periods': 2
                    },
                    'storage': {
                        'threshold': 80,
                        'period': 300,
                        'evaluation_periods': 2
                    }
                },
                'cache': {
                    'cpu': {
                        'threshold': 80,
                        'period': 300,
                        'evaluation_periods': 2
                    },
                    'memory': {
                        'threshold': 80,
                        'period': 300,
                        'evaluation_periods': 2
                    },
                    'connections': {
                        'threshold': 1000,
                        'period': 300,
                        'evaluation_periods': 2
                    }
                }
            },
            'logging': {
                'application': {
                    'type': 'CloudWatch Logs',
                    'retention': 30,
                    'groups': [
                        'api',
                        'worker',
                        'batch'
                    ]
                },
                'database': {
                    'type': 'CloudWatch Logs',
                    'retention': 30,
                    'groups': [
                        'postgresql',
                        'audit'
                    ]
                },
                'access': {
                    'type': 'CloudWatch Logs',
                    'retention': 90,
                    'groups': [
                        'alb',
                        'waf'
                    ]
                }
            },
            'alerts': {
                'channels': {
                    'email': [
                        'alerts@example.com'
                    ],
                    'slack': [
                        '#alerts-prod',
                        '#alerts-staging'
                    ],
                    'sns': [
                        'arn:aws:sns:...'
                    ]
                },
                'severity': {
                    'critical': {
                        'channels': [
                            'slack',
                            'sns'
                        ],
                        'response_time': '15分'
                    },
                    'warning': {
                        'channels': [
                            'email',
                            'slack'
                        ],
                        'response_time': '4時間'
                    }
                }
            }
        }
```

## 8. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | セキュリティ構成の追加 | 
# モニタリングとアラート設定

## 目次

1. [はじめに](#1-はじめに)
2. [モニタリング構成](#2-モニタリング構成)
3. [メトリクス](#3-メトリクス)
4. [アラート設定](#4-アラート設定)
5. [ダッシュボード](#5-ダッシュボード)
6. [ログ管理](#6-ログ管理)
7. [インシデント対応](#7-インシデント対応)

## 1. はじめに

このドキュメントは、データセット管理システムのモニタリングとアラート設定を定義するものです。システムの健全性を維持し、問題の早期発見と対応を実現します。

### 1.1 目的

- システムの健全性監視
- パフォーマンスの追跡
- 問題の早期発見
- インシデントの迅速な対応
- リソース使用状況の把握

### 1.2 監視対象

- アプリケーション
- インフラストラクチャ
- データベース
- ネットワーク
- セキュリティ

## 2. モニタリング構成

### 2.1 監視ツール

```
モニタリングスタック
├── Prometheus
│   ├── メトリクス収集
│   └── 時系列データベース
├── Grafana
│   ├── ダッシュボード
│   └── アラート設定
├── ELK Stack
│   ├── ログ収集
│   ├── ログ分析
│   └── ログ可視化
└── AlertManager
    ├── アラート管理
    └── 通知設定
```

### 2.2 監視設定

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'dataset-management-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scheme: 'https'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

## 3. メトリクス

### 3.1 アプリケーションメトリクス

1. **APIメトリクス**
   ```python
   # メトリクス定義
   from prometheus_client import Counter, Histogram

   # リクエスト数
   REQUEST_COUNT = Counter(
       'api_requests_total',
       'Total number of API requests',
       ['method', 'endpoint', 'status']
   )

   # レスポンス時間
   REQUEST_LATENCY = Histogram(
       'api_request_duration_seconds',
       'API request latency in seconds',
       ['method', 'endpoint']
   )
   ```

2. **ビジネスメトリクス**
   ```python
   # データセット関連メトリクス
   DATASET_COUNT = Counter(
       'datasets_total',
       'Total number of datasets',
       ['status']
   )

   DATASET_SIZE = Gauge(
       'dataset_size_bytes',
       'Size of datasets in bytes',
       ['dataset_id']
   )
   ```

### 3.2 インフラメトリクス

1. **システムメトリクス**
   - CPU使用率
   - メモリ使用率
   - ディスク使用率
   - ネットワークトラフィック

2. **データベースメトリクス**
   - 接続数
   - クエリ実行時間
   - キャッシュヒット率
   - レプリケーションラグ

## 4. アラート設定

### 4.1 アラートルール

```yaml
# alert.rules
groups:
- name: dataset-management
  rules:
  - alert: HighErrorRate
    expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "高エラー率を検出"
      description: "5xxエラーが10%を超えています"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "高レイテンシを検出"
      description: "95パーセンタイルのレイテンシが1秒を超えています"
```

### 4.2 通知設定

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'team-dataset'

receivers:
- name: 'team-dataset'
  slack_configs:
  - channel: '#alerts-dataset'
    send_resolved: true
  email_configs:
  - to: 'team@example.com'
    send_resolved: true
```

## 5. ダッシュボード

### 5.1 システムダッシュボード

```json
{
  "dashboard": {
    "title": "システム概要",
    "panels": [
      {
        "title": "APIリクエスト数",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "エラー率",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(api_requests_total{status=~\"5..\"}[5m]) / rate(api_requests_total[5m]) * 100",
            "legendFormat": "エラー率"
          }
        ]
      }
    ]
  }
}
```

### 5.2 ビジネスダッシュボード

```json
{
  "dashboard": {
    "title": "ビジネスメトリクス",
    "panels": [
      {
        "title": "データセット数",
        "type": "stat",
        "targets": [
          {
            "expr": "datasets_total",
            "legendFormat": "総データセット数"
          }
        ]
      },
      {
        "title": "データセットサイズ",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(dataset_size_bytes) by (dataset_id)",
            "legendFormat": "{{dataset_id}}"
          }
        ]
      }
    ]
  }
}
```

## 6. ログ管理

### 6.1 ログ収集設定

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  paths:
    - /var/log/dataset-management/*.log
  fields:
    app: dataset-management
  fields_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "dataset-management-%{+yyyy.MM.dd}"
```

### 6.2 ログ分析

1. **ログパターン**
   ```python
   # ログフォーマット
   LOG_FORMAT = {
       'timestamp': '%Y-%m-%d %H:%M:%S',
       'level': 'INFO',
       'service': 'dataset-management',
       'message': 'メッセージ',
       'context': {
           'request_id': 'uuid',
           'user_id': 'user123',
           'action': 'create_dataset'
       }
   }
   ```

2. **ログ検索**
   ```json
   {
     "query": {
       "bool": {
         "must": [
           { "match": { "level": "ERROR" } },
           { "range": { "@timestamp": { "gte": "now-1h" } } }
         ]
       }
     }
   }
   ```

## 7. インシデント対応

### 7.1 インシデントレベル

| レベル | 説明 | 対応時間 |
|--------|------|----------|
| P0 | システムダウン | 即時対応 |
| P1 | 重大な機能障害 | 1時間以内 |
| P2 | 部分的な機能障害 | 4時間以内 |
| P3 | 軽微な問題 | 24時間以内 |

### 7.2 対応フロー

1. **アラート検知**
   - アラート通知の受信
   - インシデントの初期評価
   - 担当者のアサイン

2. **調査と対応**
   - ログの確認
   - メトリクスの分析
   - 問題の特定と修正

3. **報告と改善**
   - インシデントレポートの作成
   - 再発防止策の検討
   - モニタリングの改善

## 8. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | アラートルールの追加 | 
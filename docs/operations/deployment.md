# デプロイメント手順

## 目次

1. [はじめに](#1-はじめに)
2. [デプロイメント環境](#2-デプロイメント環境)
3. [デプロイメント準備](#3-デプロイメント準備)
4. [デプロイメント手順](#4-デプロイメント手順)
5. [ロールバック手順](#5-ロールバック手順)
6. [検証手順](#6-検証手順)
7. [トラブルシューティング](#7-トラブルシューティング)

## 1. はじめに

このドキュメントは、データセット管理システムのデプロイメント手順を定義するものです。安全かつ効率的なデプロイメントを実現するための手順と注意事項を記載しています。

### 1.1 目的

- 安全なデプロイメントの実施
- システムダウンタイムの最小化
- デプロイメントの再現性確保
- トラブル発生時の迅速な対応

### 1.2 前提条件

- Kubernetesクラスタの準備
- 必要な認証情報の取得
- デプロイメント権限の確認
- バックアップの完了確認

## 2. デプロイメント環境

### 2.1 環境構成

```
本番環境
├── Kubernetesクラスタ
│   ├── マスターノード（3台）
│   └── ワーカーノード（5台）
├── データベース
│   ├── PostgreSQL（プライマリ）
│   └── PostgreSQL（レプリカ）
├── キャッシュ
│   └── Redis（クラスタ）
└── ストレージ
    └── S3互換ストレージ
```

### 2.2 リソース要件

| コンポーネント | CPU | メモリ | ストレージ |
|----------------|-----|--------|------------|
| APIサーバー | 2コア | 4GB | 20GB |
| フロントエンド | 1コア | 2GB | 10GB |
| データベース | 4コア | 8GB | 100GB |
| キャッシュ | 2コア | 4GB | 20GB |

## 3. デプロイメント準備

### 3.1 事前チェックリスト

- [ ] バックアップの完了
- [ ] 依存サービスの稼働確認
- [ ] デプロイメント用の認証情報確認
- [ ] リソース使用状況の確認
- [ ] メンテナンスウィンドウの通知

### 3.2 設定ファイル

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dataset-management-api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dataset-management-api
  template:
    metadata:
      labels:
        app: dataset-management-api
    spec:
      containers:
      - name: api
        image: dataset-management/api:1.0.0
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

## 4. デプロイメント手順

### 4.1 バックエンドデプロイメント

```bash
# 1. イメージのビルドとプッシュ
docker build -t dataset-management/api:1.0.0 .
docker push dataset-management/api:1.0.0

# 2. 設定の更新
kubectl apply -f k8s/config.yaml

# 3. デプロイメントの実行
kubectl apply -f k8s/deployment.yaml

# 4. デプロイメントの確認
kubectl rollout status deployment/dataset-management-api
```

### 4.2 フロントエンドデプロイメント

```bash
# 1. ビルド
npm run build

# 2. 静的ファイルのアップロード
aws s3 sync build/ s3://dataset-management-frontend/

# 3. CDNのキャッシュクリア
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

### 4.3 データベースマイグレーション

```bash
# 1. マイグレーションファイルの確認
alembic current

# 2. マイグレーションの実行
alembic upgrade head

# 3. マイグレーション状態の確認
alembic history
```

## 5. ロールバック手順

### 5.1 クイックロールバック

```bash
# 1. 前バージョンの確認
kubectl rollout history deployment/dataset-management-api

# 2. ロールバックの実行
kubectl rollout undo deployment/dataset-management-api

# 3. ロールバックの確認
kubectl rollout status deployment/dataset-management-api
```

### 5.2 データベースロールバック

```bash
# 1. マイグレーションのロールバック
alembic downgrade -1

# 2. ロールバックの確認
alembic current
```

## 6. 検証手順

### 6.1 システム検証

1. **API検証**
   ```bash
   # ヘルスチェック
   curl https://api.dataset-management.com/health
   
   # 主要エンドポイントの検証
   curl https://api.dataset-management.com/api/v1/datasets
   ```

2. **フロントエンド検証**
   - ブラウザでの表示確認
   - 主要機能の動作確認
   - エラーページの確認

3. **パフォーマンス検証**
   ```bash
   # 負荷テストの実行
   locust -f tests/performance/locustfile.py
   ```

### 6.2 監視設定

```yaml
# monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dataset-management-api
spec:
  selector:
    matchLabels:
      app: dataset-management-api
  endpoints:
  - port: metrics
    interval: 15s
```

## 7. トラブルシューティング

### 7.1 一般的な問題

1. **デプロイメント失敗**
   ```bash
   # ログの確認
   kubectl logs deployment/dataset-management-api
   
   # イベントの確認
   kubectl get events
   ```

2. **パフォーマンス問題**
   ```bash
   # リソース使用状況の確認
   kubectl top pods
   
   # メトリクスの確認
   curl http://localhost:9090/metrics
   ```

### 7.2 緊急時の対応

1. **システムダウンの場合**
   - ロールバックの実行
   - サポートチームへの連絡
   - インシデントレポートの作成

2. **データ不整合の場合**
   - バックアップからのリストア
   - 整合性チェックの実行
   - 影響範囲の特定

## 8. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | ロールバック手順の追加 | 
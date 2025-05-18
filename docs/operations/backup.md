# バックアップとリストア手順

## 目次

1. [はじめに](#1-はじめに)
2. [バックアップ戦略](#2-バックアップ戦略)
3. [バックアップ手順](#3-バックアップ手順)
4. [リストア手順](#4-リストア手順)
5. [検証手順](#5-検証手順)
6. [トラブルシューティング](#6-トラブルシューティング)

## 1. はじめに

このドキュメントは、データセット管理システムのバックアップとリストア手順を定義するものです。データの安全性と可用性を確保するための重要な手順を提供します。

### 1.1 目的

- データの保護
- 災害復旧の準備
- システム復旧の迅速化
- データ整合性の維持

### 1.2 バックアップ対象

- データベース
- ファイルストレージ
- 設定ファイル
- ログファイル

## 2. バックアップ戦略

### 2.1 バックアップタイプ

| タイプ | 頻度 | 保持期間 | 用途 |
|--------|------|----------|------|
| フルバックアップ | 週1回 | 1ヶ月 | 完全なシステム復旧 |
| 差分バックアップ | 日1回 | 1週間 | 前回のフルバックアップからの変更 |
| 増分バックアップ | 6時間ごと | 3日間 | 最新の変更の保護 |

### 2.2 バックアップスケジュール

```yaml
# backup-schedule.yml
schedules:
  full_backup:
    cron: "0 0 * * 0"  # 毎週日曜日 00:00
    type: full
    retention: 30d

  differential_backup:
    cron: "0 0 * * *"  # 毎日 00:00
    type: differential
    retention: 7d

  incremental_backup:
    cron: "0 */6 * * *"  # 6時間ごと
    type: incremental
    retention: 3d
```

## 3. バックアップ手順

### 3.1 データベースバックアップ

1. **PostgreSQLバックアップ**
   ```bash
   # フルバックアップ
   pg_dump -h localhost -U postgres -d dataset_management \
     -F c -b -v -f "/backup/db/full_$(date +%Y%m%d).dump"

   # 差分バックアップ
   pg_dump -h localhost -U postgres -d dataset_management \
     --data-only --exclude-table-data=audit_logs \
     -F c -b -v -f "/backup/db/diff_$(date +%Y%m%d).dump"
   ```

2. **バックアップスクリプト**
   ```python
   # backup_db.py
   import subprocess
   import datetime
   import os

   def backup_database(backup_type='full'):
       timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
       backup_dir = f"/backup/db/{backup_type}"
       os.makedirs(backup_dir, exist_ok=True)
       
       cmd = [
           'pg_dump',
           '-h', 'localhost',
           '-U', 'postgres',
           '-d', 'dataset_management',
           '-F', 'c',
           '-b',
           '-v',
           '-f', f"{backup_dir}/backup_{timestamp}.dump"
       ]
       
       if backup_type == 'differential':
           cmd.extend(['--data-only', '--exclude-table-data=audit_logs'])
       
       subprocess.run(cmd, check=True)
   ```

### 3.2 ファイルストレージバックアップ

1. **S3バックアップ**
   ```bash
   # バックアップスクリプト
   aws s3 sync s3://dataset-management-storage \
     s3://dataset-management-backup/$(date +%Y%m%d) \
     --exclude "*.tmp" \
     --exclude "temp/*"
   ```

2. **バックアップ検証**
   ```python
   # verify_backup.py
   import boto3
   import hashlib

   def verify_s3_backup(source_bucket, backup_bucket, backup_date):
       s3 = boto3.client('s3')
       
       # ソースとバックアップのオブジェクトリストを取得
       source_objects = s3.list_objects_v2(Bucket=source_bucket)
       backup_objects = s3.list_objects_v2(
           Bucket=backup_bucket,
           Prefix=backup_date
       )
       
       # オブジェクトの整合性チェック
       for obj in source_objects['Contents']:
           if obj['Key'].endswith('.tmp') or 'temp/' in obj['Key']:
               continue
               
           backup_key = f"{backup_date}/{obj['Key']}"
           if not any(b['Key'] == backup_key for b in backup_objects['Contents']):
               raise Exception(f"Missing backup: {obj['Key']}")
   ```

### 3.3 設定ファイルバックアップ

```bash
# 設定ファイルのバックアップ
tar -czf "/backup/config/config_$(date +%Y%m%d).tar.gz" \
  /etc/dataset-management \
  /opt/dataset-management/config
```

## 4. リストア手順

### 4.1 データベースリストア

1. **フルリストア**
   ```bash
   # データベースの停止
   systemctl stop dataset-management-api
   
   # リストアの実行
   pg_restore -h localhost -U postgres -d dataset_management \
     -v -c "/backup/db/full_20240321.dump"
   
   # データベースの起動
   systemctl start dataset-management-api
   ```

2. **ポイントインタイムリカバリ**
   ```python
   # point_in_time_recovery.py
   def restore_to_point_in_time(target_time):
       # 最新のフルバックアップをリストア
       restore_full_backup()
       
       # 差分バックアップを適用
       apply_differential_backups(target_time)
       
       # 増分バックアップを適用
       apply_incremental_backups(target_time)
       
       # データベースの整合性チェック
       verify_database_integrity()
   ```

### 4.2 ファイルストレージリストア

```bash
# S3からのリストア
aws s3 sync s3://dataset-management-backup/20240321 \
  s3://dataset-management-storage \
  --delete

# リストアの検証
aws s3 sync s3://dataset-management-backup/20240321 \
  s3://dataset-management-storage \
  --dryrun
```

### 4.3 設定ファイルリストア

```bash
# 設定ファイルのリストア
tar -xzf "/backup/config/config_20240321.tar.gz" -C /

# 権限の設定
chown -R dataset-management:dataset-management \
  /etc/dataset-management \
  /opt/dataset-management/config
```

## 5. 検証手順

### 5.1 バックアップ検証

1. **データベース検証**
   ```python
   def verify_database_backup(backup_file):
       # バックアップファイルの存在確認
       if not os.path.exists(backup_file):
           raise Exception(f"Backup file not found: {backup_file}")
       
       # バックアップの整合性チェック
       result = subprocess.run(
           ['pg_restore', '-l', backup_file],
           capture_output=True,
           text=True
       )
       
       if result.returncode != 0:
           raise Exception(f"Invalid backup file: {backup_file}")
   ```

2. **ファイルストレージ検証**
   ```python
   def verify_storage_backup(backup_date):
       # バックアップの存在確認
       backup_objects = s3.list_objects_v2(
           Bucket='dataset-management-backup',
           Prefix=backup_date
       )
       
       if not backup_objects['Contents']:
           raise Exception(f"No backup found for date: {backup_date}")
       
       # オブジェクトの整合性チェック
       for obj in backup_objects['Contents']:
           verify_object_integrity(obj['Key'])
   ```

### 5.2 リストア検証

1. **アプリケーション検証**
   ```python
   def verify_application_health():
       # APIの健全性チェック
       response = requests.get('https://api.example.com/health')
       if response.status_code != 200:
           raise Exception("API health check failed")
       
       # データベース接続チェック
       db = Database()
       if not db.is_connected():
           raise Exception("Database connection failed")
       
       # ストレージ接続チェック
       storage = Storage()
       if not storage.is_accessible():
           raise Exception("Storage access failed")
   ```

2. **データ整合性検証**
   ```python
   def verify_data_integrity():
       # データセットの整合性チェック
       datasets = Dataset.query.all()
       for dataset in datasets:
           if not dataset.verify_integrity():
               raise Exception(f"Dataset integrity check failed: {dataset.id}")
       
       # メタデータの整合性チェック
       metadata = Metadata.query.all()
       for meta in metadata:
           if not meta.verify_integrity():
               raise Exception(f"Metadata integrity check failed: {meta.id}")
   ```

## 6. トラブルシューティング

### 6.1 一般的な問題

1. **バックアップ失敗**
   - ディスク容量の確認
   - 権限の確認
   - ネットワーク接続の確認
   - ログの確認

2. **リストア失敗**
   - バックアップファイルの整合性確認
   - データベースの状態確認
   - ストレージの状態確認
   - ログの確認

### 6.2 エラー対応

```python
# error_handling.py
def handle_backup_error(error):
    if isinstance(error, DatabaseError):
        # データベースエラーの処理
        notify_admin("Database backup failed", error)
        retry_backup()
    elif isinstance(error, StorageError):
        # ストレージエラーの処理
        notify_admin("Storage backup failed", error)
        retry_storage_backup()
    else:
        # その他のエラーの処理
        notify_admin("Backup failed", error)
        log_error(error)
```

## 7. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | バックアップ検証手順の追加 | 
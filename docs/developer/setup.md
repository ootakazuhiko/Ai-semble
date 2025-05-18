# 開発環境セットアップガイド

## 目次

1. [はじめに](#1-はじめに)
2. [前提条件](#2-前提条件)
3. [開発環境のセットアップ](#3-開発環境のセットアップ)
4. [プロジェクトの初期化](#4-プロジェクトの初期化)
5. [開発サーバーの起動](#5-開発サーバーの起動)
6. [テスト環境のセットアップ](#6-テスト環境のセットアップ)
7. [トラブルシューティング](#7-トラブルシューティング)

## 1. はじめに

このガイドでは、データセット管理システムの開発環境をセットアップする手順を説明します。開発を始める前に、このガイドに従って環境を整えてください。

## 2. 前提条件

### 2.1 必要なソフトウェア

- Python 3.9以上
- Node.js 18以上
- Git
- Docker
- Docker Compose
- PostgreSQL 14以上
- Redis 6以上

### 2.2 推奨開発ツール

- Visual Studio Code
- PyCharm Professional
- DBeaver（データベース管理）
- Postman（APIテスト）

### 2.3 システム要件

- CPU: 4コア以上
- メモリ: 8GB以上
- ストレージ: 20GB以上の空き容量
- OS: Windows 10/11、macOS、Linux

## 3. 開発環境のセットアップ

### 3.1 Python環境のセットアップ

```bash
# Pythonのインストール（Windows）
winget install Python.Python.3.9

# Pythonのインストール（macOS）
brew install python@3.9

# Pythonのインストール（Linux）
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化（Windows）
.\venv\Scripts\activate

# 仮想環境の有効化（macOS/Linux）
source venv/bin/activate
```

### 3.2 Node.js環境のセットアップ

```bash
# Node.jsのインストール（Windows）
winget install OpenJS.NodeJS.LTS

# Node.jsのインストール（macOS）
brew install node@18

# Node.jsのインストール（Linux）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# バージョン確認
node --version
npm --version
```

### 3.3 Docker環境のセットアップ

```bash
# Docker Desktopのインストール（Windows/macOS）
# https://www.docker.com/products/docker-desktop からダウンロード

# Dockerのインストール（Linux）
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Docker Composeのインストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# バージョン確認
docker --version
docker-compose --version
```

## 4. プロジェクトの初期化

### 4.1 リポジトリのクローン

```bash
# リポジトリのクローン
git clone https://github.com/your-org/ai-semble.git
cd ai-semble

# 開発ブランチの作成
git checkout -b feature/your-feature-name
```

### 4.2 依存関係のインストール

```bash
# Python依存関係のインストール
pip install -r requirements/dev.txt

# Node.js依存関係のインストール
npm install

# 開発用の環境変数設定
cp .env.example .env
```

### 4.3 データベースのセットアップ

```bash
# PostgreSQLコンテナの起動
docker-compose up -d postgres

# データベースの作成
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE ai_semble_dev;"

# マイグレーションの実行
alembic upgrade head

# シードデータの投入
python scripts/seed_data.py
```

### 4.4 Redisのセットアップ

```bash
# Redisコンテナの起動
docker-compose up -d redis

# Redisの接続確認
docker-compose exec redis redis-cli ping
```

## 5. 開発サーバーの起動

### 5.1 バックエンドサーバーの起動

```bash
# 開発サーバーの起動
uvicorn app.main:app --reload --port 8000

# 別のターミナルでワーカーの起動
celery -A app.worker worker --loglevel=info
```

### 5.2 フロントエンドサーバーの起動

```bash
# 開発サーバーの起動
npm run dev

# ビルド
npm run build
```

### 5.3 サービスの確認

以下のURLで各サービスにアクセスできます：

- バックエンドAPI: http://localhost:8000
- フロントエンド: http://localhost:3000
- APIドキュメント: http://localhost:8000/docs
- 管理画面: http://localhost:8000/admin

## 6. テスト環境のセットアップ

### 6.1 テストデータベースの準備

```bash
# テスト用データベースの作成
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE ai_semble_test;"

# テスト用の環境変数設定
cp .env.test.example .env.test
```

### 6.2 テストの実行

```bash
# バックエンドテストの実行
pytest

# フロントエンドテストの実行
npm test

# カバレッジレポートの生成
pytest --cov=app tests/
npm run test:coverage
```

## 7. トラブルシューティング

### 7.1 よくある問題と解決方法

#### 7.1.1 ポートの競合

**症状**: ポートが既に使用されている
**解決方法**:
```bash
# 使用中のポートを確認（Windows）
netstat -ano | findstr :8000

# 使用中のポートを確認（macOS/Linux）
lsof -i :8000

# プロセスの終了
kill -9 <PID>
```

#### 7.1.2 データベース接続エラー

**症状**: データベースに接続できない
**解決方法**:
```bash
# コンテナの状態確認
docker-compose ps

# ログの確認
docker-compose logs postgres

# コンテナの再起動
docker-compose restart postgres
```

#### 7.1.3 依存関係のエラー

**症状**: パッケージのインストールに失敗
**解決方法**:
```bash
# キャッシュのクリア
pip cache purge
npm cache clean --force

# 仮想環境の再作成
rm -rf venv
python -m venv venv
source venv/bin/activate  # または .\venv\Scripts\activate
pip install -r requirements/dev.txt
```

### 7.2 デバッグツール

#### 7.2.1 バックエンドのデバッグ

```python
# デバッグログの有効化
import logging
logging.basicConfig(level=logging.DEBUG)

# ブレークポイントの設定
import pdb; pdb.set_trace()
```

#### 7.2.2 フロントエンドのデバッグ

```javascript
// デバッグログの出力
console.debug('Debug message');

// ブレークポイントの設定
debugger;
```

### 7.3 サポート

問題が解決しない場合は、以下の方法でサポートを受けることができます：

1. プロジェクトのIssueトラッカーで問題を報告
2. 開発者チャット（Slack）で質問
3. 技術文書の参照
4. コードレビューの依頼

## 8. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | トラブルシューティングセクション追加 | 
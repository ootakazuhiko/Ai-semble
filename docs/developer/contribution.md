# プロジェクト貢献ガイドライン

## 目次

1. [はじめに](#1-はじめに)
2. [開発フロー](#2-開発フロー)
3. [コーディング規約](#3-コーディング規約)
4. [コミットメッセージ規約](#4-コミットメッセージ規約)
5. [プルリクエスト](#5-プルリクエスト)
6. [テスト](#6-テスト)
7. [ドキュメント](#7-ドキュメント)
8. [レビュー](#8-レビュー)
9. [リリース](#9-リリース)

## 1. はじめに

このドキュメントは、データセット管理システムへの貢献方法を説明するものです。プロジェクトの品質を維持し、効率的な開発を促進するために、以下のガイドラインに従ってください。

### 1.1 貢献の種類

- バグ修正
- 新機能の追加
- ドキュメントの改善
- パフォーマンスの最適化
- テストの追加
- コードのリファクタリング

### 1.2 前提条件

- GitHubアカウント
- Gitの基本的な知識
- Python 3.9+の開発環境
- Node.js 16+の開発環境
- Dockerの基本的な知識

## 2. 開発フロー

### 2.1 リポジトリのセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/your-org/dataset-management.git
cd dataset-management

# 開発用ブランチの作成
git checkout -b feature/your-feature-name
```

### 2.2 開発環境の準備

```bash
# Python仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linuxの場合
.\venv\Scripts\activate   # Windowsの場合

# 依存関係のインストール
pip install -r requirements-dev.txt
npm install
```

### 2.3 ブランチ戦略

- `main`: 本番環境用の安定ブランチ
- `develop`: 開発用の統合ブランチ
- `feature/*`: 新機能開発用ブランチ
- `bugfix/*`: バグ修正用ブランチ
- `hotfix/*`: 緊急バグ修正用ブランチ
- `release/*`: リリース準備用ブランチ

## 3. コーディング規約

### 3.1 Python

- PEP 8に準拠
- 型ヒントの使用
- docstringの記述
- 最大行長: 88文字（Black準拠）

```python
from typing import List, Optional

def process_dataset(
    dataset_id: str,
    options: Optional[dict] = None
) -> List[dict]:
    """
    データセットを処理する関数

    Args:
        dataset_id: データセットのID
        options: 処理オプション

    Returns:
        処理結果のリスト

    Raises:
        DatasetNotFoundError: データセットが見つからない場合
    """
    pass
```

### 3.2 TypeScript/JavaScript

- ESLint + Prettierの設定に準拠
- 型定義の使用
- JSDocの記述
- 最大行長: 100文字

```typescript
interface DatasetOptions {
  validate?: boolean;
  notify?: boolean;
}

/**
 * データセットを処理する関数
 * @param datasetId - データセットのID
 * @param options - 処理オプション
 * @returns 処理結果の配列
 * @throws {DatasetNotFoundError} データセットが見つからない場合
 */
async function processDataset(
  datasetId: string,
  options?: DatasetOptions
): Promise<DatasetResult[]> {
  // 実装
}
```

### 3.3 SQL

- キーワードは大文字
- インデントは4スペース
- テーブル名は複数形
- カラム名はスネークケース

```sql
CREATE TABLE datasets (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_datasets_name ON datasets (name);
```

## 4. コミットメッセージ規約

### 4.1 形式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 4.2 タイプ

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの意味に影響を与えない変更
- `refactor`: バグ修正や機能追加を含まないコードの変更
- `test`: テストの追加・修正
- `chore`: ビルドプロセスやツールの変更

### 4.3 例

```
feat(api): データセット検索APIの追加

- 全文検索機能の実装
- フィルタリング機能の追加
- ページネーションの実装

Closes #123
```

## 5. プルリクエスト

### 5.1 作成手順

1. 最新の`develop`ブランチを取得
2. 機能ブランチを作成
3. 変更を実装
4. テストを実行
5. プルリクエストを作成

### 5.2 テンプレート

```markdown
## 変更内容
<!-- 変更の概要を説明 -->

## 関連Issue
<!-- 関連するIssue番号 -->

## テスト
<!-- 実行したテストの説明 -->

## スクリーンショット
<!-- UIの変更がある場合 -->

## チェックリスト
- [ ] テストを追加/更新しました
- [ ] ドキュメントを更新しました
- [ ] コードのフォーマットを確認しました
- [ ] リンターの警告を修正しました
```

## 6. テスト

### 6.1 テストの種類

- ユニットテスト
- 統合テスト
- E2Eテスト
- パフォーマンステスト

### 6.2 テスト実行

```bash
# バックエンドテスト
pytest

# フロントエンドテスト
npm test

# カバレッジレポート
pytest --cov=app tests/
npm run test:coverage
```

### 6.3 テストカバレッジ要件

- バックエンド: 80%以上
- フロントエンド: 70%以上
- クリティカルパス: 100%

## 7. ドキュメント

### 7.1 ドキュメントの種類

- API仕様書
- ユーザーガイド
- 開発者ガイド
- アーキテクチャ設計書
- 変更履歴

### 7.2 ドキュメント更新

- 新機能追加時
- API変更時
- バグ修正時
- 設定変更時

## 8. レビュー

### 8.1 レビュー基準

- コードの品質
- テストの網羅性
- パフォーマンスへの影響
- セキュリティへの影響
- ドキュメントの更新

### 8.2 レビュープロセス

1. コードレビュー依頼
2. レビューコメント
3. 修正対応
4. 承認
5. マージ

## 9. リリース

### 9.1 リリースプロセス

1. バージョン番号の決定
2. 変更履歴の更新
3. リリースブランチの作成
4. テストの実行
5. ドキュメントの更新
6. リリースノートの作成
7. タグの作成
8. デプロイ

### 9.2 バージョニング

セマンティックバージョニング（SemVer）に従う：

- メジャーバージョン: 後方互換性のない変更
- マイナーバージョン: 後方互換性のある機能追加
- パッチバージョン: バグ修正

## 10. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | レビュープロセスの詳細追加 | 
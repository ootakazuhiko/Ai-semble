# テストケース

## 目次

1. [はじめに](#1-はじめに)
2. [バックエンドテストケース](#2-バックエンドテストケース)
3. [フロントエンドテストケース](#3-フロントエンドテストケース)
4. [APIテストケース](#4-apiテストケース)
5. [統合テストケース](#5-統合テストケース)
6. [E2Eテストケース](#6-e2eテストケース)

## 1. はじめに

このドキュメントは、データセット管理システムの主要なテストケースを説明するものです。各機能のテスト要件と期待される動作を定義しています。

### 1.1 テストケースの構成

- テストID
- テスト名
- 前提条件
- テスト手順
- 期待結果
- テストデータ
- 備考

### 1.2 テストケースの優先度

- P0: クリティカル（必須）
- P1: 重要
- P2: 通常
- P3: 低優先度

## 2. バックエンドテストケース

### 2.1 データセット管理

#### TC-BE-001: データセット作成

```python
# テストケース
def test_create_dataset():
    """
    テストID: TC-BE-001
    優先度: P0
    テスト名: データセット作成の基本機能
    """
    # 前提条件
    dataset_data = {
        "name": "テストデータセット",
        "description": "テスト用データセット",
        "version": "1.0.0"
    }

    # テスト手順
    dataset = create_dataset(dataset_data)

    # 期待結果
    assert dataset.id is not None
    assert dataset.name == dataset_data["name"]
    assert dataset.status == DatasetStatus.DRAFT
```

#### TC-BE-002: データセット更新

```python
# テストケース
def test_update_dataset():
    """
    テストID: TC-BE-002
    優先度: P1
    テスト名: データセット更新の基本機能
    """
    # 前提条件
    dataset = create_test_dataset()
    update_data = {
        "name": "更新されたデータセット",
        "description": "更新された説明"
    }

    # テスト手順
    updated_dataset = update_dataset(dataset.id, update_data)

    # 期待結果
    assert updated_dataset.name == update_data["name"]
    assert updated_dataset.description == update_data["description"]
```

### 2.2 メタデータ管理

#### TC-BE-003: メタデータ登録

```python
# テストケース
def test_register_metadata():
    """
    テストID: TC-BE-003
    優先度: P1
    テスト名: メタデータ登録の基本機能
    """
    # 前提条件
    dataset = create_test_dataset()
    metadata = {
        "format": "CSV",
        "columns": ["id", "name", "value"],
        "size": 1024
    }

    # テスト手順
    result = register_metadata(dataset.id, metadata)

    # 期待結果
    assert result.dataset_id == dataset.id
    assert result.metadata == metadata
```

## 3. フロントエンドテストケース

### 3.1 データセット一覧

#### TC-FE-001: データセット一覧表示

```typescript
// テストケース
describe('DatasetList', () => {
  it('データセット一覧を表示する', () => {
    /**
     * テストID: TC-FE-001
     * 優先度: P0
     * テスト名: データセット一覧表示の基本機能
     */
    // 前提条件
    const mockDatasets = [
      {
        id: '1',
        name: 'テストデータセット1',
        version: '1.0.0'
      },
      {
        id: '2',
        name: 'テストデータセット2',
        version: '1.0.0'
      }
    ];

    // テスト手順
    const { getByText } = render(<DatasetList datasets={mockDatasets} />);

    // 期待結果
    expect(getByText('テストデータセット1')).toBeInTheDocument();
    expect(getByText('テストデータセット2')).toBeInTheDocument();
  });
});
```

### 3.2 データセット詳細

#### TC-FE-002: データセット詳細表示

```typescript
// テストケース
describe('DatasetDetail', () => {
  it('データセット詳細を表示する', () => {
    /**
     * テストID: TC-FE-002
     * 優先度: P0
     * テスト名: データセット詳細表示の基本機能
     */
    // 前提条件
    const mockDataset = {
      id: '1',
      name: 'テストデータセット',
      description: 'テスト用データセット',
      version: '1.0.0',
      metadata: {
        format: 'CSV',
        size: 1024
      }
    };

    // テスト手順
    const { getByText } = render(<DatasetDetail dataset={mockDataset} />);

    // 期待結果
    expect(getByText('テストデータセット')).toBeInTheDocument();
    expect(getByText('テスト用データセット')).toBeInTheDocument();
    expect(getByText('CSV')).toBeInTheDocument();
  });
});
```

## 4. APIテストケース

### 4.1 データセットAPI

#### TC-API-001: データセット作成API

```python
# テストケース
def test_create_dataset_api():
    """
    テストID: TC-API-001
    優先度: P0
    テスト名: データセット作成APIの基本機能
    """
    # 前提条件
    dataset_data = {
        "name": "APIテストデータセット",
        "description": "APIテスト用データセット",
        "version": "1.0.0"
    }

    # テスト手順
    response = client.post("/api/v1/datasets", json=dataset_data)

    # 期待結果
    assert response.status_code == 201
    assert response.json()["name"] == dataset_data["name"]
```

#### TC-API-002: データセット検索API

```python
# テストケース
def test_search_datasets_api():
    """
    テストID: TC-API-002
    優先度: P1
    テスト名: データセット検索APIの基本機能
    """
    # 前提条件
    create_test_datasets(5)

    # テスト手順
    response = client.get("/api/v1/datasets?q=test&page=1&size=10")

    # 期待結果
    assert response.status_code == 200
    assert len(response.json()["items"]) <= 10
    assert response.json()["total"] >= 5
```

## 5. 統合テストケース

### 5.1 データセット管理フロー

#### TC-INT-001: データセット作成から公開までのフロー

```python
# テストケース
def test_dataset_creation_to_publication():
    """
    テストID: TC-INT-001
    優先度: P0
    テスト名: データセット作成から公開までの統合フロー
    """
    # 前提条件
    dataset_data = {
        "name": "統合テストデータセット",
        "description": "統合テスト用データセット",
        "version": "1.0.0"
    }

    # テスト手順
    # 1. データセット作成
    dataset = create_dataset(dataset_data)
    assert dataset.status == DatasetStatus.DRAFT

    # 2. メタデータ登録
    metadata = register_metadata(dataset.id, {"format": "CSV"})
    assert metadata is not None

    # 3. 品質チェック実行
    quality_result = run_quality_check(dataset.id)
    assert quality_result.status == QualityStatus.PASSED

    # 4. データセット公開
    published_dataset = publish_dataset(dataset.id)
    assert published_dataset.status == DatasetStatus.PUBLISHED
```

## 6. E2Eテストケース

### 6.1 ユーザーフロー

#### TC-E2E-001: データセット管理の基本フロー

```typescript
// テストケース
describe('Dataset Management Flow', () => {
  it('データセットの作成から公開までのフロー', async () => {
    /**
     * テストID: TC-E2E-001
     * 優先度: P0
     * テスト名: データセット管理の基本E2Eフロー
     */
    // 前提条件
    await loginAsTestUser();

    // テスト手順
    // 1. データセット作成画面へ移動
    await page.goto('/datasets/new');
    await expect(page).toHaveTitle('データセット作成');

    // 2. データセット情報入力
    await page.fill('[name="name"]', 'E2Eテストデータセット');
    await page.fill('[name="description"]', 'E2Eテスト用データセット');
    await page.click('button[type="submit"]');

    // 3. メタデータ登録
    await page.waitForSelector('.metadata-form');
    await page.fill('[name="format"]', 'CSV');
    await page.click('button[type="submit"]');

    // 4. 品質チェック実行
    await page.click('button:has-text("品質チェック実行")');
    await page.waitForSelector('.quality-check-complete');

    // 5. データセット公開
    await page.click('button:has-text("公開")');
    await page.waitForSelector('.publication-complete');

    // 期待結果
    await expect(page).toHaveText('データセットが公開されました');
  });
});
```

## 7. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | E2Eテストケースの追加 | 
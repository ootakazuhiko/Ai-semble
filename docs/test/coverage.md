# テストカバレッジ

## 目次

1. [はじめに](#1-はじめに)
2. [カバレッジ要件](#2-カバレッジ要件)
3. [カバレッジ計測](#3-カバレッジ計測)
4. [カバレッジレポート](#4-カバレッジレポート)
5. [カバレッジ改善](#5-カバレッジ改善)
6. [カバレッジ管理プロセス](#6-カバレッジ管理プロセス)

## 1. はじめに

このドキュメントは、データセット管理システムのテストカバレッジ要件と管理方法を定義するものです。品質保証の観点から、適切なテストカバレッジを維持することは重要です。

### 1.1 目的

- コードの品質を確保する
- テストの網羅性を保証する
- リグレッションを防止する
- コードの保守性を向上させる

### 1.2 対象範囲

- バックエンド（Python）
- フロントエンド（TypeScript）
- APIエンドポイント
- データベース操作
- ユーティリティ関数

## 2. カバレッジ要件

### 2.1 最小カバレッジ要件

| カテゴリ | 最小カバレッジ | 備考 |
|----------|----------------|------|
| バックエンド | 80% | クリティカルパスは100% |
| フロントエンド | 70% | ユーザーインタラクションは90% |
| API | 85% | 認証・認可は100% |
| データベース | 75% | トランザクション処理は100% |
| ユーティリティ | 80% | 共通ライブラリは90% |

### 2.2 カバレッジの種類

1. **行カバレッジ（Line Coverage）**
   - 実行されたコード行の割合
   - 最小要件：80%

2. **分岐カバレッジ（Branch Coverage）**
   - 実行された条件分岐の割合
   - 最小要件：75%

3. **関数カバレッジ（Function Coverage）**
   - 実行された関数の割合
   - 最小要件：85%

4. **文カバレッジ（Statement Coverage）**
   - 実行された文の割合
   - 最小要件：80%

## 3. カバレッジ計測

### 3.1 バックエンド（Python）

```python
# pytest.ini
[pytest]
addopts = --cov=app --cov-report=html --cov-report=term-missing
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# カバレッジ計測の実行
def test_coverage():
    """
    テストカバレッジの計測を実行
    """
    import pytest
    import coverage

    # カバレッジ計測の開始
    cov = coverage.Coverage(
        branch=True,
        source=['app'],
        omit=['*/tests/*', '*/migrations/*']
    )
    cov.start()

    # テストの実行
    pytest.main(['tests'])

    # カバレッジレポートの生成
    cov.stop()
    cov.save()
    cov.html_report(directory='coverage_html')
    cov.report()
```

### 3.2 フロントエンド（TypeScript）

```typescript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'html'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{ts,tsx}',
    '!src/**/*.test.{ts,tsx}'
  ]
};

// カバレッジ計測の実行
describe('Coverage', () => {
  it('should maintain minimum coverage', () => {
    // テストの実行
    // Jestが自動的にカバレッジレポートを生成
  });
});
```

## 4. カバレッジレポート

### 4.1 レポート形式

1. **HTMLレポート**
   - 詳細なカバレッジ情報
   - 行ごとの実行状況
   - 分岐カバレッジの詳細
   - 未カバーのコードの表示

2. **コンソールレポート**
   - 概要レポート
   - 未カバーの行の一覧
   - カバレッジの傾向

3. **CI/CDレポート**
   - カバレッジの推移
   - 閾値との比較
   - トレンド分析

### 4.2 レポートの例

```bash
# バックエンドカバレッジレポート
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
app/__init__.py            10      0   100%
app/models.py             150     20    87%   24-30, 45-50
app/services.py           200     35    83%   67-80, 120-130
app/utils.py              100     15    85%   45-55
-----------------------------------------------------
TOTAL                     460     70    85%

# フロントエンドカバレッジレポート
File                |  % Stmts | % Branch | % Funcs | % Lines
--------------------|----------|-----------|---------|--------
All files          |    85.71 |     75.00 |   83.33 |   85.71
 components/        |    88.89 |     80.00 |   85.71 |   88.89
 services/         |    83.33 |     70.00 |   80.00 |   83.33
 utils/            |    84.62 |     75.00 |   83.33 |   84.62
```

## 5. カバレッジ改善

### 5.1 改善プロセス

1. **現状分析**
   - カバレッジレポートの確認
   - 未カバー領域の特定
   - 優先度の設定

2. **テストの追加**
   - 未カバーコードの特定
   - テストケースの作成
   - テストの実行と検証

3. **コードの改善**
   - 不要なコードの削除
   - テスト容易性の向上
   - リファクタリング

### 5.2 改善の例

```python
# 改善前
def process_dataset(data):
    if not data:
        return None
    result = []
    for item in data:
        if item['status'] == 'active':
            result.append(item)
    return result

# 改善後
def process_dataset(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    データセットを処理する

    Args:
        data: 処理対象のデータセット

    Returns:
        処理済みのデータセット
    """
    if not data:
        return []
    
    return [
        item for item in data
        if item.get('status') == 'active'
    ]

# テストケース
def test_process_dataset():
    # 空のデータセット
    assert process_dataset([]) == []
    
    # 正常なデータセット
    data = [
        {'status': 'active', 'id': 1},
        {'status': 'inactive', 'id': 2},
        {'status': 'active', 'id': 3}
    ]
    expected = [
        {'status': 'active', 'id': 1},
        {'status': 'active', 'id': 3}
    ]
    assert process_dataset(data) == expected
```

## 6. カバレッジ管理プロセス

### 6.1 日常的な管理

1. **開発フェーズ**
   - プルリクエスト時のカバレッジチェック
   - 新規コードのカバレッジ要件
   - コードレビューでのカバレッジ確認

2. **リリースフェーズ**
   - リリース前のカバレッジ確認
   - カバレッジトレンドの分析
   - 改善計画の策定

3. **メンテナンスフェーズ**
   - 定期的なカバレッジ監視
   - 低下傾向の検出
   - 改善アクションの実施

### 6.2 自動化

```yaml
# .github/workflows/coverage.yml
name: Coverage Check

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest-cov
          
      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml
          
      - name: Check coverage threshold
        run: |
          python scripts/check_coverage.py
          
      - name: Upload coverage report
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

## 7. 更新履歴

| 日付 | バージョン | 変更内容 |
|------|------------|----------|
| 2024-03-21 | 1.0.0 | 初版リリース |
| 2024-03-22 | 1.0.1 | カバレッジ要件の更新 | 
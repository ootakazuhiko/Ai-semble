# データセット可視化機能 開発者ガイド

## アーキテクチャ概要

データセット可視化機能は、以下のコンポーネントで構成されています：

1. **APIレイヤー** (`src/api/visualization.py`)
   - FastAPIを使用したRESTful APIエンドポイント
   - リクエストのバリデーションと認証
   - レスポンスのフォーマット

2. **サービスレイヤー** (`src/data/visualization.py`)
   - `VisualizationService`クラスによる可視化ロジック
   - Plotlyを使用したグラフ生成
   - データセットサービスとの連携

3. **データレイヤー** (`src/data/service.py`)
   - `DatasetService`クラスによるデータセット管理
   - 統計情報の計算
   - 品質指標の計算

## 実装の詳細

### VisualizationService

`VisualizationService`クラスは、以下の主要なメソッドを提供します：

```python
class VisualizationService:
    def create_statistics_dashboard(
        self,
        dataset_id: int,
        version: Optional[str] = None,
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """統計情報ダッシュボードを作成"""

    def create_version_comparison_dashboard(
        self,
        dataset_id: int,
        version1: str,
        version2: str,
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """バージョン比較ダッシュボードを作成"""

    def create_quality_metrics_dashboard(
        self,
        dataset_id: int,
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """品質指標ダッシュボードを作成"""
```

### データフロー

1. 統計情報ダッシュボードの生成フロー：
   ```
   クライアント → APIエンドポイント → VisualizationService
   → DatasetService（統計情報取得）→ Plotlyグラフ生成 → レスポンス
   ```

2. バージョン比較ダッシュボードの生成フロー：
   ```
   クライアント → APIエンドポイント → VisualizationService
   → DatasetService（2つのバージョンの統計情報取得）
   → 差分計算 → Plotlyグラフ生成 → レスポンス
   ```

3. 品質指標ダッシュボードの生成フロー：
   ```
   クライアント → APIエンドポイント → VisualizationService
   → DatasetService（品質指標履歴取得）
   → 時系列データ処理 → Plotlyグラフ生成 → レスポンス
   ```

## テストの実行方法

### 環境セットアップ

1. 必要なパッケージのインストール：
   ```bash
   pip install -r requirements.txt
   ```

2. テストデータベースの準備：
   ```bash
   pytest tests/conftest.py -v
   ```

### テストの実行

1. すべてのテストを実行：
   ```bash
   pytest tests/api/test_visualization.py -v
   ```

2. 特定のテストを実行：
   ```bash
   pytest tests/api/test_visualization.py::test_get_statistics_dashboard -v
   ```

3. カバレッジレポートの生成：
   ```bash
   pytest --cov=src.api.visualization tests/api/test_visualization.py
   ```

## 拡張方法

### 新しい可視化タイプの追加

1. `VisualizationService`に新しいメソッドを追加：
   ```python
   def create_custom_dashboard(
       self,
       dataset_id: int,
       visualization_type: str,
       parameters: Dict[str, Any],
       output_path: Optional[Path] = None,
   ) -> Dict[str, Any]:
       """カスタムダッシュボードを作成"""
   ```

2. APIエンドポイントの追加：
   ```python
   @router.get("/datasets/{dataset_id}/custom")
   async def get_custom_dashboard(
       dataset_id: int,
       visualization_type: str,
       parameters: Dict[str, Any],
       output_format: str = Query("json", enum=["json", "html"]),
       output_path: Optional[str] = None,
       current_user: User = Depends(get_current_user),
       visualization_service: VisualizationService = Depends(get_visualization_service),
   ) -> Dict[str, Any]:
       """カスタムダッシュボードを取得"""
   ```

3. テストケースの追加：
   ```python
   def test_get_custom_dashboard(
       client,
       auth_headers,
       sample_dataset_with_versions,
   ):
       """カスタムダッシュボード取得のテスト"""
   ```

### 新しい出力形式の追加

1. `VisualizationService`の出力形式を拡張：
   ```python
   def _export_dashboard(
       self,
       figure: go.Figure,
       output_format: str,
       output_path: Optional[Path] = None,
   ) -> Dict[str, Any]:
       """ダッシュボードを指定された形式で出力"""
       if output_format == "json":
           return {"figure": figure.to_dict()}
       elif output_format == "html":
           if output_path:
               figure.write_html(output_path)
               return {"output_path": str(output_path)}
           else:
               return {"html": figure.to_html()}
       elif output_format == "png":
           if output_path:
               figure.write_image(output_path)
               return {"output_path": str(output_path)}
           else:
               return {"image": figure.to_image()}
   ```

2. APIエンドポイントのパラメータを更新：
   ```python
   output_format: str = Query("json", enum=["json", "html", "png"])
   ```

## パフォーマンス最適化

### キャッシュの活用

1. 統計情報のキャッシュ：
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def get_cached_statistics(
       self,
       dataset_id: int,
       version: str,
   ) -> Dict[str, Any]:
       """統計情報をキャッシュ付きで取得"""
   ```

2. グラフのキャッシュ：
   ```python
   @lru_cache(maxsize=50)
   def get_cached_figure(
       self,
       dataset_id: int,
       visualization_type: str,
       parameters: str,  # JSON文字列化したパラメータ
   ) -> go.Figure:
       """グラフをキャッシュ付きで生成"""
   ```

### 非同期処理

1. 長時間実行タスクの非同期処理：
   ```python
   from fastapi import BackgroundTasks

   @router.post("/datasets/{dataset_id}/statistics/refresh")
   async def refresh_statistics(
       background_tasks: BackgroundTasks,
       dataset_id: int,
       version: Optional[str] = None,
   ):
       """統計情報を非同期で再計算"""
       background_tasks.add_task(
           visualization_service.recalculate_statistics,
           dataset_id,
           version,
       )
   ```

## デバッグ方法

### ログ出力

1. ログレベルの設定：
   ```python
   import logging

   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)

   def create_statistics_dashboard(self, ...):
       logger.debug(f"Creating statistics dashboard for dataset {dataset_id}")
   ```

2. パフォーマンス計測：
   ```python
   import time

   def create_statistics_dashboard(self, ...):
       start_time = time.time()
       # ... 処理 ...
       logger.info(f"Dashboard creation took {time.time() - start_time:.2f} seconds")
   ```

### エラーハンドリング

1. 例外の詳細なログ出力：
   ```python
   try:
       result = self.create_statistics_dashboard(...)
   except Exception as e:
       logger.exception("Failed to create dashboard")
       raise HTTPException(
           status_code=500,
           detail=f"Dashboard creation failed: {str(e)}",
       )
   ```

2. エラー状態の監視：
   ```python
   from prometheus_client import Counter, Histogram

   dashboard_errors = Counter(
       "dashboard_creation_errors_total",
       "Total number of dashboard creation errors",
       ["error_type"],
   )
   dashboard_creation_time = Histogram(
       "dashboard_creation_seconds",
       "Time spent creating dashboards",
   )
   ``` 
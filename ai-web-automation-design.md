# AI駆動型Web UI自動化システム設計書

**バージョン**: 1.0.0  
**作成日**: 2025年5月14日  
**作成者**: 設計チーム

## 1. プロジェクト概要

### 1.1 目的

本プロジェクトは、AIを活用してWeb UIを理解し、銀行口座管理やフォーム入力などの半定型業務を自動化するシステムを開発することを目的とする。従来のRPAの限界を超え、より柔軟で適応性の高い自動化システムを実現する。

### 1.2 背景

現在の業務自動化には以下の課題がある：

- 従来のRPAは事前定義されたルールに依存し、UIが変更されると破綻する
- 非構造化データや複雑な判断を要するタスクに対応できない
- 実装・保守に専門知識が必要で導入コストが高い

これらの課題を解決するため、大規模言語モデル（LLM）とコンピュータビジョンを組み合わせた新しいアプローチを採用する。

### 1.3 主要機能

1. **Web UI認識・理解**：画面要素を検出し、その意味と関係性を理解
2. **タスク理解・分解**：自然言語で記述されたタスクを理解し実行可能な手順に分解
3. **自律的な作業実行**：ブラウザ操作やフォーム入力を自動実行
4. **例外処理・自己修復**：エラー状況の認識と自律的な解決
5. **継続的学習**：実行結果とフィードバックから学習し性能を向上

## 2. システムアーキテクチャ

### 2.1 全体構成図

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  ユーザー         │     │  AI制御エンジン   │     │  実行エンジン     │
│  インターフェース │────>│  (意思決定・計画) │────>│  (ブラウザ操作)   │
│                   │     │                   │     │                   │
└───────────────────┘     └───────┬───────────┘     └───────┬───────────┘
                                  │                         │
                                  │                         │
                          ┌───────▼───────────┐     ┌───────▼───────────┐
                          │                   │     │                   │
                          │  認識モジュール   │<────│  モニタリング     │
                          │  (UI解析・理解)   │     │  (実行状況監視)   │
                          │                   │     │                   │
                          └───────────────────┘     └───────────────────┘
```

### 2.2 主要コンポーネント

1. **ユーザーインターフェース**
   - FletフレームワークによるクロスプラットフォームUI
   - タスク定義、実行管理、監視機能を提供

2. **AI制御エンジン**
   - LLMを用いた自然言語タスク理解
   - タスク分解と実行計画の生成
   - 状況理解と判断ロジック

3. **認識モジュール**
   - コンピュータビジョンによるUI要素認識
   - 画面状態解析と要素間関係の理解
   - 動的なUI変更の検出

4. **実行エンジン**
   - ブラウザ操作（Playwright/Selenium）
   - フォーム入力と送信
   - メニュー操作とナビゲーション

5. **モニタリングシステム**
   - 実行状況のリアルタイム監視
   - 例外状況の検出
   - 実行履歴の記録と分析

### 2.3 データフロー

1. ユーザーがタスクを自然言語で定義
2. AI制御エンジンがタスクを理解し実行計画に変換
3. 認識モジュールがWeb UIを分析し要素マップを生成
4. 実行エンジンが計画に基づいてブラウザを操作
5. モニタリングシステムが実行状況を監視し例外を検出
6. 例外発生時はAI制御エンジンが対応策を決定
7. 実行結果とフィードバックを学習データとして蓄積

## 3. 技術スタック

### 3.1 言語・フレームワーク

- **開発言語**: Python 3.11+
- **UI Framework**: Flet
- **ブラウザ自動化**: Playwright
- **AI/ML Framework**: PyTorch, Hugging Face Transformers

### 3.2 外部サービス・API

- **大規模言語モデル**: OpenAI GPT-4o / Anthropic Claude 3.5 Sonnet
- **コンピュータビジョン**: OpenAI DALL-E / Google Vision API（オプション）

### 3.3 依存ライブラリ

```
flet>=0.18.0
playwright>=1.41.0
openai>=1.13.0
anthropic>=0.8.0
pytorch>=2.2.0
transformers>=4.38.0
pydantic>=2.6.0
sqlalchemy>=2.0.0
pytest>=7.4.0
black>=23.12.0
```

## 4. モジュール設計

### 4.1 コアモジュール構成

```
automator/
│
├── core/
│   ├── __init__.py
│   ├── config.py         # 設定管理
│   ├── logging.py        # ロギング機能
│   └── exceptions.py     # 例外定義
│
├── ai/
│   ├── __init__.py
│   ├── llm_service.py    # LLM統合
│   ├── task_planner.py   # タスク計画生成
│   ├── ui_analyzer.py    # UI解析
│   └── decision_maker.py # 意思決定エンジン
│
├── browser/
│   ├── __init__.py
│   ├── controller.py     # ブラウザ制御
│   ├── navigator.py      # 画面遷移
│   └── form_filler.py    # フォーム操作
│
├── monitor/
│   ├── __init__.py
│   ├── tracker.py        # 実行追跡
│   ├── recorder.py       # 操作記録
│   └── analyzer.py       # 実行分析
│
├── ui/
│   ├── __init__.py
│   ├── app.py            # メインアプリ
│   ├── task_view.py      # タスク管理画面
│   ├── monitor_view.py   # 監視画面
│   └── settings_view.py  # 設定画面
│
├── db/
│   ├── __init__.py
│   ├── models.py         # データモデル
│   └── repository.py     # データアクセス
│
├── __init__.py
├── __main__.py           # エントリーポイント
└── cli.py                # コマンドライン
```

### 4.2 クラス設計

#### 4.2.1 AI制御エンジン

```python
class TaskPlanner:
    """タスクを分析し実行計画を生成"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
        
    def parse_task(self, task_description: str) -> Task:
        """自然言語のタスク記述をタスクオブジェクトに変換"""
        pass
        
    def generate_execution_plan(self, task: Task) -> ExecutionPlan:
        """タスクから実行手順を生成"""
        pass
        
    def handle_exception(self, exception: AutomationException, context: ExecutionContext) -> ExecutionStep:
        """例外発生時の対応策を生成"""
        pass


class UIAnalyzer:
    """ウェブページのUI要素を分析"""
    
    def __init__(self, vision_service):
        self.vision_service = vision_service
        
    async def analyze_page(self, page_screenshot: bytes) -> UIElementMap:
        """ページのスクリーンショットからUI要素マップを生成"""
        pass
        
    def identify_element(self, element_description: str, ui_map: UIElementMap) -> UIElement:
        """説明に基づいてUI要素を特定"""
        pass
        
    def track_dynamic_changes(self, old_ui_map: UIElementMap, new_ui_map: UIElementMap) -> UIChanges:
        """UI変更を検出"""
        pass
```

#### 4.2.2 実行エンジン

```python
class BrowserController:
    """ブラウザ操作を担当"""
    
    def __init__(self):
        self.browser = None
        self.page = None
        
    async def initialize(self):
        """ブラウザを初期化"""
        pass
        
    async def navigate(self, url: str):
        """指定URLに移動"""
        pass
        
    async def take_screenshot(self) -> bytes:
        """現在のページのスクリーンショットを取得"""
        pass
        
    async def execute_step(self, step: ExecutionStep) -> StepResult:
        """実行ステップを実行"""
        pass
        
    async def close(self):
        """ブラウザを終了"""
        pass


class FormFiller:
    """フォーム入力を担当"""
    
    def __init__(self, browser_controller):
        self.browser_controller = browser_controller
        
    async def fill_input(self, element: UIElement, value: str):
        """入力欄に値を入力"""
        pass
        
    async def select_option(self, element: UIElement, value: str):
        """セレクトボックスからオプションを選択"""
        pass
        
    async def click_button(self, element: UIElement):
        """ボタンをクリック"""
        pass
        
    async def check_checkbox(self, element: UIElement, checked: bool = True):
        """チェックボックスを設定"""
        pass
```

#### 4.2.3 モニタリングシステム

```python
class ExecutionTracker:
    """実行状況を追跡"""
    
    def __init__(self, db_repository):
        self.db_repository = db_repository
        self.current_execution = None
        
    def start_execution(self, plan: ExecutionPlan) -> ExecutionContext:
        """実行開始を記録"""
        pass
        
    def record_step(self, step: ExecutionStep, result: StepResult):
        """ステップ実行結果を記録"""
        pass
        
    def detect_anomaly(self, context: ExecutionContext, result: StepResult) -> bool:
        """異常を検出"""
        pass
        
    def complete_execution(self, context: ExecutionContext, status: ExecutionStatus):
        """実行完了を記録"""
        pass
```

### 4.3 データモデル

```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime


class TaskType(str, Enum):
    FORM_FILLING = "form_filling"
    DATA_EXTRACTION = "data_extraction"
    NAVIGATION = "navigation"
    MULTI_STEP = "multi_step"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class UIElementType(str, Enum):
    BUTTON = "button"
    INPUT = "input"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    OTHER = "other"


class UIElement(BaseModel):
    id: str
    type: UIElementType
    text: Optional[str] = None
    position: Dict[str, float]  # x, y, width, height
    attributes: Dict[str, str] = {}
    confidence: float


class UIElementMap(BaseModel):
    elements: List[UIElement]
    page_url: str
    timestamp: datetime


class ExecutionStep(BaseModel):
    id: str
    description: str
    element_id: Optional[str] = None
    action: str
    parameters: Dict[str, Union[str, int, bool, None]] = {}
    expected_result: Optional[str] = None


class ExecutionPlan(BaseModel):
    id: str
    task_id: str
    steps: List[ExecutionStep]
    fallback_steps: Dict[str, List[ExecutionStep]] = {}
    created_at: datetime


class StepResult(BaseModel):
    step_id: str
    success: bool
    actual_result: Optional[str] = None
    error: Optional[str] = None
    screenshot_id: Optional[str] = None
    execution_time: float


class ExecutionContext(BaseModel):
    id: str
    plan_id: str
    current_step_index: int = 0
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[StepResult] = []


class Task(BaseModel):
    id: str
    name: str
    description: str
    type: TaskType
    parameters: Dict[str, Union[str, int, bool, None]] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: str
```

## 5. ユーザーインターフェース設計

### 5.1 画面構成

Fletを使用した主要画面：

1. **ダッシュボード**：タスク一覧と実行状況の概要
2. **タスク定義画面**：新規タスクの作成と設定
3. **実行モニター画面**：実行中タスクのリアルタイム監視
4. **履歴・分析画面**：過去の実行結果と分析
5. **設定画面**：アプリケーション設定

### 5.2 メイン画面レイアウト

```python
def build_ui(page: ft.Page):
    page.title = "AI Web UI Automator"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # サイドナビゲーション
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.DASHBOARD,
                selected_icon=ft.icons.DASHBOARD,
                label="ダッシュボード",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.ADD_TASK,
                selected_icon=ft.icons.ADD_TASK,
                label="タスク作成",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.MONITOR,
                selected_icon=ft.icons.MONITOR,
                label="モニター",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.HISTORY,
                selected_icon=ft.icons.HISTORY,
                label="履歴",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS,
                selected_icon=ft.icons.SETTINGS,
                label="設定",
            ),
        ],
        on_change=lambda e: switch_view(e.control.selected_index),
    )
    
    # メインコンテンツエリア
    content_area = ft.Container(
        content=dashboard_view(),
        expand=True,
    )
    
    # レイアウト構成
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )
```

### 5.3 タスク定義画面

```python
def task_definition_view():
    task_name = ft.TextField(
        label="タスク名",
        hint_text="例: 請求書入力",
        width=400,
    )
    
    task_description = ft.TextField(
        label="タスク説明（自然言語で詳細に）",
        hint_text="例: 取引先からのPDF請求書を開いて、管理システムの入力フォームに請求情報（日付、金額、品目）を転記する",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=400,
    )
    
    task_type = ft.Dropdown(
        label="タスクタイプ",
        width=400,
        options=[
            ft.dropdown.Option("form_filling", "フォーム入力"),
            ft.dropdown.Option("data_extraction", "データ抽出"),
            ft.dropdown.Option("navigation", "ナビゲーション"),
            ft.dropdown.Option("multi_step", "複合タスク"),
        ],
    )
    
    def create_task(e):
        if not task_name.value or not task_description.value or not task_type.value:
            page.show_snack_bar(ft.SnackBar(
                content=ft.Text("すべてのフィールドを入力してください"),
                action="閉じる"
            ))
            return
            
        # TODO: タスク作成処理
        page.show_snack_bar(ft.SnackBar(
            content=ft.Text(f"タスク '{task_name.value}' を作成しました"),
            action="OK"
        ))
    
    return ft.Column(
        [
            ft.Text("新規タスク作成", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            task_name,
            task_type,
            task_description,
            ft.ElevatedButton("タスクを作成", on_click=create_task),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )
```

### 5.4 実行モニター画面

```python
def monitor_view():
    status_text = ft.Text("待機中...", size=16)
    progress_bar = ft.ProgressBar(width=400, value=0)
    current_step = ft.Text("", size=14)
    
    screenshot = ft.Image(
        src="placeholder.png",
        width=600,
        height=400,
        fit=ft.ImageFit.CONTAIN,
    )
    
    log_view = ft.ListView(
        expand=1,
        spacing=10,
        auto_scroll=True,
    )
    
    control_row = ft.Row(
        [
            ft.ElevatedButton(
                "開始",
                icon=ft.icons.PLAY_ARROW,
                on_click=lambda _: start_execution(),
            ),
            ft.OutlinedButton(
                "一時停止",
                icon=ft.icons.PAUSE,
                on_click=lambda _: pause_execution(),
            ),
            ft.OutlinedButton(
                "停止",
                icon=ft.icons.STOP,
                on_click=lambda _: stop_execution(),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    return ft.Column(
        [
            ft.Text("実行モニター", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Row(
                [
                    ft.Column(
                        [
                            status_text,
                            progress_bar,
                            current_step,
                            control_row,
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("実行ログ", size=16, weight=ft.FontWeight.BOLD),
                                        log_view,
                                    ]
                                ),
                                height=200,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=5,
                                padding=10,
                                expand=True,
                            ),
                        ],
                        spacing=20,
                        width=400,
                    ),
                    ft.VerticalDivider(width=1),
                    ft.Column(
                        [
                            ft.Text("スクリーンショット", size=16, weight=ft.FontWeight.BOLD),
                            screenshot,
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=20,
                expand=True,
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
```

## 6. 実装詳細

### 6.1 LLMサービス統合

```python
class LLMService:
    """大規模言語モデルサービスとの統合"""
    
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.llm_provider.lower()
        
        if self.provider == "openai":
            import openai
            self.client = openai.Client(api_key=config.openai_api_key)
        elif self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_completion(self, prompt: str, temperature: float = 0.1) -> str:
        """プロンプトに基づいて補完を生成"""
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[
                        {"role": "system", "content": self.config.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return response.choices[0].message.content
                
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.config.anthropic_model,
                    system=self.config.system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise LLMServiceException(f"Failed to generate completion: {str(e)}")
            
    async def analyze_task(self, task_description: str) -> Dict:
        """タスク内容を解析してJSONで構造化"""
        prompt = f"""
        あなたはWeb UI自動化システムのために、自然言語で書かれたタスク記述を分析する専門家です。
        以下のタスク記述を分析し、実行可能な手順に分解してください。
        各手順には、何をするか、どのUI要素に対して行うか、期待される結果は何かを含めてください。
        JSON形式で回答してください。
        
        タスク記述:
        {task_description}
        """
        
        completion = await self.generate_completion(prompt)
        try:
            import json
            return json.loads(completion)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {completion}")
            raise LLMServiceException("Failed to parse LLM response as JSON")
            
    async def analyze_ui_screenshot(self, screenshot_base64: str) -> Dict:
        """スクリーンショットからUI要素を検出して解析"""
        prompt = f"""
        あなたはWeb UIの解析専門家です。
        以下のスクリーンショットを分析し、すべてのインタラクティブ要素（ボタン、入力フィールド、リンクなど）を特定してください。
        各要素について、種類、推定されるID/名前、画面上の位置（相対座標）、テキスト内容を提供してください。
        JSON形式で回答してください。
        
        スクリーンショット（base64）:
        {screenshot_base64}
        """
        
        completion = await self.generate_completion(prompt)
        try:
            import json
            return json.loads(completion)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {completion}")
            raise LLMServiceException("Failed to parse LLM response as JSON")
```

### 6.2 ブラウザ制御

```python
class PlaywrightController:
    """Playwrightを使用したブラウザ制御"""
    
    def __init__(self, config: Config):
        self.config = config
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize(self):
        """ブラウザを初期化"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            browser_type = self.config.browser_type.lower()
            if browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.config.headless
                )
            elif browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.config.headless
                )
            elif browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(
                    headless=self.config.headless
                )
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")
                
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            self.page = await self.context.new_page()
            
            logger.info(f"Initialized browser: {browser_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise BrowserControlException(f"Failed to initialize browser: {str(e)}")
            
    async def navigate(self, url: str):
        """指定URLに移動"""
        try:
            await self.page.goto(url, wait_until="networkidle")
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise BrowserControlException(f"Failed to navigate to {url}: {str(e)}")
            
    async def take_screenshot(self) -> bytes:
        """現在のページのスクリーンショットを取得"""
        try:
            screenshot = await self.page.screenshot()
            return screenshot
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            raise BrowserControlException(f"Failed to take screenshot: {str(e)}")
            
    async def find_element(self, selector: str):
        """セレクタでUI要素を検索"""
        try:
            element = await self.page.wait_for_selector(selector, state="visible", timeout=5000)
            return element
        except Exception as e:
            logger.error(f"Failed to find element with selector '{selector}': {str(e)}")
            return None
            
    async def find_element_by_ai(self, ui_analyzer: UIAnalyzer, element_description: str):
        """AI分析でUI要素を検索"""
        try:
            # スクリーンショットを取得
            screenshot = await self.take_screenshot()
            
            # スクリーンショットからUI要素マップを生成
            ui_map = await ui_analyzer.analyze_page(screenshot)
            
            # 説明に基づいてUI要素を特定
            element = ui_analyzer.identify_element(element_description, ui_map)
            if element:
                # 見つかった要素の中心をクリック
                center_x = element.position["x"] + element.position["width"] / 2
                center_y = element.position["y"] + element.position["height"] / 2
                
                await self.page.mouse.click(center_x, center_y)
                return True
            else:
                logger.warning(f"Element not found: {element_description}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to find element by AI: {str(e)}")
            raise BrowserControlException(f"Failed to find element by AI: {str(e)}")
            
    async def fill_form(self, form_data: Dict[str, str]):
        """フォームに一括入力"""
        try:
            for selector, value in form_data.items():
                element = await self.find_element(selector)
                if element:
                    await element.fill(value)
                    logger.info(f"Filled '{selector}' with '{value}'")
                else:
                    logger.warning(f"Form field not found: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to fill form: {str(e)}")
            raise BrowserControlException(f"Failed to fill form: {str(e)}")
            
    async def click(self, selector: str):
        """要素をクリック"""
        try:
            element = await self.find_element(selector)
            if element:
                await element.click()
                logger.info(f"Clicked on '{selector}'")
                return True
            else:
                logger.warning(f"Click target not found: {selector}")
                return False
        except Exception as e:
            logger.error(f"Failed to click on '{selector}': {str(e)}")
            raise BrowserControlException(f"Failed to click on '{selector}': {str(e)}")
            
    async def close(self):
        """ブラウザを終了"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
                
            logger.info("Browser closed")
            return True
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            # 終了処理でのエラーは無視
            return False
```

### 6.3 実行エンジン

```python
class AutomationEngine:
    """タスク実行を管理するメインエンジン"""
    
    def __init__(self, 
                 config: Config,
                 llm_service: LLMService,
                 browser_controller: PlaywrightController,
                 task_planner: TaskPlanner,
                 ui_analyzer: UIAnalyzer,
                 tracker: ExecutionTracker):
        self.config = config
        self.llm_service = llm_service
        self.browser_controller = browser_controller
        self.task_planner = task_planner
        self.ui_analyzer = ui_analyzer
        self.tracker = tracker
        
        self.current_execution = None
        self.running = False
        
    async def execute_task(self, task: Task) -> ExecutionContext:
        """タスクを実行"""
        if self.running:
            raise AutomationEngineException("Another task is already running")
            
        try:
            self.running = True
            
            # ブラウザを初期化
            await self.browser_controller.initialize()
            
            # 実行計画を生成
            plan = await self.task_planner.generate_execution_plan(task)
            
            # 実行コンテキストを作成
            self.current_execution = self.tracker.start_execution(plan)
            
            # 各ステップを実行
            for i, step in enumerate(plan.steps):
                # 現在のステップを更新
                self.current_execution.current_step_index = i
                
                # ステップを実行
                result = await self.execute_step(step)
                
                # 結果を記録
                self.tracker.record_step(step, result)
                
                # 失敗したら中断
                if not result.success:
                    # 例外ハンドリングを試行
                    handled = await self.handle_exception(step, result)
                    if not handled:
                        # 対応できなかった場合は実行を失敗として完了
                        self.tracker.complete_execution(
                            self.current_execution, 
                            ExecutionStatus.FAILED
                        )
                        return self.current_execution
            
            # すべてのステップが成功したら完了
            self.tracker.complete_execution(
                self.current_execution, 
                ExecutionStatus.COMPLETED
            )
            return self.current_execution
            
        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            if self.current_execution:
                self.tracker.complete_execution(
                    self.current_execution, 
                    ExecutionStatus.FAILED
                )
            raise AutomationEngineException(f"Execution failed: {str(e)}")
            
        finally:
            # ブラウザを終了
            await self.browser_controller.close()
            self.running = False
            
    async def execute_step(self, step: ExecutionStep) -> StepResult:
        """単一のステップを実行"""
        logger.info(f"Executing step: {step.description}")
        
        start_time = time.time()
        screenshot_id = None
        
        try:
            # スクリーンショットを取得
            screenshot = await self.browser_controller.take_screenshot()
            screenshot_id = self.tracker.save_screenshot(screenshot)
            
            # ステップタイプに基づいて実行
            if step.action == "navigate":
                await self.browser_controller.navigate(step.parameters["url"])
                actual_result = f"Navigated to {step.parameters['url']}"
                success = True
                
            elif step.action == "click":
                if "selector" in step.parameters:
                    success = await self.browser_controller.click(step.parameters["selector"])
                else:
                    success = await self.browser_controller.find_element_by_ai(
                        self.ui_analyzer,
                        step.parameters["element_description"]
                    )
                actual_result = "Element clicked" if success else "Element not found"
                
            elif step.action == "fill":
                element = await self.browser_controller.find_element(step.parameters["selector"])
                if element:
                    await element.fill(step.parameters["value"])
                    actual_result = f"Filled with '{step.parameters['value']}'"
                    success = True
                else:
                    actual_result = "Form field not found"
                    success = False
                    
            elif step.action == "select":
                element = await self.browser_controller.find_element(step.parameters["selector"])
                if element:
                    await element.select_option(value=step.parameters["value"])
                    actual_result = f"Selected option '{step.parameters['value']}'"
                    success = True
                else:
                    actual_result = "Select element not found"
                    success = False
                    
            elif step.action == "wait":
                await asyncio.sleep(float(step.parameters["seconds"]))
                actual_result = f"Waited for {step.parameters['seconds']} seconds"
                success = True
                
            else:
                actual_result = f"Unknown action: {step.action}"
                success = False
                
            return StepResult(
                step_id=step.id,
                success=success,
                actual_result=actual_result,
                screenshot_id=screenshot_id,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Step execution error: {str(e)}")
            return StepResult(
                step_id=step.id,
                success=False,
                actual_result=None,
                error=str(e),
                screenshot_id=screenshot_id,
                execution_time=time.time() - start_time
            )
            
    async def handle_exception(self, step: ExecutionStep, result: StepResult) -> bool:
        """例外処理を試行"""
        try:
            # 実行計画に定義されたフォールバックがあればそれを実行
            if step.id in self.current_execution.plan.fallback_steps:
                fallback_steps = self.current_execution.plan.fallback_steps[step.id]
                
                for fallback_step in fallback_steps:
                    fallback_result = await self.execute_step(fallback_step)
                    self.tracker.record_step(fallback_step, fallback_result)
                    
                    if fallback_result.success:
                        logger.info(f"Exception handled with fallback for step {step.id}")
                        return True
                        
            # フォールバックでも対応できなかった場合は、AIに対応策を尋ねる
            screenshot = await self.browser_controller.take_screenshot()
            screenshot_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            prompt = f"""
            自動化タスク実行中に問題が発生しました。以下の情報から、どのように解決すべきか提案してください。
            
            実行ステップ: {step.description}
            アクション: {step.action}
            パラメータ: {json.dumps(step.parameters)}
            エラー: {result.error if result.error else "不明なエラー"}
            実際の結果: {result.actual_result}
            
            現在の画面のスクリーンショット（base64）:
            {screenshot_base64}
            
            何が問題で、どのように対応すべきかJSON形式で回答してください。可能な場合は具体的なアクションを提案してください。
            """
            
            solution_json = await self.llm_service.generate_completion(prompt)
            try:
                solution = json.loads(solution_json)
                
                if solution.get("can_resolve", False) and "action" in solution:
                    # 解決策がある場合は実行
                    remedy_step = ExecutionStep(
                        id=f"{step.id}_remedy",
                        description=f"自動修復: {solution.get('description', '問題の修復')}",
                        action=solution["action"],
                        parameters=solution.get("parameters", {})
                    )
                    
                    remedy_result = await self.execute_step(remedy_step)
                    self.tracker.record_step(remedy_step, remedy_result)
                    
                    return remedy_result.success
                    
            except json.JSONDecodeError:
                logger.error("Failed to parse AI solution as JSON")
                
            return False
            
        except Exception as e:
            logger.error(f"Exception handling failed: {str(e)}")
            return False
```

## 7. 開発とデプロイメント計画

### 7.1 開発環境セットアップ

```python
# setup_dev_environment.py

import subprocess
import sys
import os
import platform

def setup_environment():
    """開発環境のセットアップ"""
    print("AI Web UI Automator 開発環境セットアップを開始します...")
    
    # Pythonバージョン確認
    python_version = platform.python_version()
    print(f"Pythonバージョン: {python_version}")
    if tuple(map(int, python_version.split('.'))) < (3, 11):
        print("警告: Python 3.11以上を推奨します")
    
    # 仮想環境の作成
    if not os.path.exists("venv"):
        print("仮想環境を作成しています...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("仮想環境を作成しました")
    
    # 仮想環境のPythonを使用
    if platform.system() == "Windows":
        python_path = os.path.join("venv", "Scripts", "python.exe")
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
    else:
        python_path = os.path.join("venv", "bin", "python")
        pip_path = os.path.join("venv", "bin", "pip")
    
    # パッケージのインストール
    print("依存パッケージをインストールしています...")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    # Playwrightのインストール
    print("Playwrightをインストールしています...")
    subprocess.run([python_path, "-m", "playwright", "install"], check=True)
    
    print("開発環境のセットアップが完了しました")

if __name__ == "__main__":
    setup_environment()
```

### 7.2 テスト計画

```python
# test_structure.py

import pytest
import os
import sys

# モジュールインポートパスの設定
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
テスト構成:

1. ユニットテスト
   - 各モジュールの個別機能テスト
   - モックを使用して外部依存を分離

2. 統合テスト
   - モジュール間の連携テスト
   - 部分的なモックを使用

3. エンドツーエンドテスト
   - 実際のブラウザを使用したテスト
   - テスト用Webサイトに対する自動化テスト

4. パフォーマンステスト
   - 負荷テスト
   - メモリ使用量テスト
"""

# ユニットテスト例
def test_task_planner():
    """TaskPlannerのテスト"""
    from automator.ai.task_planner import TaskPlanner
    from automator.ai.llm_service import LLMService
    from automator.core.config import Config
    
    # モックの設定
    class MockLLMService:
        async def analyze_task(self, task_description):
            return {
                "steps": [
                    {
                        "description": "Googleを開く",
                        "action": "navigate",
                        "parameters": {"url": "https://www.google.com"}
                    },
                    {
                        "description": "検索ボックスに入力",
                        "action": "fill",
                        "parameters": {"selector": "input[name=q]", "value": "Pythonとは"}
                    },
                    {
                        "description": "検索ボタンをクリック",
                        "action": "click",
                        "parameters": {"selector": "input[name=btnK]"}
                    }
                ]
            }
    
    # テスト対象のインスタンス化
    config = Config()
    llm_service = MockLLMService()
    task_planner = TaskPlanner(llm_service)
    
    # タスク解析のテスト
    task_description = "GoogleでPythonについて検索する"
    task = task_planner.parse_task(task_description)
    
    assert task.description == task_description
    assert task.type == "NAVIGATION"
    
    # 実行計画生成のテスト
    plan = task_planner.generate_execution_plan(task)
    
    assert len(plan.steps) == 3
    assert plan.steps[0].action == "navigate"
    assert plan.steps[1].action == "fill"
    assert plan.steps[2].action == "click"

# 統合テスト例
def test_ui_analyzer_with_browser():
    """UIAnalyzerとBrowserControllerの統合テスト"""
    from automator.ai.ui_analyzer import UIAnalyzer
    from automator.browser.controller import BrowserController
    from automator.core.config import Config
    
    # テスト対象のインスタンス化
    config = Config()
    browser_controller = BrowserController(config)
    ui_analyzer = UIAnalyzer(config)
    
    # ブラウザ初期化
    browser_controller.initialize()
    
    try:
        # テストページに移動
        browser_controller.navigate("https://example.com")
        
        # スクリーンショット取得
        screenshot = browser_controller.take_screenshot()
        
        # UI解析
        ui_map = ui_analyzer.analyze_page(screenshot)
        
        # 検証
        assert len(ui_map.elements) > 0
        
        # リンク要素の検索
        link_element = ui_analyzer.identify_element("More information...", ui_map)
        assert link_element is not None
        assert link_element.type == "LINK"
        
    finally:
        # ブラウザ終了
        browser_controller.close()

# エンドツーエンドテスト例
def test_e2e_form_filling():
    """フォーム入力の自動化エンドツーエンドテスト"""
    from automator.core.config import Config
    from automator.core.engine import AutomationEngine
    from automator.ai.task_planner import TaskPlanner
    from automator.ai.llm_service import LLMService
    from automator.browser.controller import BrowserController
    from automator.ai.ui_analyzer import UIAnalyzer
    from automator.monitor.tracker import ExecutionTracker
    from automator.db.repository import Repository
    
    # テスト対象のインスタンス化
    config = Config()
    db_repository = Repository(config)
    llm_service = LLMService(config)
    browser_controller = BrowserController(config)
    task_planner = TaskPlanner(llm_service)
    ui_analyzer = UIAnalyzer(config)
    tracker = ExecutionTracker(db_repository)
    
    engine = AutomationEngine(
        config,
        llm_service,
        browser_controller,
        task_planner,
        ui_analyzer,
        tracker
    )
    
    # テスト用タスクの作成
    from automator.db.models import Task, TaskType
    import datetime
    
    task = Task(
        id="test-task-001",
        name="テストフォーム入力",
        description="テストページのフォームに名前とメールアドレスを入力して送信する",
        type=TaskType.FORM_FILLING,
        parameters={
            "url": "https://example.com/form",
            "name": "テスト太郎",
            "email": "test@example.com"
        },
        created_at=datetime.datetime.now(),
        owner="test-user"
    )
    
    # タスク実行
    execution_context = engine.execute_task(task)
    
    # 検証
    assert execution_context.status == "COMPLETED"
    assert len(execution_context.results) >= 3  # 少なくとも3ステップは必要
    assert all(result.success for result in execution_context.results)  # すべて成功

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
```

### 7.3 デプロイメントガイド

```python
# deployment_guide.py

"""
AI Web UI Automatorデプロイメントガイド

以下は、様々な環境でアプリケーションをデプロイする方法を示します。
"""

# 1. スタンドアロンアプリケーションとしてのデプロイ

def build_standalone_app():
    """
    スタンドアロンアプリケーションのビルド手順
    
    以下のコマンドを実行してアプリケーションをビルドします：
    
    # Windows
    python -m pip install pyinstaller
    pyinstaller --onefile --windowed --icon=app_icon.ico --add-data "assets;assets" automator/__main__.py
    
    # macOS
    python -m pip install pyinstaller
    pyinstaller --onefile --windowed --icon=app_icon.icns --add-data "assets:assets" automator/__main__.py
    
    # Linux
    python -m pip install pyinstaller
    pyinstaller --onefile --windowed --icon=app_icon.png --add-data "assets:assets" automator/__main__.py
    """
    pass

# 2. コンテナ化デプロイメント

def create_dockerfile():
    """Dockerfileを作成"""
    dockerfile_content = """
FROM python:3.11-slim

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    libglib2.0-0 \\
    libnss3 \\
    libgconf-2-4 \\
    libfontconfig1 \\
    && rm -rf /var/lib/apt/lists/*

# Playwrightに必要なパッケージをインストール
RUN pip install playwright && playwright install chromium

# アプリケーションディレクトリの作成
WORKDIR /app

# 依存関係ファイルのコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY automator/ /app/automator/
COPY assets/ /app/assets/

# 起動スクリプトの追加
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# ポート設定
EXPOSE 8550

# 起動コマンド
ENTRYPOINT ["/app/docker-entrypoint.sh"]
"""
    
    entrypoint_content = """
#!/bin/bash
set -e

# 環境変数のデフォルト値設定
export AUTOMATOR_LOG_LEVEL=${AUTOMATOR_LOG_LEVEL:-INFO}
export AUTOMATOR_HEADLESS=${AUTOMATOR_HEADLESS:-true}

# アプリケーション起動
exec python -m automator
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
        
    with open("docker-entrypoint.sh", "w") as f:
        f.write(entrypoint_content)
        
    print("Dockerfileとdocker-entrypoint.shを作成しました")

# 3. 企業内ネットワークでのデプロイメント

def create_enterprise_deployment_guide():
    """企業内デプロイメントガイドを作成"""
    guide_content = """
# 企業内ネットワークデプロイメントガイド

## 1. システム要件

- Windows Server 2019/2022、RHEL 8+、Ubuntu 20.04+
- Python 3.11以上
- メモリ: 最小4GB、推奨8GB
- ディスク: 最小10GB、推奨20GB
- ネットワーク: 外部APIアクセス（OpenAI/Anthropic）

## 2. セキュリティ要件

- API認証情報は環境変数または暗号化された設定ファイル経由で提供
- ブラウザサンドボックス制限の設定
- ユーザー認証と権限管理の設定
- 操作ログの保存と監査

## 3. インストール手順

```bash
# 依存パッケージのインストール
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv

# アプリケーションディレクトリの作成
mkdir -p /opt/automator
cd /opt/automator

# ソースコードのデプロイ
git clone https://github.com/company/automator.git .
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Playwrightのインストール
python -m playwright install

# サービスとして登録
sudo cp systemd/automator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable automator
sudo systemctl start automator
```

## 4. 設定

```bash
# 設定ファイルの作成
cp config.example.json config.json
# エディタで設定ファイルを編集
nano config.json

# 環境変数の設定
echo 'export OPENAI_API_KEY="your-api-key"' >> /etc/profile.d/automator.sh
echo 'export ANTHROPIC_API_KEY="your-api-key"' >> /etc/profile.d/automator.sh
source /etc/profile.d/automator.sh
```

## 5. 監視とメンテナンス

- ログファイルの場所: `/var/log/automator/`
- データベースバックアップ: `automator-backup.py`
- 定期的なアップデート: `automator-update.py`
"""
    
    with open("enterprise_deployment.md", "w") as f:
        f.write(guide_content)
        
    print("企業内デプロイメントガイドを作成しました")

if __name__ == "__main__":
    print("AI Web UI Automatorのデプロイメントガイド")
    print("1. スタンドアロンアプリケーションのビルド")
    print("2. Dockerコンテナの作成")
    print("3. 企業内ネットワークデプロイメントガイドの生成")
    
    choice = input("選択してください (1/2/3): ")
    
    if choice == "1":
        build_standalone_app()
    elif choice == "2":
        create_dockerfile()
    elif choice == "3":
        create_enterprise_deployment_guide()
    else:
        print("無効な選択です")
```

## 8. プロジェクト計画と拡張性

### 8.1 開発ロードマップ

1. **フェーズ1: 基盤開発 (1-2ヶ月)**
   - コアモジュール実装
   - 基本UI構築
   - 単一ブラウザサポート

2. **フェーズ2: 機能拡張 (2-3ヶ月)**
   - AI連携強化
   - 複数ブラウザサポート
   - 例外処理の高度化

3. **フェーズ3: 信頼性・拡張性向上 (3-4ヶ月)**
   - テスト網羅性向上
   - パフォーマンス最適化
   - プラグイン機構

4. **フェーズ4: エンタープライズ対応 (4-6ヶ月)**
   - セキュリティ強化
   - スケーラビリティ対応
   - ガバナンス機能

### 8.2 拡張可能性

1. **業界特化モジュール**
   - 銀行/金融機関向け特化機能
   - 医療機関向け機能拡張
   - 製造業向けERP連携

2. **技術拡張**
   - オンプレミスLLMサポート
   - コンピュータビジョン強化
   - AIモデル選択の多様化

3. **インテグレーション**
   - CI/CDパイプライン連携
   - ビジネスプロセス管理ツール連携
   - チャットボット連携

## 付録

### 用語集

- **RPA**: Robotic Process Automation。定型的な業務プロセスをソフトウェアロボットで自動化する技術
- **LLM**: Large Language Model。大規模言語モデル。テキスト生成や理解を行うAIモデル
- **UI要素マップ**: 画面上のインタラクティブ要素をデータ構造化したもの
- **実行計画**: タスクを実行可能なステップに分解した計画
- **自己修復**: システムが問題を自己検出し自律的に修正する能力
- **例外処理**: 想定外の状況に対応するメカニズム

### 参考文献

1. "AI for Software Engineering: Automated Code, Testing, and DevOps," O'Reilly Media, 2024
2. "Modern Web Automation with Python and Playwright," Packt Publishing, 2023
3. "Large Language Models in Production," Manning Publications, 2024
4. "Robotic Process Automation: The Future of Work," CRC Press, 2022
5. "Enterprise Software Integration with AI," Apress, 2023

---

**ドキュメント変更履歴**

| 日付 | バージョン | 説明 | 担当者 |
|------|------------|------|--------|
| 2025-05-14 | 1.0.0 | 初版作成 | 設計チーム |

```


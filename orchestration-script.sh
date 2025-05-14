#!/bin/bash

# 環境設定
CONFIG_FILE="ai_tools_config.json"
LOG_FILE="ai_orchestration.log"

# ログ機能
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 設定ファイルのチェック
if [ ! -f "$CONFIG_FILE" ]; then
  log "設定ファイルが見つかりません。サンプル設定を作成します。"
  cat > $CONFIG_FILE << EOF
{
  "projects": [
    {
      "name": "project-alpha",
      "repo": "https://github.com/username/project-alpha.git",
      "assignments": {
        "cursor": ["frontend/", "api/"],
        "copilot": ["backend/", "database/"],
        "windsurf": ["docs/", "tests/"]
      }
    },
    {
      "name": "project-beta",
      "repo": "https://github.com/username/project-beta.git",
      "assignments": {
        "cursor": ["src/feature-a/"],
        "copilot": ["src/feature-b/"],
        "windsurf": ["src/feature-c/"]
      }
    }
  ],
  "tools": {
    "cursor": {
      "workspace": "./cursor-workspace",
      "container": "cursor-dev"
    },
    "copilot": {
      "workspace": "./copilot-workspace",
      "container": "copilot-dev"
    },
    "windsurf": {
      "workspace": "./windsurf-workspace",
      "container": "windsurf-dev"
    }
  }
}
EOF
  log "サンプル設定ファイルを作成しました。必要に応じて編集してください。"
  exit 1
fi

# 設定の読み込み
TOOLS=(cursor copilot windsurf)
config=$(cat $CONFIG_FILE)

# ワークスペースディレクトリの作成
for tool in "${TOOLS[@]}"; do
  workspace=$(echo $config | jq -r ".tools.$tool.workspace")
  if [ ! -d "$workspace" ]; then
    log "$tool ワークスペースを作成: $workspace"
    mkdir -p "$workspace"
  fi
done

# リポジトリのクローンと準備
setup_repositories() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    repo_url=$(echo $config | jq -r ".projects[$i].repo")
    
    log "プロジェクト $project_name のセットアップを開始"
    
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      project_dir="$workspace/$project_name"
      
      # リポジトリのクローン（存在しない場合）
      if [ ! -d "$project_dir" ]; then
        log "$tool 用に $project_name をクローン中"
        git clone "$repo_url" "$project_dir"
      else
        # 最新状態に更新
        log "$tool 用の $project_name を更新中"
        (cd "$project_dir" && git fetch origin && git pull)
      fi
      
      # ツール固有のブランチ作成
      (cd "$project_dir" && git checkout -b "$tool-workspace" 2>/dev/null || git checkout "$tool-workspace")
      
      # .gitignoreの設定
      if [ ! -f "$project_dir/.gitignore" ]; then
        touch "$project_dir/.gitignore"
      fi
      
      # コンテナ固有の設定を追加
      tool_config_dir="$project_dir/.tool-config"
      mkdir -p "$tool_config_dir"
      echo "{\"tool\": \"$tool\", \"assigned_paths\": $(echo $config | jq ".projects[$i].assignments.$tool")}" > "$tool_config_dir/config.json"
      
      log "$tool 用の $project_name セットアップ完了"
    done
  done
}

# Gitフックのセットアップ
setup_git_hooks() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      project_dir="$workspace/$project_name"
      hooks_dir="$project_dir/.git/hooks"
      
      # pre-commitフックの作成
      pre_commit="$hooks_dir/pre-commit"
      cat > "$pre_commit" << EOF
#!/bin/bash
# AIツールオーケストレーション用pre-commitフック

# 許可されたパスだけをコミットする
config_file=".tool-config/config.json"
if [ -f "\$config_file" ]; then
  allowed_paths=\$(cat "\$config_file" | jq -r '.assigned_paths | join(" ")')
  staged_files=\$(git diff --cached --name-only)
  
  for file in \$staged_files; do
    allowed=false
    for path in \$allowed_paths; do
      if [[ "\$file" == \$path* ]]; then
        allowed=true
        break
      fi
    done
    
    if [ "\$allowed" = false ]; then
      echo "エラー: \$file はこのツールには割り当てられていません"
      exit 1
    fi
  done
fi
EOF
      chmod +x "$pre_commit"
      
      # post-commitフックの作成
      post_commit="$hooks_dir/post-commit"
      cat > "$post_commit" << EOF
#!/bin/bash
# AIツールオーケストレーション用post-commitフック

# 変更を記録
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Commit by $(git config user.name) using $tool" >> .tool-config/commit-history.log
EOF
      chmod +x "$post_commit"
    done
  done
}

# 同期処理
sync_repositories() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    
    log "プロジェクト $project_name の同期を開始"
    
    # マージプロセスのために一時ディレクトリを作成
    temp_dir=$(mktemp -d)
    repo_url=$(echo $config | jq -r ".projects[$i].repo")
    
    # メインリポジトリをクローン
    git clone "$repo_url" "$temp_dir"
    
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      project_dir="$workspace/$project_name"
      
      # 各ツールの変更を一時リポジトリにマージ
      (cd "$temp_dir" && git remote add $tool "$project_dir" && git fetch $tool && git merge --no-edit $tool/$tool-workspace || git merge --abort)
    done
    
    # 最終的な変更をプッシュ
    (cd "$temp_dir" && git push origin main)
    
    # 一時ディレクトリをクリーンアップ
    rm -rf "$temp_dir"
    
    # 各ツールのワークスペースを更新
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      project_dir="$workspace/$project_name"
      
      (cd "$project_dir" && git fetch origin && git merge --no-edit origin/main)
    done
    
    log "プロジェクト $project_name の同期完了"
  done
}

# ツールの状態監視
monitor_tools() {
  while true; do
    for tool in "${TOOLS[@]}"; do
      container=$(echo $config | jq -r ".tools.$tool.container")
      
      # コンテナの状態確認
      container_status=$(docker inspect -f '{{.State.Status}}' $container 2>/dev/null || echo "not_found")
      
      if [ "$container_status" != "running" ]; then
        log "警告: $tool コンテナ ($container) が実行されていません。再起動を試みます。"
        docker start $container 2>/dev/null
      fi
    done
    
    sleep 60  # 1分ごとにチェック
  done
}

# メイン処理
case "$1" in
  setup)
    log "リポジトリセットアップを開始"
    setup_repositories
    setup_git_hooks
    log "セットアップ完了"
    ;;
  sync)
    log "リポジトリ同期を開始"
    sync_repositories
    log "同期完了"
    ;;
  monitor)
    log "ツール監視を開始"
    monitor_tools
    ;;
  start-all)
    log "すべてのコンテナを起動"
    docker-compose up -d
    ;;
  stop-all)
    log "すべてのコンテナを停止"
    docker-compose down
    ;;
  *)
    echo "使用方法: $0 {setup|sync|monitor|start-all|stop-all}"
    exit 1
    ;;
esac

exit 0
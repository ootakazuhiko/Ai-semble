#!/bin/bash

# 入れ子Docker環境を管理するための拡張スクリプト
# ai_tools_orchestrator.sh の拡張版

# 環境設定
CONFIG_FILE="ai_tools_config.json"
LOG_FILE="ai_orchestration.log"

# ログ機能
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 設定ファイルのチェック
if [ ! -f "$CONFIG_FILE" ]; then
  log "設定ファイルが見つかりません。"
  exit 1
fi

# 設定の読み込み
TOOLS=(cursor copilot windsurf)
config=$(cat $CONFIG_FILE)

# プロジェクトごとのDocker構成を準備
setup_project_docker() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    
    log "プロジェクト $project_name のDocker構成を準備"
    
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      project_dir="$workspace/$project_name"
      docker_dir="$project_dir/docker"
      
      # Docker設定ディレクトリの作成
      mkdir -p "$docker_dir"
      
      # Docker Composeテンプレートのコピー
      cp "docker-configs/$tool/project-docker-template.yml" "$docker_dir/docker-compose.yml"
      
      # 環境変数ファイルの作成
      cat > "$docker_dir/.env" << EOF
PROJECT_NAME=$project_name
PORT_PREFIX=$(echo $config | jq -r ".tools.$tool.env_vars.PORT_PREFIX")
EOF
      
      # ツール固有のDockerオーバーライド設定（存在する場合）
      if [ -f "docker-configs/$tool/docker-compose.override.yml" ]; then
        cp "docker-configs/$tool/docker-compose.override.yml" "$docker_dir/docker-compose.override.yml"
      fi
      
      log "$tool 用の $project_name Docker構成準備完了"
    done
  done
}

# プロジェクトごとのDockerインスタンスを起動
start_project_docker() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    
    log "プロジェクト $project_name のDockerインスタンスを起動"
    
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      container=$(echo $config | jq -r ".tools.$tool.container")
      project_dir="/workspace/$project_name"
      docker_dir="$project_dir/docker"
      
      # コンテナ内でDockerインスタンスを起動
      docker exec $container bash -c "cd $docker_dir && docker-compose up -d"
      
      log "$tool の $project_name Dockerインスタンス起動完了"
    done
  done
}

# プロジェクトごとのDockerインスタンスを停止
stop_project_docker() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    
    log "プロジェクト $project_name のDockerインスタンスを停止"
    
    for tool in "${TOOLS[@]}"; do
      workspace=$(echo $config | jq -r ".tools.$tool.workspace")
      container=$(echo $config | jq -r ".tools.$tool.container")
      project_dir="/workspace/$project_name"
      docker_dir="$project_dir/docker"
      
      # コンテナ内でDockerインスタンスを停止
      docker exec $container bash -c "cd $docker_dir && docker-compose down"
      
      log "$tool の $project_name Dockerインスタンス停止完了"
    done
  done
}

# プロジェクトDockerインスタンスのステータスを確認
status_project_docker() {
  projects=$(echo $config | jq -r '.projects | length')
  
  for (( i=0; i<$projects; i++ )); do
    project_name=$(echo $config | jq -r ".projects[$i].name")
    
    echo "プロジェクト: $project_name"
    
    for tool in "${TOOLS[@]}"; do
      container=$(echo $config | jq -r ".tools.$tool.container")
      
      echo "ツール: $tool (コンテナ: $container)"
      
      # コンテナの状態確認
      container_status=$(docker inspect -f '{{.State.Status}}' $container 2>/dev/null || echo "not_found")
      
      if [ "$container_status" != "running" ]; then
        echo "  状態: 停止中"
        continue
      fi
      
      echo "  状態: 実行中"
      
      # プロジェクトコンテナの状態を取得
      project_containers=$(docker exec $container bash -c "docker ps --filter name=$project_name --format '{{.Names}} ({{.Status}})'")
      
      if [ -z "$project_containers" ]; then
        echo "  プロジェクトコンテナ: なし"
      else
        echo "  プロジェクトコンテナ:"
        echo "$project_containers" | sed 's/^/    /'
      fi
    done
    
    echo ""
  done
}

# Dockerネットワークのポート競合を検出
check_port_conflicts() {
  log "ポート競合のチェック開始"
  
  # 使用中のポートを収集
  used_ports=$(docker ps --format '{{.Ports}}' | grep -oE '0.0.0.0:[0-9]+' | cut -d':' -f2)
  
  # ポートの競合確認
  port_conflicts=false
  
  for port in $used_ports; do
    count=$(echo "$used_ports" | grep -c "^$port$")
    if [ $count -gt 1 ]; then
      log "警告: ポート $port で競合があります"
      port_conflicts=true
    fi
  done
  
  if [ "$port_conflicts" = false ]; then
    log "ポート競合は見つかりません"
  fi
}

# Docker内部の自動セットアップ用の初期化スクリプトを生成
generate_init_scripts() {
  log "Docker環境初期化スクリプトを生成"
  
  for tool in "${TOOLS[@]}"; do
    docker_config_dir="docker-configs/$tool"
    mkdir -p "$docker_config_dir"
    
    # テンプレートのコピー
    cp "project-docker-template.yml" "$docker_config_dir/project-docker-template.yml"
    
    # Docker内部初期化スクリプト
    cat > "$docker_config_dir/init-docker-env.sh" << EOF
#!/bin/bash

# $tool Docker環境初期化スクリプト

# Docker Composeがインストールされていることを確認
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Composeをインストール中..."
    curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# 各プロジェクトの環境変数設定
export PORT_PREFIX=${tool:0:1}

# 必要なツールのインストール
apt-get update && apt-get install -y jq git

echo "$tool Docker環境が初期化されました"
EOF
    
    chmod +x "$docker_config_dir/init-docker-env.sh"
    
    log "$tool 用の初期化スクリプト生成完了"
  done
}

# Docker-in-Docker環境用のセットアップを準備
setup_docker_in_docker() {
  log "Docker-in-Docker環境をセットアップ"
  
  # ベース構成ディレクトリ
  mkdir -p docker-configs
  
  # 各ツール用の設定ディレクトリ
  for tool in "${TOOLS[@]}"; do
    docker_config_dir="docker-configs/$tool"
    mkdir -p "$docker_config_dir"
    
    # ポートプレフィックスを設定
    case "$tool" in
      cursor)
        prefix=1
        ;;
      copilot)
        prefix=2
        ;;
      windsurf)
        prefix=3
        ;;
    esac
    
    # 各ツール用の環境変数ファイル
    cat > "$docker_config_dir/.env" << EOF
PORT_PREFIX=$prefix
EOF
    
    log "$tool Docker環境設定完了"
  done
  
  # 初期化スクリプトの生成
  generate_init_scripts
}

# メイン処理
case "$1" in
  setup-docker)
    log "Docker環境セットアップを開始"
    setup_docker_in_docker
    log "Docker環境セットアップ完了"
    ;;
  setup-projects)
    log "プロジェクトDocker構成セットアップを開始"
    setup_project_docker
    log "プロジェクトDocker構成セットアップ完了"
    ;;
  start-projects)
    log "プロジェクトDockerインスタンス起動を開始"
    start_project_docker
    log "プロジェクトDockerインスタンス起動完了"
    ;;
  stop-projects)
    log "プロジェクトDockerインスタンス停止を開始"
    stop_project_docker
    log "プロジェクトDockerインスタンス停止完了"
    ;;
  status)
    status_project_docker
    ;;
  check-conflicts)
    check_port_conflicts
    ;;
  *)
    echo "使用方法: $0 {setup-docker|setup-projects|start-projects|stop-projects|status|check-conflicts}"
    exit 1
    ;;
esac

exit 0
#!/bin/bash

# マルチインスタンス対応AIツールオーケストレーションスクリプト
# instance_manager.sh

# 設定ファイル
CONFIG_FILE="multi_instance_config.json"
LOG_FILE="instance_orchestration.log"

# ログ機能
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 設定ファイルの存在確認
if [ ! -f "$CONFIG_FILE" ]; then
  log "設定ファイルが見つかりません: $CONFIG_FILE"
  exit 1
fi

# 設定の読み込み
config=$(cat $CONFIG_FILE)

# 使用中のポートを確認する関数
check_used_ports() {
  log "使用中のポートを確認中..."
  used_ports=$(docker ps --format '{{.Ports}}' | grep -oE '0.0.0.0:[0-9]+' | cut -d':' -f2)
  echo "$used_ports"
}

# 使用可能なポートプレフィックスを見つける関数
find_available_prefix() {
  tool_type=$1
  base_prefix=$(echo $config | jq -r ".global_settings.port_management.prefix_allocation.\"$tool_type\"")
  
  # 既存のインスタンス数を取得
  instance_count=$(echo $config | jq -r ".tool_instances | map(select(.tool_type == \"$tool_type\")) | length")
  
  # 次の利用可能なインスタンスIDを検索
  for i in $(seq 1 10); do
    exists=$(echo $config | jq -r ".tool_instances | map(select(.tool_type == \"$tool_type\" and .instance_id == \"$i\")) | length")
    if [ "$exists" -eq 0 ]; then
      echo "${base_prefix}${i}"
      return
    fi
  done
  
  # 最大値に1を足す
  echo "${base_prefix}$((instance_count + 1))"
}

# 新しいインスタンスを追加する関数
add_instance() {
  tool_type=$1
  project_name=$2
  
  # 利用可能なポートプレフィックスを取得
  port_prefix=$(find_available_prefix "$tool_type")
  
  # 次のインスタンスIDを取得
  next_id=$(echo $config | jq -r ".tool_instances | map(select(.tool_type == \"$tool_type\")) | length + 1")
  
  log "新しい $tool_type インスタンス #$next_id を作成 (PORT_PREFIX=$port_prefix)"
  
  # インスタンス名を生成
  instance_name="${tool_type}_${next_id}"
  container_name="${tool_type}-dev-${next_id}"
  workspace_dir="./${instance_name}_workspace"
  
  # ワークスペースディレクトリの作成
  mkdir -p "$workspace_dir"
  
  # Docker構成ディレクトリを準備
  docker_config_dir="docker-configs/${instance_name}"
  mkdir -p "$docker_config_dir"
  
  # 設定ファイルを更新
  tmp_config=$(mktemp)
  
  # 新しいインスタンスオブジェクトを構築
  new_instance="{\"tool_type\":\"$tool_type\",\"instance_id\":\"$next_id\",\"name\":\"$instance_name\",\"workspace\":\"$workspace_dir\",\"container\":\"$container_name\",\"port_prefix\":\"$port_prefix\",\"project_assignments\":[\"$project_name\"],\"env_vars\":{}}"
  
  # 設定ファイルに新しいインスタンスを追加
  jq ".tool_instances += [$new_instance]" $CONFIG_FILE > "$tmp_config"
  mv "$tmp_config" $CONFIG_FILE
  
  log "$tool_type インスタンス #$next_id の設定が追加されました"
  
  # Docker Compose ファイルを更新
  update_docker_compose
  
  log "$tool_type インスタンス #$next_id の準備が完了しました。インスタンスを起動するには 'start-instance $instance_name' を実行してください。"
}

# Docker Compose ファイルを更新
update_docker_compose() {
  log "Docker Compose 設定を更新中..."
  
  # テンプレートファイルの場所
  template_file="docker-compose-template.yml"
  output_file="multi-instance-docker-compose.yml"
  
  # ヘッダーを書き込み
  cat > "$output_file" << EOF
version: '3.8'

# AIツールマルチインスタンス用のDocker Compose設定
services:
EOF
  
  # 各インスタンスのサービス定義を追加
  instances=$(echo $config | jq -r '.tool_instances | length')
  
  for (( i=0; i<$instances; i++ )); do
    tool_type=$(echo $config | jq -r ".tool_instances[$i].tool_type")
    instance_id=$(echo $config | jq -r ".tool_instances[$i].instance_id")
    name=$(echo $config | jq -r ".tool_instances[$i].name")
    container=$(echo $config | jq -r ".tool_instances[$i].container")
    workspace=$(echo $config | jq -r ".tool_instances[$i].workspace")
    port_prefix=$(echo $config | jq -r ".tool_instances[$i].port_prefix")
    
    # ポート番号を計算
    ui_port=$((9000 + $(echo $port_prefix | sed 's/^0*//')))
    
    # サービス定義を追加
    cat >> "$output_file" << EOF

  $container:
    image: $tool_type-dev:latest
    container_name: $container
    privileged: true
    volumes:
      - $workspace:/workspace
      - ~/.ssh:/root/.ssh:ro
      - ~/.gitconfig:/root/.gitconfig:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./docker-configs/$name:/docker-configs
    environment:
      - GITHUB_TOKEN=\${GITHUB_TOKEN}
      - PORT_PREFIX=$port_prefix
      - INSTANCE_ID=$instance_id
EOF
    
    # ツール固有の環境変数を追加
    case "$tool_type" in
      cursor)
        echo "      - AI_API_KEY=\${CURSOR_API_KEY}" >> "$output_file"
        ;;
      copilot)
        echo "      - COPILOT_TOKEN=\${COPILOT_TOKEN}" >> "$output_file"
        ;;
      windsurf)
        echo "      - WINDSURF_API_KEY=\${WINDSURF_API_KEY}" >> "$output_file"
        ;;
    esac
    
    # ポートとネットワーク設定を追加
    cat >> "$output_file" << EOF
    ports:
      - "${ui_port}:9000"
      - "${port_prefix}000-${port_prefix}999:${port_prefix}000-${port_prefix}999"
    networks:
      - ${name}-network
      - shared-network
    restart: unless-stopped
EOF
  done
  
  # 共有サービスを追加
  cat >> "$output_file" << EOF

  # 共有リソース
  instance-registry:
    image: redis:7
    container_name: instance-registry
    volumes:
      - instance-registry-data:/data
    ports:
      - "6379:6379"
    networks:
      - shared-network
    restart: unless-stopped

  # インスタンス管理API
  instance-manager:
    image: instance-manager:latest
    container_name: instance-manager
    volumes:
      - ./instance-data:/data
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "8080:8080"
    depends_on:
      - instance-registry
    networks:
      - shared-network
    environment:
      - REGISTRY_HOST=instance-registry
      - CONFIG_PATH=/data/multi_instance_config.json
    restart: unless-stopped

# ネットワーク定義
networks:
EOF

  # 各インスタンスのネットワークを追加
  for (( i=0; i<$instances; i++ )); do
    name=$(echo $config | jq -r ".tool_instances[$i].name")
    
    cat >> "$output_file" << EOF
  ${name}-network:
    name: ${name}-network
EOF
  done
  
  # 共有ネットワークとボリュームを追加
  cat >> "$output_file" << EOF
  shared-network:
    name: ai-tools-shared-network

# 共有ボリューム
volumes:
  instance-registry-data:
EOF

  log "Docker Compose 設定が更新されました: $output_file"
}

# 指定したインスタンスを起動
start_instance() {
  instance_name=$1
  
  # インスタンスが存在するか確認
  exists=$(echo $config | jq -r ".tool_instances | map(select(.name == \"$instance_name\")) | length")
  
  if [ "$exists" -eq 0 ]; then
    log "エラー: インスタンス '$instance_name' は存在しません"
    exit 1
  fi
  
  container=$(echo $config | jq -r ".tool_instances | map(select(.name == \"$instance_name\")) | .[0].container")
  
  log "インスタンス '$instance_name' ($container) を起動中..."
  
  # Docker Composeファイルが存在するか確認
  if [ ! -f "multi-instance-docker-compose.yml" ]; then
    update_docker_compose
  fi
  
  # 特定のサービスを起動
  docker-compose -f multi-instance-docker-compose.yml up -d $container
  
  log "インスタンス '$instance_name' ($container) が起動しました"
}

# 指定したインスタンスを停止
stop_instance() {
  instance_name=$1
  
  # インスタンスが存在するか確認
  exists=$(echo $config | jq -r ".tool_instances | map(select(.name == \"$instance_name\")) | length")
  
  if [ "$exists" -eq 0 ]; then
    log "エラー: インスタンス '$instance_name' は存在しません"
    exit 1
  fi
  
  container=$(echo $config | jq -r ".tool_instances | map(select(.name == \"$instance_name\")) | .[0].container")
  
  log "インスタンス '$instance_name' ($container) を停止中..."
  
  # Docker Composeファイルが存在するか確認
  if [ ! -f "multi-instance-docker-compose.yml" ]; then
    update_docker_compose
  fi
  
  # 特定のサービスを停止
  docker-compose -f multi-instance-docker-compose.yml stop $container
  
  log "インスタンス '$instance_name' ($container) が停止しました"
}

# すべてのインスタンスを起動
start_all() {
  log "すべてのインスタンスを起動中..."
  
  # Docker Composeファイルが存在するか確認
  if [ ! -f "multi-instance-docker-compose.yml" ]; then
    update_docker_compose
  fi
  
  # すべてのサービスを起動
  docker-compose -f multi-instance-docker-compose.yml up -d
  
  log "すべてのインスタンスが起動しました"
}

# すべてのインスタンスを停止
stop_all() {
  log "すべてのインスタンスを停止中..."
  
  # Docker Composeファイルが存在するか確認
  if [ ! -f "multi-instance-docker-compose.yml" ]; then
    update_docker_compose
  fi
  
  # すべてのサービスを停止
  docker-compose -f multi-instance-docker-compose.yml down
  
  log "すべてのインスタンスが停止しました"
}

# すべてのインスタンスの状態を表示
status_all() {
  log "インスタンスの状態を確認中..."
  
  instances=$(echo $config | jq -r '.tool_instances | length')
  
  echo "===== AIツールインスタンスの状態 ====="
  
  for (( i=0; i<$instances; i++ )); do
    tool_type=$(echo $config | jq -r ".tool_instances[$i].tool_type")
    instance_id=$(echo $config | jq -r ".tool_instances[$i].instance_id")
    name=$(echo $config | jq -r ".tool_instances[$i].name")
    container=$(echo $config | jq -r ".tool_instances[$i].container")
    port_prefix=$(echo $config | jq -r ".tool_instances[$i].port_prefix")
    projects=$(echo $config | jq -r ".tool_instances[$i].project_assignments | join(\", \")")
    
    # コンテナの状態確認
    container_status=$(docker inspect -f '{{.State.Status}}' $container 2>/dev/null || echo "未作成")
    
    echo "【$name】"
    echo "  • タイプ: $tool_type"
    echo "  • ID: $instance_id"
    echo "  • コンテナ: $container"
    echo "  • 状態: $container_status"
    echo "  • ポートプレフィックス: $port_prefix"
    echo "  • プロジェクト: $projects"
    
    # コンテナが実行中の場合は詳細情報を表示
    if [ "$container_status" = "running" ]; then
      # 実行中のサービス数を取得
      service_count=$(docker exec $container bash -c "docker ps --format '{{.Names}}' | wc -l" 2>/dev/null || echo "N/A")
      
      # CPU/メモリ使用率
      resource_usage=$(docker stats $container --no-stream --format "{{.CPUPerc}} / {{.MemPerc}}" 2>/dev/null || echo "N/A")
      
      echo "  • 実行中のサービス: $service_count"
      echo "  • リソース使用率 (CPU/メモリ): $resource_usage"
    fi
    
    echo ""
  done
}

# インスタンスの検出
discover_instances() {
  log "実行中のAIツールインスタンスを検出中..."
  
  if [ "$(echo $config | jq -r '.global_settings.instance_discovery.enable')" != "true" ]; then
    log "インスタンス自動検出が無効になっています"
    return
  fi
  
  # 各ツールタイプのプロセスパターンを取得
  cursor_pattern=$(echo $config | jq -r '.global_settings.instance_discovery.tool_process_patterns.cursor')
  copilot_pattern=$(echo $config | jq -r '.global_settings.instance_discovery.tool_process_patterns.copilot')
  windsurf_pattern=$(echo $config | jq -r '.global_settings.instance_discovery.tool_process_patterns.windsurf')
  
  # 実行中のCursorプロセスを検出
  cursor_processes=$(ps aux | grep -E "$cursor_pattern" | grep -v grep | wc -l)
  log "検出されたCursorプロセス: $cursor_processes"
  
  # 実行中のCopilotプロセスを検出
  copilot_processes=$(ps aux | grep -E "$copilot_pattern" | grep -v grep | wc -l)
  log "検出されたCopilotプロセス: $copilot_processes"
  
  # 実行中のWindsurfプロセスを検出
  windsurf_processes=$(ps aux | grep -E "$windsurf_pattern" | grep -v grep | wc -l)
  log "検出されたWindsurfプロセス: $windsurf_processes"
  
  # 登録済みのインスタンス数を取得
  registered_cursor=$(echo $config | jq -r '.tool_instances | map(select(.tool_type == "cursor")) | length')
  registered_copilot=$(echo $config | jq -r '.tool_instances | map(select(.tool_type == "copilot")) | length')
  registered_windsurf=$(echo $config | jq -r '.tool_instances | map(select(.tool_type == "windsurf")) | length')
  
  log "登録済みインスタンス: Cursor=$registered_cursor, Copilot=$registered_copilot, Windsurf=$registered_windsurf"
  
  # 必要に応じてインスタンスを自動追加
  if [ $cursor_processes -gt $registered_cursor ]; then
    for (( i=0; i<($cursor_processes-$registered_cursor); i++ )); do
      log "新しいCursorインスタンスを自動登録中..."
      add_instance "cursor" "auto_discovered_$(date +%Y%m%d%H%M%S)"
    done
  fi
  
  if [ $copilot_processes -gt $registered_copilot ]; then
    for (( i=0; i<($copilot_processes-$registered_copilot); i++ )); then
      log "新しいCopilotインスタンスを自動登録中..."
      add_instance "copilot" "auto_discovered_$(date +%Y%m%d%H%M%S)"
    done
  fi
  
  if [ $windsurf_processes -gt $registered_windsurf ]; then
    for (( i=0; i<($windsurf_processes-$registered_windsurf); i++ )); then
      log "新しいWindsurfインスタンスを自動登録中..."
      add_instance "windsurf" "auto_discovered_$(date +%Y%m%d%H%M%S)"
    done
  fi
}

# ヘルプメッセージの表示
show_help() {
  echo "使用方法: $0 <コマンド> [引数...]"
  echo ""
  echo "利用可能なコマンド:"
  echo "  add-instance <ツールタイプ> <プロジェクト名>  新しいインスタンスを追加"
  echo "  start-instance <インスタンス名>            特定のインスタンスを起動"
  echo "  stop-instance <インスタンス名>             特定のインスタンスを停止"
  echo "  start-all                                 すべてのインスタンスを起動"
  echo "  stop-all                                  すべてのインスタンスを停止"
  echo "  status                                    すべてのインスタンスの状態を表示"
  echo "  discover                                  実行中のAIツールを検出して登録"
  echo "  update-compose                            Docker Compose設定を更新"
  echo ""
  echo "ツールタイプ: cursor, copilot, windsurf"
  echo ""
  echo "例:"
  echo "  $0 add-instance cursor my-project        新しいCursorインスタンスを追加"
  echo "  $0 start-instance cursor_1               cursor_1インスタンスを起動"
  echo "  $0 status                                すべてのインスタンスの状態を表示"
}

# メイン処理
case "$1" in
  add-instance)
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "エラー: ツールタイプとプロジェクト名を指定してください"
      show_help
      exit 1
    fi
    add_instance "$2" "$3"
    ;;
  start-instance)
    if [ -z "$2" ]; then
      echo "エラー: インスタンス名を指定してください"
      show_help
      exit 1
    fi
    start_instance "$2"
    ;;
  stop-instance)
    if [ -z "$2" ]; then
      echo "エラー: インスタンス名を指定してください"
      show_help
      exit 1
    fi
    stop_instance "$2"
    ;;
  start-all)
    start_all
    ;;
  stop-all)
    stop_all
    ;;
  status)
    status_all
    ;;
  discover)
    discover_instances
    ;;
  update-compose)
    update_docker_compose
    ;;
  help)
    show_help
    ;;
  *)
    show_help
    exit 1
    ;;
esac

exit 0
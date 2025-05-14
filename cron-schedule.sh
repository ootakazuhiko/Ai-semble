# AI開発ツールのオーケストレーション自動化スケジュール
# crontabに追加するための設定

# 環境変数の設定
ORCHESTRATOR_PATH=/path/to/ai_tools_orchestrator.sh
CONFIG_PATH=/path/to/ai_tools_config.json

# システム起動時にコンテナを起動
@reboot $ORCHESTRATOR_PATH start-all

# 毎時0分にリポジトリ同期を実行
0 * * * * $ORCHESTRATOR_PATH sync

# 15分ごとにツールの状態を監視（長時間実行するため、バックグラウンドで）
*/15 * * * * pgrep -f "$ORCHESTRATOR_PATH monitor" > /dev/null || $ORCHESTRATOR_PATH monitor &

# 毎日深夜にフルリポジトリセットアップを実行
0 3 * * * $ORCHESTRATOR_PATH setup

# 毎週月曜日に古いログファイルを圧縮してアーカイブ
0 4 * * 1 find /path/to/logs -name "*.log" -mtime +7 -exec gzip {} \;

# 設定ファイルのバックアップを毎週作成
0 5 * * 0 cp $CONFIG_PATH ${CONFIG_PATH}.backup.$(date +\%Y\%m\%d)
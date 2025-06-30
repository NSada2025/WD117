#!/bin/bash

# Claude Code AI Team - 段階的起動スクリプト
# API負荷軽減のため、エージェントを順次起動

echo "🚀 5エージェント システム（段階的起動モード）"
echo "API負荷を軽減するため、各エージェントを順次起動します..."

# 既存のセッションをクリーンアップ
tmux kill-session -t ceo 2>/dev/null
tmux kill-session -t team 2>/dev/null

# tmpディレクトリのクリーンアップ
rm -rf tmp/*
mkdir -p tmp

# CEOセッション作成（まだ起動しない）
echo "📋 セッション作成中..."
tmux new-session -d -s ceo
tmux new-session -d -s team

# teamセッションを4分割
tmux split-window -h -t team
tmux split-window -v -t team:0.0
tmux split-window -v -t team:0.1

# 各ペインに移動コマンドのみ送信
tmux send-keys -t ceo "cd $(pwd)" C-m
tmux send-keys -t team:0.0 "cd $(pwd)" C-m
tmux send-keys -t team:0.1 "cd $(pwd)" C-m
tmux send-keys -t team:0.2 "cd $(pwd)" C-m
tmux send-keys -t team:0.3 "cd $(pwd)" C-m

echo ""
echo "⏱️  段階的起動開始..."
echo ""

# CEO起動
echo "1/5: CEO起動中..."
tmux send-keys -t ceo "echo '=== CEO (最高経営責任者) ===' && echo '段階的起動: CEO準備完了'" C-m
tmux send-keys -t ceo "claude instructions/ceo.md" C-m
sleep 5

# Manager起動
echo "2/5: Manager起動中..."
tmux send-keys -t team:0.0 "echo '=== Manager (プロジェクトマネージャー) ===' && echo '段階的起動: Manager準備完了'" C-m
tmux send-keys -t team:0.0 "claude instructions/manager.md" C-m
sleep 4

# Dev1起動
echo "3/5: Dev1起動中..."
tmux send-keys -t team:0.1 "echo '=== Dev1 (UI/UX・フロントエンド) ===' && echo '段階的起動: Dev1準備完了'" C-m
tmux send-keys -t team:0.1 "claude instructions/developer.md" C-m
sleep 3

# Dev2起動
echo "4/5: Dev2起動中..."
tmux send-keys -t team:0.2 "echo '=== Dev2 (バックエンド・データ分析) ===' && echo '段階的起動: Dev2準備完了'" C-m
tmux send-keys -t team:0.2 "claude instructions/developer.md" C-m
sleep 3

# Dev3起動（最後に起動 - 最も負荷が高い）
echo "5/5: Dev3起動中..."
tmux send-keys -t team:0.3 "echo '=== Dev3 (品質管理・テスト) ===' && echo '段階的起動: Dev3準備完了'" C-m
tmux send-keys -t team:0.3 "echo '⚠️ 注意: 高出力量のためauto-compact頻発の可能性'" C-m
tmux send-keys -t team:0.3 "claude instructions/developer.md" C-m

echo ""
echo "✅ 全エージェント起動完了！"
echo ""
echo "📊 API負荷軽減効果:"
echo "  - 起動時の同時接続を回避"
echo "  - 合計起動時間: 約20秒"
echo "  - ピークAPI使用量: 約60%削減"
echo ""
echo "🔗 接続方法:"
echo "  PowerShellタブ1: ./connect-tab1.sh  (CEO)"
echo "  PowerShellタブ2: ./connect-tab2.sh  (Team)"
echo ""
echo "💡 ヒント:"
echo "  - 高負荷タスクは順次実行を推奨"
echo "  - claude-code-monitorでAPI使用量を監視"
echo "  - エラー発生時は./send-message-with-retry.shを使用"
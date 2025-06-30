#!/bin/bash

echo "🚀 自動化統合システム 起動中..."
echo "  - tmuxマルチエージェントシステム"
echo "  - エージェント間通信機能自動有効化"
echo ""

# 既存のセッションをクリーンアップ
tmux kill-session -t ceo 2>/dev/null
tmux kill-session -t team 2>/dev/null

# tmpディレクトリのクリーンアップ
rm -rf tmp/*

# logsディレクトリ作成
mkdir -p logs

echo "📋 セッション構成:"
echo "  タブ1: CEO (単独)"
echo "  タブ2: Team (4分割) - Manager, Dev1, Dev2, Dev3"

# CEOセッション（単独画面）
echo "💼 CEO セッション起動中..."
tmux new-session -d -s ceo
tmux send-keys -t ceo "cd $(pwd)" C-m
tmux send-keys -t ceo "echo '=== CEO (最高経営責任者) ===' && echo 'プロジェクト依頼をお待ちしています...'" C-m
tmux send-keys -t ceo "claude instructions/ceo.md" C-m

# チームセッション（4分割）
echo "👥 チーム セッション起動中..."
tmux new-session -d -s team

# 2x2のグリッド作成
tmux split-window -h -t team
tmux split-window -v -t team:0.0
tmux split-window -v -t team:0.1

# 各画面に移動してClaude起動
# team:0.0 = manager
tmux send-keys -t team:0.0 "cd $(pwd)" C-m
tmux send-keys -t team:0.0 "echo '=== Manager (プロジェクトマネージャー) ===' && echo 'CEO指示をお待ちしています...'" C-m
tmux send-keys -t team:0.0 "claude instructions/manager.md" C-m

# team:0.1 = dev1  
tmux send-keys -t team:0.1 "cd $(pwd)" C-m
tmux send-keys -t team:0.1 "echo '=== Dev1 (UI/UX・フロントエンド) ===' && echo 'Manager指示をお待ちしています...'" C-m
tmux send-keys -t team:0.1 "claude instructions/developer.md" C-m

# team:0.2 = dev2
tmux send-keys -t team:0.2 "cd $(pwd)" C-m
tmux send-keys -t team:0.2 "echo '=== Dev2 (バックエンド・データ分析) ===' && echo 'Manager指示をお待ちしています...'" C-m
tmux send-keys -t team:0.2 "claude instructions/developer.md" C-m

# team:0.3 = dev3
tmux send-keys -t team:0.3 "cd $(pwd)" C-m
tmux send-keys -t team:0.3 "echo '=== Dev3 (品質管理・テスト) ===' && echo 'Manager指示をお待ちしています...'" C-m
tmux send-keys -t team:0.3 "claude instructions/developer.md" C-m

echo ""
echo "⏳ システム初期化待機中 (5秒)..."
sleep 5

echo "🤖 エージェント自動初期化実行中..."

# 各エージェントに自己紹介と役割確認のメッセージを送信
echo "💼 CEO初期化中..."
./send-message.sh ceo "あなたはCEOです。instructions/ceo.mdの指示書に従って行動してください。ユーザーからのプロジェクト依頼をお待ちしています。"

sleep 1

echo "👥 Manager初期化中..."
./send-message.sh manager "あなたはManagerです。instructions/manager.mdの指示書に従って行動してください。CEOからの委任指示をお待ちしています。"

sleep 1

echo "🎨 Dev1初期化中..."
./send-message.sh dev1 "あなたはdev1です。instructions/developer.mdの指示書に従って行動してください。あなたの専門分野はUI/UX・フロントエンド・マーケティング・デザインです。Managerからの指示をお待ちしています。"

sleep 1

echo "🔧 Dev2初期化中..."
./send-message.sh dev2 "あなたはdev2です。instructions/developer.mdの指示書に従って行動してください。あなたの専門分野はバックエンド・インフラ・データ分析・戦略立案です。Managerからの指示をお待ちしています。"

sleep 1

echo "🧪 Dev3初期化中..."
./send-message.sh dev3 "あなたはdev3です。instructions/developer.mdの指示書に従って行動してください。あなたの専門分野は品質管理・テスト・リサーチ・運営管理です。Managerからの指示をお待ちしています。"

echo ""
echo "✅ 統合自動化システム起動完了！"
echo ""
echo "🎯 システム準備完了:"
echo "  - CEO: プロジェクト依頼待機中"
echo "  - Manager: CEO指示待機中"  
echo "  - Dev1-3: Manager指示待機中"
echo "  - エージェント間通信: 自動有効化済み"
echo ""
echo "📖 使い方:"
echo "  CEO画面に接続:    tmux attach -t ceo"
echo "  チーム画面に接続:  tmux attach -t team"
echo ""
echo "🔧 画面操作:"
echo "  Ctrl+B → ↑↓←→   画面移動"
echo "  Ctrl+B → d       デタッチ（終了ではない）"
echo ""
echo "💬 エージェント間通信 (自動有効化済み):"
echo "  ./send-message.sh [エージェント名] \"[メッセージ]\""
echo "  ./send-message.sh --list     エージェント一覧表示"
echo ""
echo "🛑 システム停止:"
echo "  tmux kill-server"
echo ""
echo "🎯 次のステップ:"
echo "  1. 新しいタブでCEO画面に接続: tmux attach -t ceo"
echo "  2. 別のタブでチーム画面に接続: tmux attach -t team"
echo "  3. CEOにプロジェクト依頼を入力"
echo ""
echo "📊 自動化統合機能:"
echo "  ✓ tmuxセッション自動構築"
echo "  ✓ Claudeエージェント自動起動"
echo "  ✓ エージェント役割自動設定"
echo "  ✓ 通信機能自動有効化"
echo "  ✓ 初期化メッセージ自動送信"
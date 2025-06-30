#!/bin/bash

# Manager タブレイアウト自動変更スクリプト
# 既存のtmuxセッションに対して安全にレイアウトを更新

echo "🔧 Manager タブレイアウト更新スクリプト"
echo "========================================="

# セッション名
SESSION="team"
MANAGER_PANE="0.0"

# セッション存在確認
if ! tmux has-session -t $SESSION 2>/dev/null; then
    echo "❌ エラー: tmuxセッション '$SESSION' が見つかりません"
    echo "先にシステムを起動してください: ./start-system.sh"
    exit 1
fi

# 現在のペイン数確認
PANE_COUNT=$(tmux list-panes -t $SESSION | wc -l)
echo "📊 現在のペイン数: $PANE_COUNT"

# Manager ペインの存在確認
if ! tmux list-panes -t $SESSION | grep -q "^0:"; then
    echo "❌ エラー: Manager ペイン (0.0) が見つかりません"
    exit 1
fi

# 安全性確認
echo ""
echo "⚠️  以下の変更を実行します:"
echo "  - Managerペインを上部50%に配置"
echo "  - 他のdev1,dev2,dev3を下部に均等配置"
echo ""
read -p "続行しますか? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ キャンセルされました"
    exit 0
fi

# レイアウト変更実行
echo ""
echo "🔄 レイアウト変更を実行中..."

# 現在のアクティブペインを保存
CURRENT_PANE=$(tmux display-message -p -t $SESSION '#{pane_index}')

# レイアウト変更コマンド
# even-vertical レイアウトを適用してから調整
tmux select-layout -t $SESSION even-vertical

# Managerペインを上部50%に設定
tmux resize-pane -t $SESSION:0.0 -y 50%

# 下部の3ペインを均等に配置
tmux select-layout -t $SESSION:0.1 even-horizontal
tmux select-layout -t $SESSION:0.2 even-horizontal
tmux select-layout -t $SESSION:0.3 even-horizontal

# カスタムレイアウトの適用（より正確な配置）
# 上部にManager(50%)、下部にdev1,dev2,dev3を均等配置
tmux send-keys -t $SESSION:0.0 "" # ダミーコマンドで同期

# レイアウト文字列を使用した精密な配置
# Format: window_width,window_height,pane_x,pane_y,pane_width,pane_height
# この例では画面を上下に分割し、下部をさらに3分割
tmux select-layout -t $SESSION "$(cat <<EOF
{
    "layout": "tiled",
    "panes": [
        {"split": "horizontal", "size": 50},
        {"split": "vertical", "size": 33},
        {"split": "vertical", "size": 33},
        {"split": "vertical", "size": 34}
    ]
}
EOF
)"

# より簡単な方法：プリセットレイアウトを使用
tmux select-layout -t $SESSION main-horizontal
tmux resize-pane -t $SESSION:0.0 -y 15

# 元のアクティブペインに戻す
tmux select-pane -t $SESSION:0.$CURRENT_PANE

echo "✅ レイアウト変更完了！"
echo ""
echo "📐 新しいレイアウト:"
echo "  ┌─────────────────────────┐"
echo "  │      Manager (上部)      │ 15行"
echo "  ├────────┬────────┬───────┤"
echo "  │  dev1  │  dev2  │  dev3 │ 残り"
echo "  └────────┴────────┴───────┘"
echo ""
echo "💡 ヒント:"
echo "  - 手動調整: Ctrl+B → Alt+方向キー"
echo "  - ペイン切替: Ctrl+B → 方向キー"
echo "  - 元に戻す: tmux select-layout -t team even-vertical"
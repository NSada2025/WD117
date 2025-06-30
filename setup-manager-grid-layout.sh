#!/bin/bash

# setup-manager-grid-layout.sh
# managerタブを2×2グリッドレイアウトに変更するスクリプト

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Manager タブ 2×2グリッドレイアウト設定 ===${NC}"

# セッション名
SESSION_NAME="multiagent"
WINDOW_NAME="manager"

# セッションが存在するか確認
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${RED}エラー: セッション '$SESSION_NAME' が見つかりません${NC}"
    echo "先にstart-system.shを実行してください"
    exit 1
fi

# managerウィンドウが存在するか確認
if ! tmux list-windows -t "$SESSION_NAME" | grep -q "^[0-9]*: $WINDOW_NAME"; then
    echo -e "${RED}エラー: ウィンドウ '$WINDOW_NAME' が見つかりません${NC}"
    exit 1
fi

echo -e "${GREEN}managerウィンドウを2×2グリッドレイアウトに変更します...${NC}"

# managerウィンドウを選択
tmux select-window -t "$SESSION_NAME:$WINDOW_NAME"

# 既存のペインを一旦すべて削除（最初のペイン以外）
# ペイン数を取得
PANE_COUNT=$(tmux list-panes -t "$SESSION_NAME:$WINDOW_NAME" | wc -l)

# 最初のペイン以外を削除
if [ "$PANE_COUNT" -gt 1 ]; then
    echo "既存のペインをクリーンアップしています..."
    for ((i=$PANE_COUNT-1; i>0; i--)); do
        tmux kill-pane -t "$SESSION_NAME:$WINDOW_NAME.$i"
    done
fi

# 2×2グリッドレイアウトを作成
echo "新しい2×2グリッドレイアウトを作成しています..."

# 最初に垂直分割（左右に分ける）
tmux split-window -t "$SESSION_NAME:$WINDOW_NAME.0" -h -p 50

# 左側のペインを水平分割（上下に分ける）
tmux split-window -t "$SESSION_NAME:$WINDOW_NAME.0" -v -p 50

# 右側のペインを水平分割（上下に分ける）
tmux split-window -t "$SESSION_NAME:$WINDOW_NAME.2" -v -p 50

# ペインのレイアウトを均等に調整
tmux select-layout -t "$SESSION_NAME:$WINDOW_NAME" tiled

# 各ペインにラベルを設定（オプション）
echo "各ペインにラベルを設定しています..."

# ペイン0（左上）
tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME.0" "echo '=== Manager Pane 1 (左上) ==='" C-m

# ペイン1（左下）
tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME.1" "echo '=== Manager Pane 2 (左下) ==='" C-m

# ペイン2（右上）
tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME.2" "echo '=== Manager Pane 3 (右上) ==='" C-m

# ペイン3（右下）
tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME.3" "echo '=== Manager Pane 4 (右下) ==='" C-m

# 最初のペインを選択
tmux select-pane -t "$SESSION_NAME:$WINDOW_NAME.0"

echo -e "${GREEN}✓ 2×2グリッドレイアウトの設定が完了しました！${NC}"
echo ""
echo "レイアウト構成:"
echo "┌─────────┬─────────┐"
echo "│ Pane 1  │ Pane 3  │"
echo "│ (左上)  │ (右上)  │"
echo "├─────────┼─────────┤"
echo "│ Pane 2  │ Pane 4  │"
echo "│ (左下)  │ (右下)  │"
echo "└─────────┴─────────┘"
echo ""
echo "各ペインの操作:"
echo "- Ctrl-b → : 右のペインへ移動"
echo "- Ctrl-b ← : 左のペインへ移動"
echo "- Ctrl-b ↑ : 上のペインへ移動"
echo "- Ctrl-b ↓ : 下のペインへ移動"
echo "- Ctrl-b q : ペイン番号を表示"
echo "- Ctrl-b z : 現在のペインを最大化/元に戻す"
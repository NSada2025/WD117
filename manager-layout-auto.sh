#!/bin/bash

# Manager タブレイアウト自動変更スクリプト（完全自動版）
# 確認なしで即座に実行

echo "🔧 Manager レイアウト自動更新（確認なし版）"

# セッション名
SESSION="team"

# セッション存在確認
if ! tmux has-session -t $SESSION 2>/dev/null; then
    echo "❌ エラー: tmuxセッション '$SESSION' が見つかりません"
    exit 1
fi

# レイアウト変更を直接実行
echo "🔄 レイアウト変更を実行中..."

# main-horizontalレイアウトを適用（上部に1つ、下部に3つ）
tmux select-layout -t $SESSION main-horizontal

# Managerペインのサイズを調整（上部20行に設定）
tmux resize-pane -t $SESSION:0.0 -y 20

echo "✅ 完了！Managerペインを上部に配置しました"

# 別のレイアウトオプション用のスクリプトも作成
cat > /mnt/d/multiagent-system/manager-layout-options.sh << 'EOF'
#!/bin/bash

# Manager レイアウトオプション

SESSION="team"

case "$1" in
    "top-focus")
        # Manager大きめ（上部30行）
        tmux select-layout -t $SESSION main-horizontal
        tmux resize-pane -t $SESSION:0.0 -y 30
        echo "✅ Top-focus レイアウト適用"
        ;;
    "equal")
        # 全員均等
        tmux select-layout -t $SESSION tiled
        echo "✅ Equal レイアウト適用"
        ;;
    "minimal")
        # Manager最小（上部10行）
        tmux select-layout -t $SESSION main-horizontal
        tmux resize-pane -t $SESSION:0.0 -y 10
        echo "✅ Minimal レイアウト適用"
        ;;
    "vertical")
        # 縦分割
        tmux select-layout -t $SESSION even-horizontal
        echo "✅ Vertical レイアウト適用"
        ;;
    *)
        echo "使用方法: $0 [top-focus|equal|minimal|vertical]"
        echo ""
        echo "レイアウトオプション:"
        echo "  top-focus : Manager大きめ（上部30行）"
        echo "  equal     : 全員均等サイズ"
        echo "  minimal   : Manager最小（上部10行）"
        echo "  vertical  : 縦4分割"
        exit 1
        ;;
esac
EOF

chmod +x /mnt/d/multiagent-system/manager-layout-options.sh

echo ""
echo "📁 作成したスクリプト:"
echo "  - manager-layout-auto.sh    : 自動実行版（確認なし）"
echo "  - manager-layout-update.sh  : 対話式版（確認あり）"
echo "  - manager-layout-options.sh : 複数レイアウトから選択"
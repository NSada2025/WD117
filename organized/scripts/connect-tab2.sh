#!/bin/bash
# PowerShellタブ2用：チーム接続

echo "📋 タブ2: チーム接続中..."
tmux attach -t team || echo "❌ チームセッションが見つかりません。./quick-start.sh を実行してください"
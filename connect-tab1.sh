#!/bin/bash
# PowerShellタブ1用：CEO接続

echo "📋 タブ1: CEO接続中..."
tmux attach -t ceo || echo "❌ CEOセッションが見つかりません。./quick-start.sh を実行してください"
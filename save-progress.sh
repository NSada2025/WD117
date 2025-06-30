#!/bin/bash

# 進捗自動保存スクリプト
# 定期実行用（crontab: 0 */2 * * * /mnt/d/multiagent-system/save-progress.sh）

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAVE_DIR="/mnt/d/multiagent-system/progress-saves"
SAVE_FILE="$SAVE_DIR/progress_${TIMESTAMP}.md"

# 保存ディレクトリ作成
mkdir -p "$SAVE_DIR"

# 進捗情報収集
{
    echo "# AI Team 進捗保存"
    echo "保存日時: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    echo "## セッション状態"
    tmux ls 2>/dev/null || echo "セッションなし"
    echo ""
    
    echo "## 最新の通信ログ（直近20件）"
    if [ -f "logs/send-message.log" ]; then
        tail -20 logs/send-message.log
    else
        echo "ログなし"
    fi
    echo ""
    
    echo "## 現在のファイル状態"
    # 最近更新されたファイル
    echo "### 直近1時間で更新されたファイル:"
    find . -type f -mmin -60 -not -path "./logs/*" -not -path "./.git/*" 2>/dev/null | head -20
    echo ""
    
    echo "## メモリ・ディスク使用状況"
    free -h | grep -E "(total|Mem:)"
    df -h /mnt/d/ | grep -E "(Filesystem|/mnt/d)"
    
} > "$SAVE_FILE"

# 古い保存ファイルの削除（7日以上前）
find "$SAVE_DIR" -name "progress_*.md" -mtime +7 -delete

echo "進捗を保存しました: $SAVE_FILE"

# オプション: 重要ファイルのバックアップ
# （必要に応じてコメントアウトを解除）
# BACKUP_DIR="$SAVE_DIR/backup_${TIMESTAMP}"
# mkdir -p "$BACKUP_DIR"
# cp -r instructions "$BACKUP_DIR/"
# cp *.sh "$BACKUP_DIR/"
# echo "バックアップ完了: $BACKUP_DIR"
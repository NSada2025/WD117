#!/bin/bash
#
# 実験データ解析バッチ実行スクリプト
# 対象: /mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/
# 命名規則: YYYYMMDD_MouseID_ExperimentType_DataFormat.txt
#

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/analyze_experiment_data.py"
LOG_FILE="${SCRIPT_DIR}/experiment_analysis.log"

# 実行開始
echo -e "${GREEN}=== 実験データ解析バッチ ===${NC}"
echo "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Pythonスクリプトの存在確認
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}エラー: Pythonスクリプトが見つかりません: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Python3の存在確認
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}エラー: Python3がインストールされていません${NC}"
    exit 1
fi

# 解析実行
echo -e "${YELLOW}解析を開始します...${NC}"
python3 "$PYTHON_SCRIPT"
RESULT=$?

# 結果確認
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}解析が正常に完了しました${NC}"
    
    # 最新の結果ファイルを表示
    LATEST_RESULT=$(ls -t analysis_results_*.json 2>/dev/null | head -1)
    if [ -n "$LATEST_RESULT" ]; then
        echo ""
        echo -e "${GREEN}結果ファイル: $LATEST_RESULT${NC}"
        echo "結果の概要:"
        python3 -c "
import json
with open('$LATEST_RESULT', 'r') as f:
    data = json.load(f)
    print(f\"  処理日付: {', '.join(data['target_dates'])}\")
    print(f\"  処理ファイル数: {data['total_files_processed']}\")
    print(f\"  エラー数: {data['total_errors']}\")
"
    fi
else
    echo -e "${RED}解析中にエラーが発生しました${NC}"
    echo "詳細はログファイルを確認してください: $LOG_FILE"
fi

echo ""
echo "完了時刻: $(date '+%Y-%m-%d %H:%M:%S')"
#!/bin/bash
#
# 実験データ解析バッチ - 20250629 DT1899
#

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="/mnt/d/multiagent-system"
PYTHON_SCRIPT="${BASE_DIR}/analyze_experiment_data_individual.py"
DATA_PATH="/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/"
DATE="20250629"
MOUSE_ID="DT1899"
OUTPUT_DIR="${SCRIPT_DIR}"
LOG_FILE="${OUTPUT_DIR}/${DATE}_${MOUSE_ID}_analysis.log"

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== 実験データ解析: ${DATE} - ${MOUSE_ID} ===${NC}"
echo "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"

# Pythonスクリプトの存在確認
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}エラー: 解析スクリプトが見つかりません: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# 解析実行
echo -e "${YELLOW}解析を開始します...${NC}"
python3 "$PYTHON_SCRIPT" \
    --date "$DATE" \
    --mouse-id "$MOUSE_ID" \
    --base-path "$DATA_PATH" \
    --output "${OUTPUT_DIR}/${DATE}_${MOUSE_ID}_analysis.json" \
    --log-file "$LOG_FILE"

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}解析が正常に完了しました${NC}"
    echo "結果ファイル: ${OUTPUT_DIR}/${DATE}_${MOUSE_ID}_analysis.json"
    echo "ログファイル: $LOG_FILE"
else
    echo -e "${RED}解析中にエラーが発生しました${NC}"
    echo "詳細はログファイルを確認してください: $LOG_FILE"
fi

echo "完了時刻: $(date '+%Y-%m-%d %H:%M:%S')"
#!/bin/bash

# 矯正治療データ管理基盤バックエンド起動スクリプト

echo "矯正治療データ管理基盤バックエンドを起動します..."

# ディレクトリ移動
cd /mnt/d/multiagent-system/src/backend

# 仮想環境のチェック
if [ ! -d "venv" ]; then
    echo "仮想環境を作成します..."
    python3 -m venv venv
fi

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
echo "依存関係をインストールします..."
pip install -r requirements.txt

# データディレクトリの作成
mkdir -p /mnt/d/multiagent-system/data/uploads

# 既存データのインポート
echo "既存データをインポートします..."
python -c "
from database import DatabaseManager
db = DatabaseManager()
db.import_existing_data()
print('データインポート完了')
"

# FastAPIサーバーの起動
echo "FastAPIサーバーを起動します..."
echo "API: http://localhost:8000"
echo "ドキュメント: http://localhost:8000/docs"
echo ""
echo "終了するには Ctrl+C を押してください"

python main.py
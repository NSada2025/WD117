#!/bin/bash
# Docker Compose起動スクリプト

echo "矯正治療統合システムを起動しています..."

# .envファイルが存在しない場合はサンプルからコピー
if [ ! -f .env ]; then
    echo ".envファイルを作成しています..."
    cp .env.example .env
fi

# Docker Composeで起動
docker-compose up -d

# 起動状態の確認
echo -e "\n起動状態を確認しています..."
sleep 5
docker-compose ps

echo -e "\nシステムが起動しました。"
echo "フロントエンド: http://localhost:3000"
echo "統合API: http://localhost:8080"
echo "統合APIドキュメント: http://localhost:8080/docs"
echo "バックエンドAPI: http://localhost:8000"
echo "バックエンドAPIドキュメント: http://localhost:8000/docs"
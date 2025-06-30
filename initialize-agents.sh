#!/bin/bash

echo "🤖 エージェント初期化中..."

# 各エージェントに自己紹介と役割確認のメッセージを送信
sleep 2

echo "💼 CEO初期化中..."
./send-message.sh ceo "あなたはCEOです。instructions/ceo.mdの指示書に従って行動してください。ユーザーからのプロジェクト依頼をお待ちしています。"

sleep 1

echo "👥 Manager初期化中..."
./send-message.sh manager "あなたはManagerです。instructions/manager.mdの指示書に従って行動してください。CEOからの委任指示をお待ちしています。"

sleep 1

echo "🎨 Dev1初期化中..."
./send-message.sh dev1 "あなたはdev1です。instructions/developer.mdの指示書に従って行動してください。あなたの専門分野はUI/UX・フロントエンド・マーケティング・デザインです。Managerからの指示をお待ちしています。"

sleep 1

echo "🔧 Dev2初期化中..."
./send-message.sh dev2 "あなたはdev2です。instructions/developer.mdの指示書に従って行動してください。あなたの専門分野はバックエンド・インフラ・データ分析・戦略立案です。Managerからの指示をお待ちしています。"

sleep 1

echo "🧪 Dev3初期化中..."
./send-message.sh dev3 "あなたはdev3です。instructions/developer.mdの指示書に従って行動してください。あなたの専門分野は品質管理・テスト・リサーチ・運営管理です。Managerからの指示をお待ちしています。"

echo ""
echo "✅ 全エージェント初期化完了！"
echo ""
echo "🎯 システム準備完了:"
echo "  - CEO: プロジェクト依頼待機中"
echo "  - Manager: CEO指示待機中"  
echo "  - Dev1-3: Manager指示待機中"
echo ""
echo "📝 プロジェクト開始方法:"
echo "  1. CEO画面に接続: tmux attach -t ceo"
echo "  2. プロジェクト依頼を入力"
echo "  3. 自動的にManager→Dev1-3に展開されます"
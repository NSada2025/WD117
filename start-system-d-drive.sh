#!/bin/bash

# Claude Code AI Team Startup Script - D Drive Version
# 次回起動用: WSL Dドライブ直下で5つのClaude Code起動

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Dドライブ直下で実行されているか確認
if [ "$PWD" != "/mnt/d" ]; then
    echo -e "${RED}Error: このスクリプトはDドライブ直下(/mnt/d/)で実行してください${NC}"
    echo -e "${YELLOW}使用方法:${NC}"
    echo "  cd /mnt/d/"
    echo "  ./start-system-d-drive.sh"
    exit 1
fi

echo -e "${CYAN}=== Claude Code AI Team System (D Drive Edition) ===${NC}"
echo -e "${GREEN}Dドライブ直下で5エージェント体制を起動します${NC}"
echo ""

# GitHub CLI認証確認
echo -e "${YELLOW}GitHub CLI認証状況を確認中...${NC}"
if gh auth status &>/dev/null; then
    echo -e "${GREEN}✓ GitHub CLI認証済み${NC}"
    gh auth status
else
    echo -e "${RED}✗ GitHub CLI未認証${NC}"
    echo -e "${YELLOW}先に 'gh auth login' を実行してください${NC}"
    exit 1
fi

# tmuxセッション名
SESSION_NAME="ai-team"

# 既存セッションの確認
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo -e "${YELLOW}既存のセッション '$SESSION_NAME' が検出されました${NC}"
    echo -e "既存のセッションに接続しますか？ (y/n): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        tmux attach-session -t $SESSION_NAME
        exit 0
    else
        echo -e "${RED}セッションを終了してから再実行してください${NC}"
        echo "コマンド: tmux kill-session -t $SESSION_NAME"
        exit 1
    fi
fi

# instructionsディレクトリの確認/作成
INSTRUCTIONS_DIR="/mnt/d/ai-team-instructions"
if [ ! -d "$INSTRUCTIONS_DIR" ]; then
    echo -e "${YELLOW}instructionsディレクトリを作成中...${NC}"
    mkdir -p "$INSTRUCTIONS_DIR"
fi

# 各役割のinstructionsファイルを作成
echo -e "${BLUE}各エージェントの指示書を準備中...${NC}"

# CEO instructions
cat > "$INSTRUCTIONS_DIR/ceo.md" << 'EOF'
あなたはCEOです。チーム全体の戦略的方向性を設定し、Managerに具体的なタスクを委任してください。

## 重要な行動規範
- 常にManagerへの委任を最優先に行う
- 細かい実装には関与しない
- 戦略的な判断と方向性の提示に専念
- プロジェクト全体の成功に責任を持つ

## 基本的なワークフロー
1. ユーザーからのプロジェクト要求を受け取る
2. 要求を分析し、戦略的な実行計画を立てる
3. Managerに具体的なタスクを委任する
4. 進捗を監視し、必要に応じて方向修正

## 注意事項
- Dドライブ全体にアクセス可能（/mnt/d/）
- 各プロジェクトディレクトリを自由に参照
- GitHub連携を活用した効率的な作業
EOF

# Manager instructions
cat > "$INSTRUCTIONS_DIR/manager.md" << 'EOF'
あなたはManagerです。CEOからの委任を受けて、開発チーム(dev1-3)に具体的なタスクを割り当ててください。

## 重要な行動規範
- CEOの戦略的指示を具体的なタスクに分解
- 各開発者の特性を活かした適切な割り当て
- 進捗管理と品質保証の責任
- 自律的な判断と問題解決

## チーム構成と役割
- dev1: 設計・アーキテクチャ担当
- dev2: 実装・開発担当
- dev3: 品質保証・テスト担当（注意: 出力量が多い）

## auto-compact対策
- dev3への指示時は出力量を考慮
- 段階的な実行を推奨
- 重要情報の事前保存を指示

## 注意事項
- Dドライブ全体にアクセス可能（/mnt/d/）
- プロジェクト間の移動が自由
- リアルタイムでの状況把握が重要
EOF

# Developer instructions (共通部分 + 個別指示)
for i in 1 2 3; do
    case $i in
        1)
            ROLE="設計・アーキテクチャ担当"
            SPECIFIC="- システム全体の設計を重視\n- 技術選定と構造設計\n- ドキュメント作成"
            ;;
        2)
            ROLE="実装・開発担当"
            SPECIFIC="- 効率的なコード実装\n- 機能開発の中心\n- バージョン管理"
            ;;
        3)
            ROLE="品質保証・テスト担当"
            SPECIFIC="- テスト実行と品質検証\n- バグ検出と修正提案\n- 出力量管理に注意（auto-compact対策）"
            ;;
    esac

    cat > "$INSTRUCTIONS_DIR/developer${i}.md" << EOF
あなたはdev${i}（${ROLE}）です。Managerからの指示に従って作業を実施してください。

## 重要な行動規範
- Managerの指示を正確に実行
- 完了後は必ず報告
- 問題発生時は即座に相談
- チーム内での協調を重視

## 専門領域
${SPECIFIC}

## 注意事項
- Dドライブ全体にアクセス可能（/mnt/d/）
- 他の開発者との連携を密に
- 進捗の定期的な報告
EOF
done

# tmuxセッション作成
echo -e "${GREEN}tmuxセッションを作成中...${NC}"
tmux new-session -d -s $SESSION_NAME -n "CEO"

# 各ペインでClaude Codeを起動
echo -e "${BLUE}各エージェントを起動中...${NC}"

# CEO
tmux send-keys -t $SESSION_NAME:CEO "cd /mnt/d/ && claude-code --profile ceo" C-m
sleep 2

# Manager
tmux new-window -t $SESSION_NAME -n "Manager"
tmux send-keys -t $SESSION_NAME:Manager "cd /mnt/d/ && claude-code --profile manager" C-m
sleep 2

# Dev1
tmux new-window -t $SESSION_NAME -n "Dev1"
tmux send-keys -t $SESSION_NAME:Dev1 "cd /mnt/d/ && claude-code --profile dev1" C-m
sleep 2

# Dev2
tmux new-window -t $SESSION_NAME -n "Dev2"
tmux send-keys -t $SESSION_NAME:Dev2 "cd /mnt/d/ && claude-code --profile dev2" C-m
sleep 2

# Dev3
tmux new-window -t $SESSION_NAME -n "Dev3"
tmux send-keys -t $SESSION_NAME:Dev3 "cd /mnt/d/ && claude-code --profile dev3" C-m
sleep 2

# 通信スクリプトの準備
echo -e "${YELLOW}通信システムを準備中...${NC}"
cat > /mnt/d/send-message.sh << 'EOF'
#!/bin/bash
# エージェント間通信スクリプト（D Drive版）

TARGET=$1
MESSAGE=$2

if [ -z "$TARGET" ] || [ -z "$MESSAGE" ]; then
    echo "使用方法: ./send-message.sh [ceo|manager|dev1|dev2|dev3] \"メッセージ\""
    exit 1
fi

# ウィンドウ名の対応
case $TARGET in
    ceo) WINDOW="CEO" ;;
    manager) WINDOW="Manager" ;;
    dev1) WINDOW="Dev1" ;;
    dev2) WINDOW="Dev2" ;;
    dev3) WINDOW="Dev3" ;;
    *) echo "不明なターゲット: $TARGET"; exit 1 ;;
esac

# メッセージ送信
tmux send-keys -t ai-team:$WINDOW "$MESSAGE" C-m
echo "メッセージを送信しました: $TARGET"
EOF
chmod +x /mnt/d/send-message.sh

# 起動完了メッセージ
echo ""
echo -e "${GREEN}=== AI Team 起動完了 ===${NC}"
echo -e "${CYAN}システム構成:${NC}"
echo "  - CEO: 戦略的意思決定"
echo "  - Manager: タスク管理と割り当て"
echo "  - Dev1: 設計・アーキテクチャ"
echo "  - Dev2: 実装・開発"
echo "  - Dev3: 品質保証・テスト"
echo ""
echo -e "${YELLOW}重要な特徴:${NC}"
echo "  ✓ Dドライブ直下で全プロジェクトアクセス可能"
echo "  ✓ DN001_TF等の研究データへの直接アクセス"
echo "  ✓ auto-compact対策実装済み"
echo "  ✓ GitHub連携対応"
echo ""
echo -e "${MAGENTA}使用方法:${NC}"
echo "  接続: tmux attach -t $SESSION_NAME"
echo "  通信: ./send-message.sh [target] \"message\""
echo "  終了: tmux kill-session -t $SESSION_NAME"
echo ""
echo -e "${BLUE}推奨ワークフロー:${NC}"
echo "  1. CEOタブでプロジェクト指示"
echo "  2. 自動的にタスク分解・実行"
echo "  3. claude-code-monitorで進捗確認"
echo ""

# セッションにアタッチ
echo -e "${GREEN}セッションに接続しています...${NC}"
tmux attach-session -t $SESSION_NAME
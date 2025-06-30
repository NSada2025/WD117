# Enterキー不要機能 実装方針

## 1. 現状分析

### 1.1 現在の問題点
- `tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m` でEnterキー（C-m）が自動送信される
- 受信側で手動でEnterキーを押す必要がある場合の柔軟性がない
- メッセージの即座実行と段階的入力の選択肢がない

### 1.2 要求される改善点
- Enterキー送信の有無を選択可能にする
- デフォルトの動作を維持しつつ、オプション機能として追加
- 既存の機能に影響を与えない後方互換性の確保

## 2. 実装方針

### 2.1 オプション設計
#### オプション1: --no-enter フラグ
```bash
./send-message.sh manager "メッセージ" --no-enter
./send-message.sh --no-enter manager "メッセージ"
```

#### オプション2: -n ショートオプション
```bash
./send-message.sh -n manager "メッセージ"
```

#### オプション3: 環境変数制御
```bash
SEND_ENTER=false ./send-message.sh manager "メッセージ"
```

### 2.2 推奨実装方式
**オプション1 + オプション2の組み合わせ**を推奨
- 可読性が高い（--no-enter）
- 効率性も考慮（-n）
- 既存機能への影響なし

## 3. 技術実装詳細

### 3.1 引数解析の修正
```bash
# 現在の引数チェック部分を拡張
NO_ENTER=false
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-enter|-n)
            NO_ENTER=true
            shift
            ;;
        --list)
            # 既存のリスト機能
            echo "利用可能なエージェント:"
            # ... 既存コード
            exit 0
            ;;
        -*|--*)
            echo "不明なオプション: $1"
            exit 1
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# 引数の再設定
set -- "${ARGS[@]}"
```

### 3.2 メッセージ送信部分の修正
```bash
# メッセージ送信
echo "[$TIMESTAMP] → $AGENT: $MESSAGE" >> $LOG_FILE

if [ "$NO_ENTER" = true ]; then
    # Enterキーなしで送信
    tmux send-keys -t $SESSION:$PANE "$MESSAGE"
    echo "メッセージを送信しました（Enterキーなし）: $AGENT"
else
    # 従来通りEnterキー付きで送信
    tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m
    echo "メッセージを送信しました: $AGENT"
fi
```

### 3.3 ヘルプメッセージの更新
```bash
if [ $# -eq 0 ]; then
    echo "使用方法: $0 [オプション] [エージェント名] \"[メッセージ]\""
    echo ""
    echo "オプション:"
    echo "  --list          利用可能なエージェント一覧を表示"
    echo "  --no-enter, -n  Enterキーを送信しない"
    echo ""
    echo "エージェント一覧: $0 --list"
    exit 1
fi
```

## 4. 実装段階

### 4.1 Phase 1: 基本実装
1. 引数解析ロジックの追加
2. --no-enter / -n オプションの実装
3. メッセージ送信部分の条件分岐追加
4. ヘルプメッセージの更新

### 4.2 Phase 2: テスト・検証
1. 既存機能の回帰テスト
2. 新機能のテストケース作成
3. エラーハンドリングの確認
4. パフォーマンス影響の評価

### 4.3 Phase 3: 最適化・拡張
1. ログメッセージの改善
2. 設定ファイルでのデフォルト動作変更機能
3. より詳細なデバッグ情報の追加

## 5. 使用例とテストケース

### 5.1 使用例
```bash
# 従来通り（Enterキー付き）
./send-message.sh manager "完了報告"

# Enterキーなし（長いオプション）
./send-message.sh --no-enter manager "入力途中のメッセージ"

# Enterキーなし（短いオプション）
./send-message.sh -n dev1 "追加入力待ちのコマンド"

# オプションの位置柔軟性
./send-message.sh manager "メッセージ" --no-enter
```

### 5.2 テストケース
```bash
# TC_NE001: --no-enterオプションの動作確認
./send-message.sh --no-enter manager "テストメッセージ"

# TC_NE002: -nオプションの動作確認
./send-message.sh -n dev1 "ショートオプションテスト"

# TC_NE003: 従来機能の動作確認
./send-message.sh manager "従来通りのメッセージ"

# TC_NE004: オプション位置の柔軟性確認
./send-message.sh manager "メッセージ" --no-enter

# TC_NE005: 不正オプションのエラー確認
./send-message.sh --invalid-option manager "エラーテスト"
```

## 6. 期待される効果

### 6.1 機能面の改善
- メッセージ送信の柔軟性向上
- インタラクティブな操作への対応
- 段階的なコマンド入力のサポート

### 6.2 運用面の改善
- 手動確認が必要な操作の効率化
- 複雑なコマンドの段階的構築
- デバッグ時の操作性向上

### 6.3 保守性の向上
- 既存機能への影響なし
- 明確なオプション体系
- テストカバレッジの向上

## 7. リスク評価と対策

### 7.1 潜在的リスク
- 既存スクリプトとの互換性問題
- 新しいオプションの学習コスト
- テストケースの増加によるメンテナンス負荷

### 7.2 対策
- 詳細な回帰テストの実施
- 段階的な機能展開
- 包括的なドキュメント作成
- ユーザーへの適切な周知

## 8. 実装優先度

### 8.1 High Priority
- 基本的な--no-enterオプションの実装
- 既存機能の動作確認
- 基本的なテストケースの作成

### 8.2 Medium Priority
- -nショートオプションの追加
- エラーハンドリングの強化
- ヘルプメッセージの改善

### 8.3 Low Priority
- 設定ファイル対応
- 詳細なログ機能
- 高度なデバッグ機能

この実装方針により、Enterキー不要機能を安全かつ効率的に追加できます。
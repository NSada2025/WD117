# API Error頻発問題の分析と対策

## 🚨 問題の深刻性

5エージェント並行実行により、単独使用時の5倍のAPI負荷が発生。
特に以下のタイミングでエラーが集中:
- プロジェクト開始時（全エージェント同時起動）
- 大規模タスク実行時（複数ツール同時使用）
- dev3のauto-compact発生時

## 📊 原因分析

### 1. レート制限の影響
```
単独使用: 10 requests/min
5エージェント: 50 requests/min（理論値）
実際: バースト的に100+ requests/min発生の可能性
```

### 2. 同時実行による競合
- **ファイルアクセス競合**: 複数エージェントが同一ファイルを同時編集
- **Git操作競合**: commit/push時のコンフリクト
- **ツール実行競合**: Bash、Read、Write等の同時実行

### 3. 長時間接続の問題
- セッション維持による接続劣化
- メモリリークの可能性
- WebSocketタイムアウト

### 4. auto-compact時の通信エラー
- dev3の大量出力時に他エージェントへの影響
- 通信バッファオーバーフロー
- レスポンス遅延の連鎖

### 5. ネットワーク帯域圧迫
- 5つの独立したWebSocket接続
- 大量のツール実行結果の転送
- リアルタイム同期による帯域使用

## 🛠️ 対策案

### 1. エージェント間の実行タイミング調整

```bash
# start-system-staggered.sh
#!/bin/bash

# CEO起動
tmux send-keys -t ceo "claude instructions/ceo.md" C-m
sleep 5  # 5秒待機

# Manager起動
tmux send-keys -t team:0.0 "claude instructions/manager.md" C-m
sleep 3  # 3秒待機

# Dev1-3を順次起動
for i in 1 2 3; do
    tmux send-keys -t team:0.$i "claude instructions/developer.md" C-m
    sleep 2  # 2秒間隔
done
```

### 2. API呼び出し間隔の制御

```python
# api-rate-limiter.py
import time
from threading import Lock

class APIRateLimiter:
    def __init__(self, max_calls_per_minute=40):  # 安全マージン
        self.max_calls = max_calls_per_minute
        self.call_times = []
        self.lock = Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            # 1分以内の呼び出しをカウント
            self.call_times = [t for t in self.call_times if now - t < 60]
            
            if len(self.call_times) >= self.max_calls:
                # 待機時間計算
                sleep_time = 60 - (now - self.call_times[0]) + 1
                time.sleep(sleep_time)
            
            self.call_times.append(now)
```

### 3. エラー時の自動リトライ

```bash
# send-message-with-retry.sh
#!/bin/bash

TARGET=$1
MESSAGE=$2
MAX_RETRIES=3
RETRY_DELAY=5

for i in $(seq 1 $MAX_RETRIES); do
    if ./send-message.sh "$TARGET" "$MESSAGE"; then
        echo "メッセージ送信成功"
        exit 0
    else
        echo "送信失敗 (試行 $i/$MAX_RETRIES)"
        if [ $i -lt $MAX_RETRIES ]; then
            echo "${RETRY_DELAY}秒後にリトライ..."
            sleep $RETRY_DELAY
        fi
    fi
done

echo "送信失敗: 最大リトライ回数に達しました"
exit 1
```

### 4. 使用量監視の強化

```python
# enhanced-monitor.py
class EnhancedClaudeMonitor:
    def __init__(self):
        self.api_calls = {}
        self.error_counts = {}
        self.last_compact = {}
    
    def track_api_call(self, agent_name):
        self.api_calls[agent_name] = self.api_calls.get(agent_name, 0) + 1
        
    def track_error(self, agent_name, error_type):
        if agent_name not in self.error_counts:
            self.error_counts[agent_name] = {}
        self.error_counts[agent_name][error_type] = \
            self.error_counts[agent_name].get(error_type, 0) + 1
    
    def get_dashboard(self):
        return {
            "total_api_calls": sum(self.api_calls.values()),
            "calls_per_agent": self.api_calls,
            "error_summary": self.error_counts,
            "recommendations": self.get_recommendations()
        }
    
    def get_recommendations(self):
        recommendations = []
        total_calls = sum(self.api_calls.values())
        
        if total_calls > 40:  # 1分あたり
            recommendations.append("API呼び出し頻度が高すぎます。タスクを分散してください。")
        
        if self.error_counts:
            recommendations.append("エラーが発生しています。エージェント数を減らすことを検討してください。")
        
        return recommendations
```

## 📋 実装優先順位

1. **即時対応**
   - エージェント起動の段階的実行（staggered start）
   - send-message-with-retry.shの導入

2. **短期対応**
   - API Rate Limiterの実装
   - claude-code-monitor拡張

3. **中期対応**
   - エージェント数の動的調整機能
   - 負荷分散アルゴリズム

## 🎯 推奨運用方法

### 低負荷運用モード
```bash
# 3エージェント運用（CEO + Manager + Dev1のみ）
./start-system-minimal.sh

# 必要に応じてDev2, Dev3を追加起動
./add-agent.sh dev2
```

### 負荷分散運用
```bash
# タスクの性質に応じてエージェント割当
# 設計フェーズ: CEO + Manager + Dev1
# 実装フェーズ: Manager + Dev2
# テストフェーズ: Manager + Dev3（単独）
```

### エラー監視強化
```bash
# リアルタイムモニタリング
watch -n 5 'claude-code-monitor --api-stats'

# エラー発生時の自動通知
./monitor-with-alert.sh
```

## ⚠️ 暫定回避策

1. **時間帯をずらした運用**
   - 高負荷タスクは夜間実行
   - API使用量の少ない時間帯を活用

2. **タスクの細分化**
   - 大規模タスクを小さく分割
   - 順次実行で負荷分散

3. **定期的な再起動**
   - 2-3時間ごとにセッション再起動
   - メモリリーク対策

これらの対策により、5エージェント体制を
より安定的に運用することが可能になります。
# Auto-Compact事前検知システム設計書

## 📋 概要

画面異常インシデントの経験を基に、auto-compact発生を事前検知し、システム安定性を確保するための包括的なソリューション。

## 🎯 目的

1. **事前検知**: auto-compact発生前の予兆を検出
2. **自動対応**: 検知時の自動復旧・回避アクション
3. **継続性確保**: 作業中断を最小限に抑制
4. **可視化**: リアルタイムの状態監視

## 🏗️ システムアーキテクチャ

### コアコンポーネント

```
auto-compact-detection/
├── monitors/
│   ├── tmux-health-monitor.py      # tmuxセッション健全性監視
│   ├── buffer-size-tracker.py      # バッファサイズ追跡
│   ├── session-age-monitor.py      # セッション経過時間監視
│   └── output-rate-analyzer.py     # 出力レート分析
├── detectors/
│   ├── compact-predictor.py        # compact発生予測エンジン
│   ├── anomaly-detector.py         # 異常パターン検出
│   └── threshold-analyzer.py      # 閾値分析
├── actions/
│   ├── preemptive-clear.py        # 予防的クリア実行
│   ├── session-rotation.py        # セッション自動ローテーション
│   ├── buffer-optimization.py     # バッファ最適化
│   └── emergency-backup.py        # 緊急バックアップ
├── dashboard/
│   ├── realtime-status.py         # リアルタイムステータス表示
│   ├── health-metrics.py          # 健全性メトリクス
│   └── alert-panel.py             # アラートパネル
└── integration/
    ├── workflow-hook.py           # ワークフローシステム連携
    ├── monitor-bridge.py          # claude-code-monitor連携
    └── notification-system.py     # 通知システム
```

## 🔍 検知メカニズム

### 1. 予兆検知指標

```python
class CompactPredictor:
    def __init__(self):
        self.indicators = {
            "buffer_size": {
                "warning": 80,     # バッファ使用率80%
                "critical": 90,    # バッファ使用率90%
                "emergency": 95    # バッファ使用率95%
            },
            "session_age": {
                "warning": 3600,   # 1時間
                "critical": 7200,  # 2時間
                "emergency": 10800 # 3時間
            },
            "output_rate": {
                "warning": 1000,   # 1000行/分
                "critical": 2000,  # 2000行/分
                "emergency": 3000  # 3000行/分
            },
            "scroll_buffer": {
                "warning": 50000,  # 5万行
                "critical": 80000, # 8万行
                "emergency": 100000 # 10万行
            }
        }
```

### 2. 複合判定ロジック

```python
def calculate_compact_risk_score(metrics):
    """auto-compactリスクスコアを計算"""
    
    weights = {
        "buffer_usage": 0.3,
        "session_age": 0.2,
        "output_rate": 0.25,
        "scroll_buffer": 0.25
    }
    
    risk_score = 0
    for metric, value in metrics.items():
        normalized = normalize_metric(metric, value)
        risk_score += normalized * weights[metric]
    
    return risk_score  # 0-100
```

## 🚨 自動対応アクション

### レベル1: 予防的対応（リスクスコア 60-70）
```bash
# バッファクリア
tmux clear-history -t session_name

# 出力レート制限
nice -n 10 command  # CPU優先度を下げる

# ログローテーション
rotate_large_logs()
```

### レベル2: 積極的対応（リスクスコア 70-85）
```bash
# セッション分割
split_large_session()

# バッファサイズ調整
tmux set-option -g history-limit 5000

# 一時停止と再開
pause_heavy_operations()
```

### レベル3: 緊急対応（リスクスコア 85+）
```bash
# セッション状態保存
backup_session_state()

# 新セッション起動
create_fresh_session()

# 作業移行
migrate_to_new_session()
```

## 📊 リアルタイム監視ダッシュボード

### ターミナルベースUI
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     AUTO-COMPACT DETECTION DASHBOARD                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║ 📊 SYSTEM HEALTH                                                             ║
║ ├─ Risk Score: ████████████░░░░░░░░ 62% [WARNING]                          ║
║ ├─ Buffer Usage: ██████████████░░░░░ 72%                                   ║
║ ├─ Session Age: 1h 23m                                                      ║
║ └─ Output Rate: 856 lines/min                                               ║
║                                                                              ║
║ 🔍 ACTIVE SESSIONS                                                           ║
║ ├─ neuroscience-team    [●] 68% risk | 1.2h | 45k lines                   ║
║ ├─ workflow-dev-team    [●] 45% risk | 0.5h | 12k lines                   ║
║ └─ monitor-dashboard    [●] 23% risk | 2.1h | 8k lines                    ║
║                                                                              ║
║ ⚡ RECENT ACTIONS                                                            ║
║ ├─ [12:05] Cleared buffer for neuroscience-team (prevented compact)        ║
║ ├─ [11:48] Rotated session workflow-dev-team                               ║
║ └─ [11:32] Optimized buffer settings globally                              ║
║                                                                              ║
║ 🎯 RECOMMENDATIONS                                                           ║
║ • Consider clearing neuroscience-team buffer soon                          ║
║ • Schedule session rotation for long-running projects                      ║
║ • Enable automatic buffer management                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 🔧 実装詳細

### tmux健全性監視
```python
class TmuxHealthMonitor:
    def __init__(self):
        self.check_interval = 30  # 30秒ごと
        self.sessions = {}
        
    def monitor_session(self, session_name):
        """セッションの健全性を監視"""
        metrics = {
            "buffer_size": self.get_buffer_size(session_name),
            "line_count": self.get_line_count(session_name),
            "creation_time": self.get_session_age(session_name),
            "output_rate": self.calculate_output_rate(session_name)
        }
        
        risk_score = self.calculate_risk_score(metrics)
        
        if risk_score > 60:
            self.trigger_preventive_action(session_name, risk_score)
        
        return metrics, risk_score
```

### 予測アルゴリズム
```python
class CompactPredictor:
    def __init__(self):
        self.history = []  # 過去のcompactイベント
        self.patterns = self.learn_patterns()
        
    def predict_compact_time(self, current_metrics):
        """compactまでの予測時間を計算"""
        
        # 線形回帰による予測
        growth_rate = self.calculate_growth_rate(current_metrics)
        buffer_remaining = self.get_buffer_remaining()
        
        if growth_rate > 0:
            time_to_compact = buffer_remaining / growth_rate
            return time_to_compact
        
        return float('inf')  # 成長していない
        
    def learn_patterns(self):
        """過去のパターンから学習"""
        # 機械学習モデルによるパターン認識
        # （簡略化のため統計的手法を使用）
        return self.analyze_historical_data()
```

## 🛡️ 統合セーフティネット

### 1. 自動バックアップ
```bash
# 定期的なセッション状態保存
*/5 * * * * /usr/bin/save-tmux-sessions.sh

# 重要な作業内容の自動保存
auto-save-work-context.py
```

### 2. フェイルオーバー機構
```python
def failover_mechanism(session_name):
    """セッション障害時の自動フェイルオーバー"""
    
    # 1. 現在の状態を保存
    backup_current_state(session_name)
    
    # 2. 新しいセッションを作成
    new_session = create_fresh_session(session_name + "_new")
    
    # 3. 作業を移行
    restore_work_context(new_session)
    
    # 4. 古いセッションをクリーンアップ
    cleanup_old_session(session_name)
```

### 3. 継続性保証
```python
class ContinuityManager:
    def ensure_continuity(self):
        """作業継続性を保証"""
        
        # チェックポイント作成
        self.create_checkpoint()
        
        # 状態の永続化
        self.persist_state()
        
        # リカバリプラン準備
        self.prepare_recovery_plan()
```

## 📈 期待される効果

1. **インシデント削減**: auto-compact発生を90%以上防止
2. **作業継続性**: 中断時間を5分以内に短縮
3. **自動復旧**: 人的介入なしで80%のケースを自動処理
4. **可視性向上**: リアルタイムでシステム健全性を把握

## 🚀 実装ロードマップ

### Phase 1: 基礎監視（1-2日）
- [ ] tmux健全性監視実装
- [ ] 基本的なメトリクス収集
- [ ] シンプルな閾値アラート

### Phase 2: 予測エンジン（2-3日）
- [ ] リスクスコア計算実装
- [ ] compact予測アルゴリズム
- [ ] パターン学習機能

### Phase 3: 自動対応（2-3日）
- [ ] 予防的アクション実装
- [ ] セッションローテーション
- [ ] 自動バックアップ機構

### Phase 4: 統合・最適化（1-2日）
- [ ] ワークフローシステム連携
- [ ] ダッシュボード完成
- [ ] パフォーマンス最適化

---

**優先度: 最高** - 画面異常インシデントの再発防止のため即座に着手
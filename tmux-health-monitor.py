#!/usr/bin/env python3
"""
tmux Health Monitor
tmuxセッションの健全性を監視し、auto-compact発生を予防
"""

import subprocess
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class TmuxHealthMonitor:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.sessions_data = {}
        self.risk_thresholds = {
            "buffer_lines": {
                "warning": 50000,    # 5万行
                "critical": 80000,   # 8万行  
                "emergency": 100000  # 10万行
            },
            "session_age_seconds": {
                "warning": 3600,     # 1時間
                "critical": 7200,    # 2時間
                "emergency": 10800   # 3時間
            },
            "output_rate_per_min": {
                "warning": 1000,     # 1000行/分
                "critical": 2000,    # 2000行/分
                "emergency": 3000    # 3000行/分
            },
            "pane_count": {
                "warning": 10,       # 10ペイン
                "critical": 15,      # 15ペイン
                "emergency": 20      # 20ペイン
            }
        }
        self.history_file = "tmux-health-history.json"
        self.alert_log = "tmux-health-alerts.log"
        
    def get_tmux_sessions(self) -> List[str]:
        """アクティブなtmuxセッション一覧を取得"""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True, text=True, check=True
            )
            return [s.strip() for s in result.stdout.split('\n') if s.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def get_session_info(self, session_name: str) -> Dict:
        """セッションの詳細情報を取得"""
        try:
            # セッション作成時刻
            created_result = subprocess.run(
                ["tmux", "display-message", "-t", session_name, "-p", "#{session_created}"],
                capture_output=True, text=True, check=True
            )
            created_timestamp = int(created_result.stdout.strip())
            session_age = int(time.time()) - created_timestamp
            
            # ペイン数
            panes_result = subprocess.run(
                ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"],
                capture_output=True, text=True, check=True
            )
            pane_count = len([p for p in panes_result.stdout.split('\n') if p.strip()])
            
            # バッファ行数（推定）
            buffer_lines = self.estimate_buffer_lines(session_name)
            
            # 出力レート計算
            output_rate = self.calculate_output_rate(session_name, buffer_lines)
            
            return {
                "session_name": session_name,
                "created_timestamp": created_timestamp,
                "session_age_seconds": session_age,
                "pane_count": pane_count,
                "buffer_lines": buffer_lines,
                "output_rate_per_min": output_rate,
                "last_checked": datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "session_name": session_name,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }
    
    def estimate_buffer_lines(self, session_name: str) -> int:
        """バッファ内の行数を推定"""
        try:
            # 各ペインのキャプチャサイズから推定
            panes_result = subprocess.run(
                ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"],
                capture_output=True, text=True, check=True
            )
            
            total_lines = 0
            for pane_id in panes_result.stdout.strip().split('\n'):
                if pane_id:
                    # キャプチャ可能な行数を確認
                    try:
                        capture_result = subprocess.run(
                            ["tmux", "capture-pane", "-t", f"{session_name}:{pane_id}", 
                             "-p", "-S", "-1000"],  # 最新1000行のみ取得
                            capture_output=True, text=True, check=True
                        )
                        lines = len(capture_result.stdout.split('\n'))
                        # 実際のバッファはもっと大きい可能性があるため推定値を使用
                        total_lines += lines * 10  # 推定倍率
                    except:
                        total_lines += 5000  # デフォルト推定値
            
            return total_lines
            
        except:
            return 10000  # エラー時のデフォルト値
    
    def calculate_output_rate(self, session_name: str, current_lines: int) -> float:
        """出力レート（行/分）を計算"""
        if session_name not in self.sessions_data:
            return 0.0
        
        prev_data = self.sessions_data[session_name]
        if "buffer_lines" not in prev_data or "last_checked" not in prev_data:
            return 0.0
        
        # 前回チェックからの経過時間
        prev_time = datetime.fromisoformat(prev_data["last_checked"])
        time_diff = (datetime.now() - prev_time).total_seconds()
        
        if time_diff <= 0:
            return 0.0
        
        # 行数の変化
        lines_diff = current_lines - prev_data["buffer_lines"]
        
        # 分あたりのレート
        rate_per_min = (lines_diff / time_diff) * 60
        
        return max(0, rate_per_min)  # 負の値は0に
    
    def calculate_risk_score(self, session_info: Dict) -> Tuple[float, str]:
        """リスクスコアを計算（0-100）"""
        if "error" in session_info:
            return 0.0, "error"
        
        risk_components = {
            "buffer_lines": 0.35,      # 35%の重み
            "session_age_seconds": 0.20,  # 20%の重み
            "output_rate_per_min": 0.30,  # 30%の重み
            "pane_count": 0.15        # 15%の重み
        }
        
        total_risk = 0.0
        risk_level = "normal"
        
        for metric, weight in risk_components.items():
            if metric not in session_info:
                continue
            
            value = session_info[metric]
            thresholds = self.risk_thresholds[metric]
            
            # 正規化（0-100）
            if value <= thresholds["warning"]:
                normalized = (value / thresholds["warning"]) * 33
            elif value <= thresholds["critical"]:
                normalized = 33 + ((value - thresholds["warning"]) / 
                                  (thresholds["critical"] - thresholds["warning"])) * 33
            elif value <= thresholds["emergency"]:
                normalized = 66 + ((value - thresholds["critical"]) / 
                                  (thresholds["emergency"] - thresholds["critical"])) * 34
            else:
                normalized = 100
            
            total_risk += normalized * weight
        
        # リスクレベル判定
        if total_risk >= 85:
            risk_level = "emergency"
        elif total_risk >= 70:
            risk_level = "critical"
        elif total_risk >= 60:
            risk_level = "warning"
        
        return total_risk, risk_level
    
    def should_take_action(self, risk_score: float, risk_level: str) -> List[str]:
        """必要なアクションを決定"""
        actions = []
        
        if risk_level == "emergency":
            actions.extend([
                "clear_buffer",
                "rotate_session",
                "backup_state"
            ])
        elif risk_level == "critical":
            actions.extend([
                "clear_buffer",
                "reduce_output_rate"
            ])
        elif risk_level == "warning":
            actions.append("clear_buffer")
        
        return actions
    
    def execute_preventive_actions(self, session_name: str, actions: List[str]):
        """予防的アクションを実行"""
        results = []
        
        for action in actions:
            if action == "clear_buffer":
                result = self.clear_session_buffer(session_name)
                results.append(("clear_buffer", result))
            
            elif action == "reduce_output_rate":
                result = self.reduce_output_rate(session_name)
                results.append(("reduce_output_rate", result))
            
            elif action == "rotate_session":
                result = self.rotate_session(session_name)
                results.append(("rotate_session", result))
            
            elif action == "backup_state":
                result = self.backup_session_state(session_name)
                results.append(("backup_state", result))
        
        return results
    
    def clear_session_buffer(self, session_name: str) -> bool:
        """セッションバッファをクリア"""
        try:
            # 全ペインのヒストリーをクリア
            panes_result = subprocess.run(
                ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"],
                capture_output=True, text=True, check=True
            )
            
            for pane_id in panes_result.stdout.strip().split('\n'):
                if pane_id:
                    subprocess.run(
                        ["tmux", "clear-history", "-t", f"{session_name}:{pane_id}"],
                        check=True
                    )
            
            self.log_action(session_name, "clear_buffer", "success")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_action(session_name, "clear_buffer", f"failed: {e}")
            return False
    
    def reduce_output_rate(self, session_name: str) -> bool:
        """出力レートを削減（実装は環境依存）"""
        # 実装例: セッション内のプロセスにシグナルを送る
        # または nice値を調整するなど
        self.log_action(session_name, "reduce_output_rate", "attempted")
        return True
    
    def rotate_session(self, session_name: str) -> bool:
        """セッションをローテート（新しいセッションに移行）"""
        try:
            new_session = f"{session_name}_rotated_{int(time.time())}"
            
            # 新セッション作成
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", new_session],
                check=True
            )
            
            self.log_action(session_name, "rotate_session", f"created {new_session}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_action(session_name, "rotate_session", f"failed: {e}")
            return False
    
    def backup_session_state(self, session_name: str) -> bool:
        """セッション状態をバックアップ"""
        try:
            backup_dir = f"tmux-backups/{session_name}_{int(time.time())}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 各ペインの内容を保存
            panes_result = subprocess.run(
                ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_id}"],
                capture_output=True, text=True, check=True
            )
            
            for pane_id in panes_result.stdout.strip().split('\n'):
                if pane_id:
                    capture_result = subprocess.run(
                        ["tmux", "capture-pane", "-t", f"{session_name}:{pane_id}", 
                         "-p", "-S", "-"],
                        capture_output=True, text=True
                    )
                    
                    with open(f"{backup_dir}/pane_{pane_id}.txt", "w") as f:
                        f.write(capture_result.stdout)
            
            self.log_action(session_name, "backup_state", f"saved to {backup_dir}")
            return True
            
        except Exception as e:
            self.log_action(session_name, "backup_state", f"failed: {e}")
            return False
    
    def log_action(self, session_name: str, action: str, result: str):
        """アクションをログに記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session": session_name,
            "action": action,
            "result": result
        }
        
        with open(self.alert_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def save_history(self):
        """監視履歴を保存"""
        history_data = {
            "last_update": datetime.now().isoformat(),
            "sessions": self.sessions_data
        }
        
        with open(self.history_file, "w") as f:
            json.dump(history_data, f, indent=2)
    
    def load_history(self):
        """監視履歴を読み込み"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.sessions_data = data.get("sessions", {})
        except:
            self.sessions_data = {}
    
    def monitor_once(self) -> Dict:
        """1回の監視サイクルを実行"""
        sessions = self.get_tmux_sessions()
        results = {}
        
        for session_name in sessions:
            # セッション情報取得
            session_info = self.get_session_info(session_name)
            
            # リスクスコア計算
            risk_score, risk_level = self.calculate_risk_score(session_info)
            session_info["risk_score"] = risk_score
            session_info["risk_level"] = risk_level
            
            # アクション判定
            actions = self.should_take_action(risk_score, risk_level)
            if actions:
                action_results = self.execute_preventive_actions(session_name, actions)
                session_info["actions_taken"] = action_results
            
            # データ更新
            self.sessions_data[session_name] = session_info
            results[session_name] = session_info
        
        # 履歴保存
        self.save_history()
        
        return results
    
    def run_continuous_monitoring(self):
        """継続的な監視を実行"""
        print("🚀 Starting tmux Health Monitor")
        print(f"Check interval: {self.check_interval} seconds")
        print("Press Ctrl+C to stop")
        
        self.load_history()
        
        try:
            while True:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking sessions...")
                
                results = self.monitor_once()
                
                # 結果表示
                for session_name, info in results.items():
                    if "error" in info:
                        print(f"  ❌ {session_name}: Error - {info['error']}")
                    else:
                        risk_icon = {
                            "normal": "🟢",
                            "warning": "🟡",
                            "critical": "🟠",
                            "emergency": "🔴"
                        }.get(info["risk_level"], "⚪")
                        
                        print(f"  {risk_icon} {session_name}: "
                              f"Risk {info['risk_score']:.1f}% | "
                              f"Age {info['session_age_seconds']//60}m | "
                              f"Lines ~{info['buffer_lines']} | "
                              f"Rate {info['output_rate_per_min']:.0f}/min")
                        
                        if "actions_taken" in info:
                            for action, success in info["actions_taken"]:
                                status = "✓" if success else "✗"
                                print(f"     {status} {action}")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            self.save_history()

def main():
    """メイン実行関数"""
    import sys
    
    # コマンドライン引数でチェック間隔を指定可能
    check_interval = 30
    if len(sys.argv) > 1:
        try:
            check_interval = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 tmux-health-monitor.py [check_interval_seconds]")
            return
    
    monitor = TmuxHealthMonitor(check_interval=check_interval)
    monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()
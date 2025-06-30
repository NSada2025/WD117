#!/usr/bin/env python3
"""
Realtime Status Dashboard
リアルタイムでシステム状態を表示する統合ダッシュボード
"""

import os
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

class RealtimeStatusDashboard:
    def __init__(self):
        self.refresh_interval = 5  # 5秒ごとに更新
        self.clear_screen = True
        self.dashboard_width = 80
        
    def clear_terminal(self):
        """ターミナルをクリア"""
        if self.clear_screen:
            os.system('clear' if os.name == 'posix' else 'cls')
    
    def get_tmux_health_data(self) -> Dict:
        """tmux健全性データを取得"""
        try:
            if os.path.exists("tmux-health-history.json"):
                with open("tmux-health-history.json", "r") as f:
                    data = json.load(f)
                    return data.get("sessions", {})
        except:
            pass
        return {}
    
    def get_project_sessions(self) -> List[Dict]:
        """アクティブなプロジェクトセッション情報を取得"""
        try:
            result = subprocess.run(
                ["python3", "tmux-session-manager.py", "list"],
                capture_output=True, text=True
            )
            # 出力から情報を抽出（簡略化）
            sessions = []
            for line in result.stdout.split('\n'):
                if "🟢" in line or "🟡" in line or "🔴" in line:
                    # セッション情報をパース
                    parts = line.strip().split()
                    if len(parts) > 2:
                        sessions.append({
                            "name": parts[2],
                            "status": "active" if "🟢" in line else "warning"
                        })
            return sessions
        except:
            return []
    
    def get_token_usage(self) -> Dict:
        """トークン使用量データを取得"""
        try:
            if os.path.exists("token-usage-cache.json"):
                with open("token-usage-cache.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def format_bytes(self, bytes_value: int) -> str:
        """バイト数を人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}TB"
    
    def format_time_ago(self, timestamp_str: str) -> str:
        """タイムスタンプを「〜前」形式に変換"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            delta = datetime.now() - timestamp
            
            if delta.total_seconds() < 60:
                return f"{int(delta.total_seconds())}秒前"
            elif delta.total_seconds() < 3600:
                return f"{int(delta.total_seconds() / 60)}分前"
            elif delta.total_seconds() < 86400:
                return f"{int(delta.total_seconds() / 3600)}時間前"
            else:
                return f"{int(delta.total_seconds() / 86400)}日前"
        except:
            return "不明"
    
    def draw_header(self):
        """ヘッダーを描画"""
        print("╔" + "═" * (self.dashboard_width - 2) + "╗")
        title = "REALTIME SYSTEM STATUS DASHBOARD"
        padding = (self.dashboard_width - len(title) - 2) // 2
        print("║" + " " * padding + title + " " * (self.dashboard_width - len(title) - padding - 2) + "║")
        print("╠" + "═" * (self.dashboard_width - 2) + "╣")
    
    def draw_tmux_health_section(self, health_data: Dict):
        """tmux健全性セクションを描画"""
        print("║ 🏥 TMUX HEALTH MONITOR" + " " * (self.dashboard_width - 25) + "║")
        print("║" + " " * (self.dashboard_width - 2) + "║")
        
        if not health_data:
            print("║   No tmux health data available" + " " * (self.dashboard_width - 35) + "║")
        else:
            for session_name, info in list(health_data.items())[:5]:  # 最大5セッション表示
                if "error" in info:
                    continue
                
                risk_score = info.get("risk_score", 0)
                risk_level = info.get("risk_level", "normal")
                
                # リスクバー作成
                bar_width = 20
                filled = int(risk_score * bar_width / 100)
                risk_bar = "█" * filled + "░" * (bar_width - filled)
                
                # リスクアイコン
                risk_icon = {
                    "normal": "🟢",
                    "warning": "🟡", 
                    "critical": "🟠",
                    "emergency": "🔴"
                }.get(risk_level, "⚪")
                
                # セッション情報表示
                session_display = f"{session_name[:15]:15}"
                risk_display = f"{risk_icon} {risk_bar} {risk_score:5.1f}%"
                
                line = f"   {session_display} {risk_display}"
                print("║" + line + " " * (self.dashboard_width - len(line) - 2) + "║")
                
                # 詳細情報
                age_min = info.get("session_age_seconds", 0) // 60
                lines = info.get("buffer_lines", 0)
                rate = info.get("output_rate_per_min", 0)
                
                details = f"     Age: {age_min}m | Lines: ~{lines:,} | Rate: {rate:.0f}/min"
                print("║" + details[:self.dashboard_width-2] + " " * (self.dashboard_width - len(details) - 2) + "║")
        
        print("║" + " " * (self.dashboard_width - 2) + "║")
    
    def draw_project_sessions_section(self, sessions: List[Dict]):
        """プロジェクトセッションセクションを描画"""
        print("║ 📂 ACTIVE PROJECTS" + " " * (self.dashboard_width - 21) + "║")
        print("║" + " " * (self.dashboard_width - 2) + "║")
        
        if not sessions:
            print("║   No active project sessions" + " " * (self.dashboard_width - 32) + "║")
        else:
            for session in sessions[:5]:  # 最大5プロジェクト表示
                name = session.get("name", "Unknown")
                status = session.get("status", "unknown")
                
                status_icon = "🟢" if status == "active" else "🟡"
                line = f"   {status_icon} {name}"
                print("║" + line + " " * (self.dashboard_width - len(line) - 2) + "║")
        
        print("║" + " " * (self.dashboard_width - 2) + "║")
    
    def draw_token_usage_section(self, token_data: Dict):
        """トークン使用量セクションを描画"""
        print("║ 💰 TOKEN USAGE" + " " * (self.dashboard_width - 17) + "║")
        print("║" + " " * (self.dashboard_width - 2) + "║")
        
        if not token_data:
            print("║   No token usage data available" + " " * (self.dashboard_width - 35) + "║")
        else:
            total_tokens = 0
            for project_name, project_data in list(token_data.items())[:3]:  # 最大3プロジェクト
                tokens = project_data.get("total_tokens", 0)
                total_tokens += tokens
                
                # トークン表示
                token_display = f"{tokens:,}" if tokens < 1000000 else f"{tokens/1000000:.1f}M"
                line = f"   {project_name[:20]:20} {token_display:>10} tokens"
                print("║" + line + " " * (self.dashboard_width - len(line) - 2) + "║")
            
            if total_tokens > 0:
                total_display = f"{total_tokens:,}" if total_tokens < 1000000 else f"{total_tokens/1000000:.1f}M"
                line = f"   {'TOTAL':20} {total_display:>10} tokens"
                print("║" + "─" * (self.dashboard_width - 2) + "║")
                print("║" + line + " " * (self.dashboard_width - len(line) - 2) + "║")
        
        print("║" + " " * (self.dashboard_width - 2) + "║")
    
    def draw_system_alerts(self):
        """システムアラートセクションを描画"""
        print("║ 🚨 SYSTEM ALERTS" + " " * (self.dashboard_width - 19) + "║")
        print("║" + " " * (self.dashboard_width - 2) + "║")
        
        # アラートログから最新のアラートを取得
        alerts = self.get_recent_alerts()
        
        if not alerts:
            print("║   ✅ No active alerts" + " " * (self.dashboard_width - 25) + "║")
        else:
            for alert in alerts[:3]:  # 最大3アラート表示
                timestamp = alert.get("timestamp", "")
                action = alert.get("action", "")
                result = alert.get("result", "")
                
                time_ago = self.format_time_ago(timestamp)
                line = f"   [{time_ago}] {action}: {result}"
                print("║" + line[:self.dashboard_width-2] + " " * max(0, self.dashboard_width - len(line) - 2) + "║")
        
        print("║" + " " * (self.dashboard_width - 2) + "║")
    
    def get_recent_alerts(self) -> List[Dict]:
        """最新のアラートを取得"""
        alerts = []
        try:
            if os.path.exists("tmux-health-alerts.log"):
                with open("tmux-health-alerts.log", "r") as f:
                    lines = f.readlines()[-10:]  # 最新10件
                    for line in reversed(lines):
                        try:
                            alert = json.loads(line.strip())
                            alerts.append(alert)
                            if len(alerts) >= 3:
                                break
                        except:
                            continue
        except:
            pass
        return alerts
    
    def draw_footer(self):
        """フッターを描画"""
        print("╠" + "═" * (self.dashboard_width - 2) + "╣")
        
        # 更新時刻
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_line = f"Last Update: {current_time} | Refresh: {self.refresh_interval}s"
        print("║ " + update_line + " " * (self.dashboard_width - len(update_line) - 3) + "║")
        
        # 操作方法
        controls = "Press Ctrl+C to exit | 'p' to pause | 'r' to refresh"
        print("║ " + controls + " " * (self.dashboard_width - len(controls) - 3) + "║")
        
        print("╚" + "═" * (self.dashboard_width - 2) + "╝")
    
    def draw_dashboard(self):
        """ダッシュボード全体を描画"""
        self.clear_terminal()
        
        # データ取得
        health_data = self.get_tmux_health_data()
        project_sessions = self.get_project_sessions()
        token_data = self.get_token_usage()
        
        # 各セクション描画
        self.draw_header()
        self.draw_tmux_health_section(health_data)
        self.draw_project_sessions_section(project_sessions)
        self.draw_token_usage_section(token_data)
        self.draw_system_alerts()
        self.draw_footer()
    
    def run(self):
        """ダッシュボードを実行"""
        print("Starting Realtime Status Dashboard...")
        print("Initializing...")
        time.sleep(1)
        
        try:
            while True:
                self.draw_dashboard()
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            self.clear_terminal()
            print("\n👋 Dashboard stopped")
            print("Thank you for using Realtime Status Dashboard!")

def main():
    """メイン実行関数"""
    import sys
    
    dashboard = RealtimeStatusDashboard()
    
    # コマンドライン引数で更新間隔を設定可能
    if len(sys.argv) > 1:
        try:
            dashboard.refresh_interval = int(sys.argv[1])
        except ValueError:
            print("Usage: python3 realtime-status-dashboard.py [refresh_interval_seconds]")
            return
    
    dashboard.run()

if __name__ == "__main__":
    main()
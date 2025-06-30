#!/usr/bin/env python3
"""
Claude Code Monitor Integration
claude-code-monitorとの連携強化システム
"""

import subprocess
import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

class MonitorIntegration:
    def __init__(self):
        self.monitor_repo = "NSada2025/claude-code-monitor"
        self.monitor_paths = [
            "../claude-code-monitor",
            "../../claude-code-monitor", 
            os.path.expanduser("~/claude-code-monitor"),
            "/tmp/claude-code-monitor"
        ]
        self.usage_cache_file = "token-usage-cache.json"
        self.alert_thresholds = {
            "warning": 1000000,   # 1M tokens
            "critical": 2000000,  # 2M tokens
            "emergency": 3000000  # 3M tokens
        }
        
    def find_monitor_directory(self) -> Optional[str]:
        """claude-code-monitor リポジトリディレクトリを検索"""
        for path in self.monitor_paths:
            if os.path.isdir(path) and os.path.exists(os.path.join(path, "claude_code_monitor.py")):
                return os.path.abspath(path)
        return None
    
    def clone_monitor_repository(self) -> Optional[str]:
        """claude-code-monitor リポジトリをクローン"""
        clone_path = "/tmp/claude-code-monitor"
        
        print(f"🔄 Cloning {self.monitor_repo} to {clone_path}...")
        
        try:
            # 既存ディレクトリを削除
            if os.path.exists(clone_path):
                subprocess.run(["rm", "-rf", clone_path], check=True)
            
            # クローン実行
            result = subprocess.run([
                "gh", "repo", "clone", self.monitor_repo, clone_path
            ], check=True, capture_output=True, text=True)
            
            if os.path.exists(os.path.join(clone_path, "claude_code_monitor.py")):
                print(f"✅ Successfully cloned monitor to {clone_path}")
                return clone_path
            else:
                print(f"❌ Monitor script not found after cloning")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone monitor repository: {e}")
            return None
    
    def setup_monitor_environment(self) -> Optional[str]:
        """モニター環境をセットアップ"""
        # 既存ディレクトリを検索
        monitor_dir = self.find_monitor_directory()
        
        if monitor_dir:
            print(f"✅ Found existing monitor at: {monitor_dir}")
            return monitor_dir
        
        # 見つからない場合はクローン
        print("📦 claude-code-monitor not found locally, cloning...")
        return self.clone_monitor_repository()
    
    def is_monitor_running(self, project_name: str) -> bool:
        """指定プロジェクトのモニターが動作中かチェック"""
        session_name = f"{project_name}-monitor"
        
        try:
            result = subprocess.run([
                "tmux", "has-session", "-t", session_name
            ], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def start_project_monitor(self, project_name: str, monitor_dir: str = None) -> bool:
        """プロジェクト専用モニターを起動"""
        if self.is_monitor_running(project_name):
            print(f"ℹ️  Monitor already running for project: {project_name}")
            return True
        
        if not monitor_dir:
            monitor_dir = self.setup_monitor_environment()
            if not monitor_dir:
                print("❌ Failed to setup monitor environment")
                return False
        
        session_name = f"{project_name}-monitor"
        
        print(f"🚀 Starting monitor for project: {project_name}")
        
        try:
            # モニターセッション作成
            subprocess.run([
                "tmux", "new-session", "-d", "-s", session_name
            ], check=True)
            
            # ディレクトリ移動
            subprocess.run([
                "tmux", "send-keys", "-t", session_name, 
                f"cd '{monitor_dir}'", "C-m"
            ], check=True)
            
            # 初期メッセージ
            welcome_msg = f"echo '=== Claude Code Monitor - {project_name} ===' && echo 'Starting token usage monitoring...'"
            subprocess.run([
                "tmux", "send-keys", "-t", session_name, 
                welcome_msg, "C-m"
            ], check=True)
            
            # モニター起動
            monitor_cmd = f"python3 claude_code_monitor.py --project '{project_name}' --auto-save"
            subprocess.run([
                "tmux", "send-keys", "-t", session_name, 
                monitor_cmd, "C-m"
            ], check=True)
            
            print(f"✅ Monitor started for project: {project_name}")
            
            # 起動確認のため少し待機
            time.sleep(2)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start monitor: {e}")
            return False
    
    def stop_project_monitor(self, project_name: str) -> bool:
        """プロジェクトモニターを停止"""
        session_name = f"{project_name}-monitor"
        
        if not self.is_monitor_running(project_name):
            print(f"ℹ️  No monitor running for project: {project_name}")
            return True
        
        try:
            print(f"🛑 Stopping monitor for project: {project_name}")
            subprocess.run([
                "tmux", "kill-session", "-t", session_name
            ], check=True)
            
            print(f"✅ Monitor stopped for project: {project_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop monitor: {e}")
            return False
    
    def get_project_token_usage(self, project_name: str) -> Dict:
        """プロジェクトのトークン使用量を取得"""
        # キャッシュから読み込み
        usage_data = self.load_usage_cache()
        
        project_usage = usage_data.get(project_name, {
            "total_tokens": 0,
            "sessions": [],
            "last_updated": None,
            "agents": {
                "ceo": 0,
                "manager": 0, 
                "dev1": 0,
                "dev2": 0,
                "dev3": 0
            }
        })
        
        # モニターセッションからリアルタイムデータを取得を試行
        try:
            realtime_usage = self.fetch_realtime_usage(project_name)
            if realtime_usage:
                project_usage.update(realtime_usage)
        except Exception as e:
            print(f"⚠️  Could not fetch realtime usage: {e}")
        
        return project_usage
    
    def fetch_realtime_usage(self, project_name: str) -> Optional[Dict]:
        """リアルタイムのトークン使用量を取得"""
        session_name = f"{project_name}-monitor"
        
        if not self.is_monitor_running(project_name):
            return None
        
        try:
            # モニターセッションから統計情報を取得（仮想的な実装）
            # 実際の実装では、claude-code-monitorのAPIエンドポイントまたは
            # ログファイルから使用量を読み取る
            
            # セッションの活動状態を確認
            result = subprocess.run([
                "tmux", "display-message", "-t", session_name, "-p", 
                "#{session_name}:#{session_windows}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "active",
                    "last_check": datetime.now().isoformat(),
                    "session_info": result.stdout.strip()
                }
            
        except Exception as e:
            print(f"⚠️  Error fetching realtime usage: {e}")
        
        return None
    
    def load_usage_cache(self) -> Dict:
        """使用量キャッシュを読み込み"""
        try:
            if os.path.exists(self.usage_cache_file):
                with open(self.usage_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading usage cache: {e}")
        
        return {}
    
    def save_usage_cache(self, usage_data: Dict):
        """使用量キャッシュを保存"""
        try:
            with open(self.usage_cache_file, 'w', encoding='utf-8') as f:
                json.dump(usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error saving usage cache: {e}")
    
    def update_project_usage(self, project_name: str, agent_name: str, tokens_used: int):
        """プロジェクトの使用量を更新"""
        usage_data = self.load_usage_cache()
        
        if project_name not in usage_data:
            usage_data[project_name] = {
                "total_tokens": 0,
                "sessions": [],
                "last_updated": None,
                "agents": {
                    "ceo": 0,
                    "manager": 0,
                    "dev1": 0,
                    "dev2": 0,
                    "dev3": 0
                }
            }
        
        # エージェント別使用量更新
        if agent_name in usage_data[project_name]["agents"]:
            usage_data[project_name]["agents"][agent_name] += tokens_used
        
        # 総使用量更新
        usage_data[project_name]["total_tokens"] += tokens_used
        usage_data[project_name]["last_updated"] = datetime.now().isoformat()
        
        # セッション記録
        session_record = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "tokens": tokens_used
        }
        usage_data[project_name]["sessions"].append(session_record)
        
        # 最新100セッションのみ保持
        usage_data[project_name]["sessions"] = usage_data[project_name]["sessions"][-100:]
        
        # キャッシュ保存
        self.save_usage_cache(usage_data)
        
        # 閾値チェック
        self.check_usage_alerts(project_name, usage_data[project_name])
    
    def check_usage_alerts(self, project_name: str, project_usage: Dict):
        """使用量アラートをチェック"""
        total_tokens = project_usage.get("total_tokens", 0)
        
        alert_level = None
        if total_tokens >= self.alert_thresholds["emergency"]:
            alert_level = "emergency"
        elif total_tokens >= self.alert_thresholds["critical"]:
            alert_level = "critical"
        elif total_tokens >= self.alert_thresholds["warning"]:
            alert_level = "warning"
        
        if alert_level:
            self.send_usage_alert(project_name, alert_level, total_tokens)
    
    def send_usage_alert(self, project_name: str, level: str, total_tokens: int):
        """使用量アラートを送信"""
        threshold = self.alert_thresholds[level]
        
        alert_icons = {
            "warning": "⚠️",
            "critical": "🚨", 
            "emergency": "🔥"
        }
        
        icon = alert_icons.get(level, "⚠️")
        
        message = f"""
{icon} TOKEN USAGE ALERT - {level.upper()}

Project: {project_name}
Total Usage: {total_tokens:,} tokens
Threshold: {threshold:,} tokens
Exceeded by: {total_tokens - threshold:,} tokens

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        print(message)
        
        # アラートログに記録
        self.log_alert(project_name, level, total_tokens, message)
    
    def log_alert(self, project_name: str, level: str, tokens: int, message: str):
        """アラートをログファイルに記録"""
        log_file = f"alerts-{project_name}.log"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} | {level.upper()} | {tokens} tokens\n")
                f.write(f"{message}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            print(f"⚠️  Error logging alert: {e}")
    
    def generate_usage_report(self, project_name: str = None) -> str:
        """使用量レポートを生成"""
        usage_data = self.load_usage_cache()
        
        if project_name and project_name in usage_data:
            # 特定プロジェクトのレポート
            return self.generate_project_report(project_name, usage_data[project_name])
        else:
            # 全プロジェクトのレポート
            return self.generate_global_report(usage_data)
    
    def generate_project_report(self, project_name: str, project_data: Dict) -> str:
        """プロジェクト別レポート生成"""
        total_tokens = project_data.get("total_tokens", 0)
        agents = project_data.get("agents", {})
        last_updated = project_data.get("last_updated", "Never")
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    TOKEN USAGE REPORT - {project_name.upper():<31} ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 Total Usage: {total_tokens:,} tokens
🕐 Last Updated: {last_updated[:19] if last_updated != "Never" else "Never"}

👥 Agent Breakdown:
   CEO:     {agents.get('ceo', 0):>8,} tokens
   Manager: {agents.get('manager', 0):>8,} tokens  
   Dev1:    {agents.get('dev1', 0):>8,} tokens
   Dev2:    {agents.get('dev2', 0):>8,} tokens
   Dev3:    {agents.get('dev3', 0):>8,} tokens

🎯 Usage Status:
   Warning Threshold:  {self.alert_thresholds['warning']:>8,} tokens
   Critical Threshold: {self.alert_thresholds['critical']:>8,} tokens
   Emergency Threshold:{self.alert_thresholds['emergency']:>8,} tokens

📈 Status: {self.get_usage_status(total_tokens)}
        """.strip()
        
        return report
    
    def generate_global_report(self, usage_data: Dict) -> str:
        """全プロジェクト統合レポート生成"""
        if not usage_data:
            return "📭 No projects tracked yet"
        
        total_projects = len(usage_data)
        total_global_tokens = sum(proj.get("total_tokens", 0) for proj in usage_data.values())
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          GLOBAL TOKEN USAGE REPORT                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 Overview:
   Total Projects: {total_projects}
   Global Usage:   {total_global_tokens:,} tokens

📋 Project Breakdown:
        """
        
        for project_name, project_data in usage_data.items():
            tokens = project_data.get("total_tokens", 0)
            status = self.get_usage_status(tokens)
            report += f"\n   {project_name:<30} {tokens:>8,} tokens ({status})"
        
        report += f"""

🎯 System Health:
   Projects at Warning+:  {sum(1 for p in usage_data.values() if p.get('total_tokens', 0) >= self.alert_thresholds['warning'])}
   Projects at Critical+: {sum(1 for p in usage_data.values() if p.get('total_tokens', 0) >= self.alert_thresholds['critical'])}
   Projects at Emergency: {sum(1 for p in usage_data.values() if p.get('total_tokens', 0) >= self.alert_thresholds['emergency'])}
        """
        
        return report
    
    def get_usage_status(self, total_tokens: int) -> str:
        """使用量ステータスを取得"""
        if total_tokens >= self.alert_thresholds["emergency"]:
            return "🔥 EMERGENCY"
        elif total_tokens >= self.alert_thresholds["critical"]:
            return "🚨 CRITICAL"
        elif total_tokens >= self.alert_thresholds["warning"]:
            return "⚠️  WARNING"
        else:
            return "✅ NORMAL"

def main():
    """メイン実行関数"""
    import sys
    
    monitor = MonitorIntegration()
    
    if len(sys.argv) < 2:
        print("📖 Usage:")
        print("  python3 monitor-integration.py start <project_name>")
        print("  python3 monitor-integration.py stop <project_name>")
        print("  python3 monitor-integration.py status <project_name>")
        print("  python3 monitor-integration.py report [project_name]")
        print("  python3 monitor-integration.py setup")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        # モニター環境セットアップ
        monitor_dir = monitor.setup_monitor_environment()
        if monitor_dir:
            print(f"✅ Monitor environment ready at: {monitor_dir}")
        else:
            print("❌ Failed to setup monitor environment")
    
    elif command == "start" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        monitor.start_project_monitor(project_name)
    
    elif command == "stop" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        monitor.stop_project_monitor(project_name)
    
    elif command == "status" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        usage = monitor.get_project_token_usage(project_name)
        print(monitor.generate_project_report(project_name, usage))
    
    elif command == "report":
        project_name = sys.argv[2] if len(sys.argv) >= 3 else None
        report = monitor.generate_usage_report(project_name)
        print(report)
    
    else:
        print("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()
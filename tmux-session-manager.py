#!/usr/bin/env python3
"""
tmux Session Manager for Multi-Project Workflow
複数プロジェクト並行運用のためのtmuxセッション管理システム
"""

import subprocess
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional

class TmuxSessionManager:
    def __init__(self, max_projects: int = 4):
        self.max_projects = max_projects
        self.session_config_dir = "session-configs"
        self.state_backup_dir = "session-states"
        self.ensure_directories()
        
    def ensure_directories(self):
        """必要なディレクトリを作成"""
        for directory in [self.session_config_dir, self.state_backup_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def run_tmux_command(self, command: str) -> bool:
        """tmuxコマンドを実行"""
        try:
            result = subprocess.run(command, shell=True, check=True, 
                                  capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ tmux command failed: {command}")
            print(f"Error: {e.stderr}")
            return False
    
    def get_active_sessions(self) -> List[str]:
        """アクティブなtmuxセッション一覧を取得"""
        try:
            result = subprocess.run(["tmux", "list-sessions"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                sessions = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        # セッション名を抽出 (例: "session-name: 1 windows")
                        session_name = line.split(':')[0]
                        sessions.append(session_name)
                return sessions
            return []
        except Exception as e:
            print(f"⚠️ Error getting sessions: {e}")
            return []
    
    def get_project_sessions(self) -> List[Dict]:
        """プロジェクト用セッションの詳細情報を取得"""
        active_sessions = self.get_active_sessions()
        project_sessions = []
        
        for session in active_sessions:
            if session.endswith('-team') or session.endswith('-ceo'):
                # プロジェクト名を抽出
                if session.endswith('-team'):
                    project_name = session[:-5]  # "-team"を除去
                elif session.endswith('-ceo'):
                    project_name = session[:-4]   # "-ceo"を除去
                else:
                    continue
                
                # 既存のプロジェクトかチェック
                existing = next((p for p in project_sessions if p["project_name"] == project_name), None)
                if not existing:
                    project_info = self.get_project_info(project_name)
                    project_sessions.append(project_info)
        
        return project_sessions
    
    def get_project_info(self, project_name: str) -> Dict:
        """プロジェクトの詳細情報を取得"""
        team_session = f"{project_name}-team"
        ceo_session = f"{project_name}-ceo"
        monitor_session = f"{project_name}-monitor"
        
        active_sessions = self.get_active_sessions()
        
        info = {
            "project_name": project_name,
            "team_session": team_session if team_session in active_sessions else None,
            "ceo_session": ceo_session if ceo_session in active_sessions else None,
            "monitor_session": monitor_session if monitor_session in active_sessions else None,
            "agent_count": 0,
            "status": "inactive"
        }
        
        # アクティブなセッション数をカウント
        if info["team_session"] and info["ceo_session"]:
            info["agent_count"] = 5  # Manager + Dev1,2,3 + CEO
            info["status"] = "active"
        elif info["team_session"] or info["ceo_session"]:
            info["agent_count"] = 4 if info["team_session"] else 1
            info["status"] = "partial"
        
        return info
    
    def create_project_session(self, project_name: str, repository_path: str = None) -> bool:
        """新しいプロジェクト用セッションを作成"""
        if len(self.get_project_sessions()) >= self.max_projects:
            print(f"❌ Maximum {self.max_projects} projects already active")
            return False
        
        print(f"🚀 Creating project session: {project_name}")
        
        # セッション名を定義
        team_session = f"{project_name}-team"
        ceo_session = f"{project_name}-ceo"
        
        # 既存セッションをチェック
        active_sessions = self.get_active_sessions()
        if team_session in active_sessions or ceo_session in active_sessions:
            print(f"⚠️ Project '{project_name}' already has active sessions")
            return False
        
        try:
            # 1. CEOセッション作成
            success = self.create_ceo_session(ceo_session, repository_path)
            if not success:
                return False
            
            # 2. チームセッション作成（4分割）
            success = self.create_team_session(team_session, repository_path)
            if not success:
                # CEOセッションも削除
                self.run_tmux_command(f"tmux kill-session -t {ceo_session}")
                return False
            
            # 3. エージェント起動
            success = self.start_agents(project_name, repository_path)
            if not success:
                # 両セッションを削除
                self.run_tmux_command(f"tmux kill-session -t {ceo_session}")
                self.run_tmux_command(f"tmux kill-session -t {team_session}")
                return False
            
            print(f"✅ Project session '{project_name}' created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating project session: {e}")
            return False
    
    def create_ceo_session(self, session_name: str, repository_path: str = None) -> bool:
        """CEOセッションを作成"""
        print(f"💼 Creating CEO session: {session_name}")
        
        # CEOセッション作成
        if not self.run_tmux_command(f"tmux new-session -d -s {session_name}"):
            return False
        
        # ディレクトリ移動
        if repository_path:
            if not self.run_tmux_command(f"tmux send-keys -t {session_name} 'cd {repository_path}' C-m"):
                return False
        
        # CEOの初期メッセージ
        welcome_msg = "echo '=== CEO (最高経営責任者) ===' && echo 'プロジェクト依頼をお待ちしています...'"
        if not self.run_tmux_command(f"tmux send-keys -t {session_name} \"{welcome_msg}\" C-m"):
            return False
        
        return True
    
    def create_team_session(self, session_name: str, repository_path: str = None) -> bool:
        """チームセッション（4分割）を作成"""
        print(f"👥 Creating team session: {session_name}")
        
        # メインセッション作成
        if not self.run_tmux_command(f"tmux new-session -d -s {session_name}"):
            return False
        
        # 2x2のグリッド作成
        split_commands = [
            f"tmux split-window -h -t {session_name}",      # 縦分割
            f"tmux split-window -v -t {session_name}:0.0",  # 左上を横分割
            f"tmux split-window -v -t {session_name}:0.1"   # 右上を横分割
        ]
        
        for cmd in split_commands:
            if not self.run_tmux_command(cmd):
                return False
            time.sleep(0.1)  # 分割間に小さな遅延
        
        # 各ペインにディレクトリ移動
        if repository_path:
            for pane in ["0.0", "0.1", "0.2", "0.3"]:
                cmd = f"tmux send-keys -t {session_name}:{pane} 'cd {repository_path}' C-m"
                if not self.run_tmux_command(cmd):
                    return False
        
        return True
    
    def start_agents(self, project_name: str, repository_path: str = None) -> bool:
        """各ペインでエージェントを起動"""
        print(f"🤖 Starting agents for project: {project_name}")
        
        team_session = f"{project_name}-team"
        ceo_session = f"{project_name}-ceo"
        
        # エージェント設定
        agents = [
            {"pane": "0.0", "name": "Manager", "file": "instructions/manager.md"},
            {"pane": "0.1", "name": "Dev1", "file": "instructions/developer.md"},
            {"pane": "0.2", "name": "Dev2", "file": "instructions/developer.md"},
            {"pane": "0.3", "name": "Dev3", "file": "instructions/developer.md"}
        ]
        
        # チームエージェント起動
        for agent in agents:
            # 初期メッセージ
            welcome_msg = f"echo '=== {agent['name']} ===' && echo 'Manager指示をお待ちしています...'"
            if not self.run_tmux_command(f"tmux send-keys -t {team_session}:{agent['pane']} \"{welcome_msg}\" C-m"):
                return False
            
            # Claude起動
            claude_cmd = f"claude {agent['file']}"
            if not self.run_tmux_command(f"tmux send-keys -t {team_session}:{agent['pane']} '{claude_cmd}' C-m"):
                return False
            
            time.sleep(0.5)  # エージェント間の起動間隔
        
        # CEO起動
        claude_cmd = "claude instructions/ceo.md"
        if not self.run_tmux_command(f"tmux send-keys -t {ceo_session} '{claude_cmd}' C-m"):
            return False
        
        print(f"✅ All agents started for project: {project_name}")
        return True
    
    def switch_to_project(self, project_name: str) -> bool:
        """プロジェクトにフォーカスを切り替え"""
        project_sessions = self.get_project_sessions()
        target_project = next((p for p in project_sessions if p["project_name"] == project_name), None)
        
        if not target_project:
            print(f"❌ Project '{project_name}' not found")
            return False
        
        if target_project["status"] != "active":
            print(f"⚠️ Project '{project_name}' is not fully active")
            return False
        
        print(f"🔄 Switching to project: {project_name}")
        
        # チームセッションにアタッチ
        team_session = f"{project_name}-team"
        if not self.run_tmux_command(f"tmux attach-session -t {team_session}"):
            print(f"❌ Failed to attach to {team_session}")
            return False
        
        return True
    
    def save_project_state(self, project_name: str) -> bool:
        """プロジェクトの現在状態を保存"""
        print(f"💾 Saving state for project: {project_name}")
        
        state_file = os.path.join(self.state_backup_dir, f"{project_name}-state.json")
        
        project_info = self.get_project_info(project_name)
        state_data = {
            "project_name": project_name,
            "saved_at": datetime.now().isoformat(),
            "project_info": project_info,
            "sessions": {}
        }
        
        # 各セッションの状態を保存
        for session_type in ["team_session", "ceo_session", "monitor_session"]:
            session_name = project_info.get(session_type)
            if session_name:
                session_state = self.capture_session_state(session_name)
                state_data["sessions"][session_type] = session_state
        
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            print(f"✅ State saved to: {state_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving state: {e}")
            return False
    
    def capture_session_state(self, session_name: str) -> Dict:
        """セッションの現在状態をキャプチャ"""
        try:
            # セッション情報を取得
            cmd = f"tmux display-message -t {session_name} -p '#{{session_name}}:#{{window_index}}.#{{pane_index}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            state = {
                "session_name": session_name,
                "captured_at": datetime.now().isoformat(),
                "active": result.returncode == 0,
                "pane_info": result.stdout.strip() if result.returncode == 0 else None
            }
            
            return state
        except Exception as e:
            print(f"⚠️ Error capturing session state: {e}")
            return {"session_name": session_name, "active": False, "error": str(e)}
    
    def list_projects(self):
        """アクティブなプロジェクト一覧を表示"""
        projects = self.get_project_sessions()
        
        print("\n" + "="*80)
        print("🚀 ACTIVE MULTI-AGENT PROJECTS")
        print("="*80)
        
        if not projects:
            print("📭 No active projects found")
            return
        
        for i, project in enumerate(projects, 1):
            status_icon = "🟢" if project["status"] == "active" else "🟡" if project["status"] == "partial" else "🔴"
            print(f"\n[{i}] {status_icon} {project['project_name']}")
            print(f"    📊 Status: {project['status']} | 👥 Agents: {project['agent_count']}")
            
            if project["team_session"]:
                print(f"    🏢 Team: {project['team_session']}")
            if project["ceo_session"]:
                print(f"    💼 CEO: {project['ceo_session']}")
            if project["monitor_session"]:
                print(f"    📈 Monitor: {project['monitor_session']}")
        
        print("\n" + "="*80)
        print(f"📈 Total Projects: {len(projects)}/{self.max_projects}")
        print("="*80)
    
    def cleanup_project(self, project_name: str) -> bool:
        """プロジェクトセッションを完全にクリーンアップ"""
        print(f"🧹 Cleaning up project: {project_name}")
        
        # 状態を保存
        self.save_project_state(project_name)
        
        # セッションを削除
        sessions_to_kill = [
            f"{project_name}-team",
            f"{project_name}-ceo", 
            f"{project_name}-monitor"
        ]
        
        success = True
        for session in sessions_to_kill:
            if session in self.get_active_sessions():
                if not self.run_tmux_command(f"tmux kill-session -t {session}"):
                    success = False
                    print(f"⚠️ Failed to kill session: {session}")
                else:
                    print(f"✅ Killed session: {session}")
        
        return success

def main():
    """メイン実行関数"""
    import sys
    
    manager = TmuxSessionManager()
    
    if len(sys.argv) < 2:
        print("📋 Usage:")
        print("  python3 tmux-session-manager.py list")
        print("  python3 tmux-session-manager.py create <project_name> [repository_path]")
        print("  python3 tmux-session-manager.py switch <project_name>")
        print("  python3 tmux-session-manager.py cleanup <project_name>")
        print("  python3 tmux-session-manager.py save <project_name>")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        manager.list_projects()
    
    elif command == "create" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        repository_path = sys.argv[3] if len(sys.argv) > 3 else None
        manager.create_project_session(project_name, repository_path)
    
    elif command == "switch" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        manager.switch_to_project(project_name)
    
    elif command == "cleanup" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        manager.cleanup_project(project_name)
    
    elif command == "save" and len(sys.argv) >= 3:
        project_name = sys.argv[2]
        manager.save_project_state(project_name)
    
    else:
        print("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()
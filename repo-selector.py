#!/usr/bin/env python3
"""
GitHub Repository Selector
GitHub CLIを使用した効率的なリポジトリ選択システム
"""

import subprocess
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional

class GitHubRepoSelector:
    def __init__(self, cache_file="recent-projects-cache.json"):
        self.cache_file = cache_file
        self.recent_projects = self.load_recent_projects()
        
    def load_recent_projects(self) -> Dict:
        """最近使用したプロジェクトのキャッシュを読み込み"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Cache load error: {e}")
        
        return {"recent": [], "favorites": []}
    
    def save_recent_projects(self):
        """最近使用したプロジェクトをキャッシュに保存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_projects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Cache save error: {e}")
    
    def get_repositories(self, limit: int = 20) -> List[Dict]:
        """GitHub CLIを使用してリポジトリ一覧を取得"""
        try:
            print("🔍 Fetching repositories from GitHub...")
            cmd = ["gh", "repo", "list", "--limit", str(limit)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            repositories = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    repo_data = self.parse_repo_line(line)
                    if repo_data:
                        repositories.append(repo_data)
            
            print(f"✅ Found {len(repositories)} repositories")
            return repositories
            
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub CLI error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
    
    def parse_repo_line(self, line: str) -> Optional[Dict]:
        """GitHub CLIの出力行を解析してリポジトリ情報を抽出"""
        try:
            # gh repo list の出力形式: "owner/name description visibility updated_at"
            parts = line.split('\t')
            if len(parts) >= 3:
                return {
                    "full_name": parts[0],
                    "name": parts[0].split('/')[-1],
                    "description": parts[1] if parts[1] else "No description",
                    "visibility": parts[2] if len(parts) > 2 else "unknown",
                    "updated_at": parts[3] if len(parts) > 3 else "unknown"
                }
        except Exception as e:
            print(f"⚠️ Parse error for line: {line[:50]}... - {e}")
        
        return None
    
    def categorize_repositories(self, repositories: List[Dict]) -> Dict[str, List[Dict]]:
        """リポジトリをカテゴリ別に分類"""
        categories = {
            "analysis": [],      # データ解析
            "infrastructure": [], # インフラ・システム  
            "research": [],      # 研究プロジェクト
            "tools": [],         # 開発ツール
            "monitoring": [],    # 監視システム
            "other": []          # その他
        }
        
        for repo in repositories:
            category = self.classify_repository(repo)
            categories[category].append(repo)
        
        return categories
    
    def classify_repository(self, repo: Dict) -> str:
        """リポジトリを分類するロジック"""
        name = repo["name"].lower()
        description = repo["description"].lower()
        
        # 分析関連キーワード
        if any(keyword in name or keyword in description for keyword in 
               ["analysis", "neuroscience", "data", "experiment", "matlab", "med-pc"]):
            return "analysis"
        
        # インフラ関連キーワード
        if any(keyword in name or keyword in description for keyword in 
               ["tmux", "multiagent", "system", "infrastructure", "automation"]):
            return "infrastructure"
        
        # 研究関連キーワード
        if any(keyword in name or keyword in description for keyword in 
               ["research", "academic", "tf", "fiber", "dn001"]):
            return "research"
        
        # ツール関連キーワード
        if any(keyword in name or keyword in description for keyword in 
               ["tool", "utility", "helper", "manager", "wd1"]):
            return "tools"
        
        # 監視関連キーワード
        if any(keyword in name or keyword in description for keyword in 
               ["monitor", "tracking", "usage", "claude-code"]):
            return "monitoring"
        
        return "other"
    
    def add_to_recent(self, repo_name: str):
        """リポジトリを最近使用したリストに追加"""
        # 既存のエントリを削除（重複防止）
        self.recent_projects["recent"] = [
            r for r in self.recent_projects["recent"] if r["name"] != repo_name
        ]
        
        # 新しいエントリを先頭に追加
        entry = {
            "name": repo_name,
            "last_used": datetime.now().isoformat(),
            "usage_count": self.get_usage_count(repo_name) + 1
        }
        self.recent_projects["recent"].insert(0, entry)
        
        # 最新10件のみ保持
        self.recent_projects["recent"] = self.recent_projects["recent"][:10]
        
        self.save_recent_projects()
    
    def get_usage_count(self, repo_name: str) -> int:
        """リポジトリの使用回数を取得"""
        for entry in self.recent_projects["recent"]:
            if entry["name"] == repo_name:
                return entry.get("usage_count", 0)
        return 0
    
    def display_repositories(self, repositories: List[Dict], show_recent: bool = True):
        """リポジトリ一覧を見やすく表示"""
        print("\n" + "="*80)
        print("🚀 GITHUB REPOSITORY SELECTOR")
        print("="*80)
        
        # 最近使用したプロジェクトを優先表示
        if show_recent and self.recent_projects["recent"]:
            print("\n📚 RECENT PROJECTS:")
            print("-" * 50)
            for i, recent in enumerate(self.recent_projects["recent"][:5], 1):
                # 対応するリポジトリ情報を検索
                repo_info = None
                for repo in repositories:
                    if repo["name"] == recent["name"]:
                        repo_info = repo
                        break
                
                if repo_info:
                    print(f"[R{i}] {repo_info['name']}")
                    print(f"     {repo_info['description'][:60]}...")
                    print(f"     👥 Used {recent['usage_count']} times | 🕐 {recent['last_used'][:10]}")
                    print()
        
        # カテゴリ別表示
        categorized = self.categorize_repositories(repositories)
        
        display_order = ["analysis", "infrastructure", "research", "tools", "monitoring", "other"]
        category_icons = {
            "analysis": "🧠",
            "infrastructure": "🏗️", 
            "research": "🔬",
            "tools": "🛠️",
            "monitoring": "📊",
            "other": "📁"
        }
        
        item_number = 1
        selection_map = {}
        
        for category in display_order:
            repos = categorized[category]
            if repos:
                print(f"\n{category_icons[category]} {category.upper()} PROJECTS:")
                print("-" * 50)
                
                for repo in repos:
                    selection_map[item_number] = repo
                    print(f"[{item_number}] {repo['name']}")
                    print(f"     {repo['description'][:60]}...")
                    print(f"     🔒 {repo['visibility']} | 📅 {repo['updated_at'][:10]}")
                    print()
                    item_number += 1
        
        return selection_map
    
    def interactive_selection(self) -> Optional[Dict]:
        """インタラクティブなリポジトリ選択"""
        repositories = self.get_repositories()
        if not repositories:
            print("❌ No repositories found")
            return None
        
        selection_map = self.display_repositories(repositories)
        
        print("\n" + "="*80)
        print("📋 SELECTION OPTIONS:")
        print("   - Enter number [1-N] to select repository")
        print("   - Enter 'R1-R5' to select recent project")
        print("   - Enter 'q' to quit")
        print("   - Enter 'refresh' to reload repositories")
        print("="*80)
        
        while True:
            try:
                user_input = input("\n🎯 Select repository: ").strip()
                
                if user_input.lower() == 'q':
                    print("👋 Exiting...")
                    return None
                
                if user_input.lower() == 'refresh':
                    print("🔄 Refreshing repository list...")
                    return self.interactive_selection()
                
                # Recent project selection (R1-R5)
                if user_input.upper().startswith('R'):
                    try:
                        recent_index = int(user_input[1:]) - 1
                        if 0 <= recent_index < len(self.recent_projects["recent"]):
                            recent_name = self.recent_projects["recent"][recent_index]["name"]
                            # Find full repo info
                            for repo in repositories:
                                if repo["name"] == recent_name:
                                    print(f"✅ Selected recent project: {repo['name']}")
                                    self.add_to_recent(repo["name"])
                                    return repo
                            print(f"❌ Recent project '{recent_name}' not found in current list")
                        else:
                            print("❌ Invalid recent project number")
                    except ValueError:
                        print("❌ Invalid recent project format")
                    continue
                
                # Regular number selection
                selection_num = int(user_input)
                if selection_num in selection_map:
                    selected_repo = selection_map[selection_num]
                    print(f"✅ Selected: {selected_repo['name']}")
                    self.add_to_recent(selected_repo["name"])
                    return selected_repo
                else:
                    print(f"❌ Invalid selection: {selection_num}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                return None
    
    def quick_select_by_name(self, repo_name: str) -> Optional[Dict]:
        """名前によるクイック選択"""
        repositories = self.get_repositories()
        
        for repo in repositories:
            if repo["name"] == repo_name or repo["full_name"] == repo_name:
                print(f"✅ Quick selected: {repo['name']}")
                self.add_to_recent(repo["name"])
                return repo
        
        print(f"❌ Repository '{repo_name}' not found")
        return None

def main():
    """メイン実行関数"""
    import sys
    
    selector = GitHubRepoSelector()
    
    # コマンドライン引数での指定
    if len(sys.argv) > 1:
        repo_name = sys.argv[1]
        selected = selector.quick_select_by_name(repo_name)
    else:
        # インタラクティブ選択
        selected = selector.interactive_selection()
    
    if selected:
        print("\n" + "="*80)
        print("🎉 REPOSITORY SELECTED")
        print("="*80)
        print(f"Name: {selected['name']}")
        print(f"Full Name: {selected['full_name']}")
        print(f"Description: {selected['description']}")
        print(f"Visibility: {selected['visibility']}")
        print(f"Last Updated: {selected['updated_at']}")
        print("="*80)
        
        # 選択されたリポジトリ情報をJSONで出力（他のスクリプトから利用可能）
        output = {
            "selected_repository": selected,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("selected-repository.json", "w", encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print("📁 Repository info saved to: selected-repository.json")
        return selected
    
    return None

if __name__ == "__main__":
    main()
#!/bin/bash

# ユーザーワークフロー自動化システム - メイン起動スクリプト
# GitHub CLI → tmux → リポジトリ選択 → チーム作業の完全自動化

set -e  # エラー時に停止

# 色付きテキストの定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX_PARALLEL_PROJECTS=4
CLAUDE_CODE_MONITOR_REPO="NSada2025/claude-code-monitor"

# 起動バナー表示
show_banner() {
    echo -e "${PURPLE}"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "🚀 WORKFLOW AUTOMATION SYSTEM"
    echo "   GitHub CLI → tmux → Repository Selection → Multi-Agent Team Work"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# システム前提条件チェック
check_prerequisites() {
    log_header "🔍 CHECKING SYSTEM PREREQUISITES"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    local missing_deps=0
    
    # GitHub CLI チェック
    if command -v gh &> /dev/null; then
        log_success "GitHub CLI is installed"
    else
        log_error "GitHub CLI is not installed"
        missing_deps=$((missing_deps + 1))
    fi
    
    # tmux チェック
    if command -v tmux &> /dev/null; then
        log_success "tmux is installed"
    else
        log_error "tmux is not installed" 
        missing_deps=$((missing_deps + 1))
    fi
    
    # Python チェック
    if command -v python3 &> /dev/null; then
        log_success "Python 3 is installed"
    else
        log_error "Python 3 is not installed"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Claude Code チェック
    if command -v claude &> /dev/null; then
        log_success "Claude Code CLI is installed"
    else
        log_error "Claude Code CLI is not installed"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Git チェック
    if command -v git &> /dev/null; then
        log_success "Git is installed"
    else
        log_error "Git is not installed"
        missing_deps=$((missing_deps + 1))
    fi
    
    if [ $missing_deps -gt 0 ]; then
        log_error "Missing $missing_deps required dependencies"
        echo "Please install missing tools and try again"
        exit 1
    fi
    
    log_success "All prerequisites satisfied"
    echo ""
}

# GitHub認証状態チェック
check_github_auth() {
    log_info "Checking GitHub authentication..."
    
    if gh auth status &> /dev/null; then
        log_success "GitHub authentication is valid"
    else
        log_warning "GitHub authentication required"
        echo "Please run: gh auth login"
        exit 1
    fi
}

# アクティブプロジェクト一覧表示
show_active_projects() {
    log_header "📊 ACTIVE MULTI-AGENT PROJECTS"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    python3 "${SCRIPT_DIR}/tmux-session-manager.py" list
    echo ""
}

# リポジトリ選択
select_repository() {
    local repo_name="$1"
    
    if [ -n "$repo_name" ]; then
        # コマンドライン引数で指定された場合
        log_info "Quick selecting repository: $repo_name"
        python3 "${SCRIPT_DIR}/repo-selector.py" "$repo_name"
    else
        # インタラクティブ選択
        log_header "🔍 REPOSITORY SELECTION"
        echo "────────────────────────────────────────────────────────────────────────────────"
        python3 "${SCRIPT_DIR}/repo-selector.py"
    fi
    
    # 選択結果を確認
    if [ ! -f "selected-repository.json" ]; then
        log_error "No repository selected"
        return 1
    fi
    
    return 0
}

# claude-code-monitor起動
start_monitor() {
    local project_name="$1"
    
    log_info "Starting claude-code-monitor for project: $project_name"
    
    # claude-code-monitorリポジトリの場所を確認
    local monitor_paths=(
        "../claude-code-monitor"
        "../../claude-code-monitor"
        "$HOME/claude-code-monitor"
        "/tmp/claude-code-monitor"
    )
    
    local monitor_dir=""
    for path in "${monitor_paths[@]}"; do
        if [ -d "$path" ]; then
            monitor_dir="$path"
            break
        fi
    done
    
    if [ -z "$monitor_dir" ]; then
        log_warning "claude-code-monitor repository not found locally"
        log_info "Cloning claude-code-monitor..."
        
        if gh repo clone "$CLAUDE_CODE_MONITOR_REPO" "/tmp/claude-code-monitor"; then
            monitor_dir="/tmp/claude-code-monitor"
            log_success "claude-code-monitor cloned to $monitor_dir"
        else
            log_warning "Failed to clone claude-code-monitor, continuing without monitoring"
            return 1
        fi
    fi
    
    # モニターセッション作成
    local monitor_session="${project_name}-monitor"
    
    if tmux has-session -t "$monitor_session" 2>/dev/null; then
        log_info "Monitor session already exists: $monitor_session"
    else
        log_info "Creating monitor session: $monitor_session"
        tmux new-session -d -s "$monitor_session"
        tmux send-keys -t "$monitor_session" "cd '$monitor_dir'" C-m
        tmux send-keys -t "$monitor_session" "echo '=== Claude Code Monitor - $project_name ===' && echo 'Starting token usage monitoring...'" C-m
        
        # モニター起動（プロジェクト名をタグとして使用）
        tmux send-keys -t "$monitor_session" "python3 claude_code_monitor.py --project '$project_name'" C-m
        
        log_success "Monitor started for project: $project_name"
    fi
    
    return 0
}

# プロジェクトセッション作成
create_project_session() {
    local selected_repo_file="selected-repository.json"
    
    if [ ! -f "$selected_repo_file" ]; then
        log_error "Repository selection file not found"
        return 1
    fi
    
    # 選択されたリポジトリ情報を取得
    local repo_name
    local repo_full_name
    repo_name=$(python3 -c "import json; data=json.load(open('$selected_repo_file')); print(data['selected_repository']['name'])")
    repo_full_name=$(python3 -c "import json; data=json.load(open('$selected_repo_file')); print(data['selected_repository']['full_name'])")
    
    if [ -z "$repo_name" ]; then
        log_error "Could not extract repository name"
        return 1
    fi
    
    log_header "🚀 STARTING PROJECT: $repo_name"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    # リポジトリクローン/ディレクトリ移動の準備
    local project_dir="/tmp/workflow-projects/$repo_name"
    local current_dir="$(pwd)"
    
    # プロジェクトディレクトリ確認
    if [ "$repo_full_name" = "$(basename "$current_dir")" ] || [ "$repo_name" = "$(basename "$current_dir")" ]; then
        # 現在のディレクトリが選択されたリポジトリ
        project_dir="$current_dir"
        log_info "Using current directory: $project_dir"
    elif [ -d "$project_dir" ]; then
        log_info "Using existing project directory: $project_dir"
    else
        # リポジトリをクローン
        log_info "Cloning repository: $repo_full_name"
        mkdir -p "$(dirname "$project_dir")"
        
        if gh repo clone "$repo_full_name" "$project_dir"; then
            log_success "Repository cloned to: $project_dir"
        else
            log_error "Failed to clone repository"
            return 1
        fi
    fi
    
    # claude-code-monitor起動
    start_monitor "$repo_name"
    
    # tmuxセッション作成
    log_info "Creating multi-agent tmux session..."
    if python3 "${SCRIPT_DIR}/tmux-session-manager.py" create "$repo_name" "$project_dir"; then
        log_success "Multi-agent session created for: $repo_name"
    else
        log_error "Failed to create multi-agent session"
        return 1
    fi
    
    # セッションに接続
    log_success "Project setup complete!"
    echo ""
    log_info "To connect to the team session:"
    echo -e "${YELLOW}  tmux attach-session -t ${repo_name}-team${NC}"
    echo ""
    log_info "To connect to the CEO session:"
    echo -e "${YELLOW}  tmux attach-session -t ${repo_name}-ceo${NC}"
    echo ""
    log_info "To view the monitoring dashboard:"
    echo -e "${YELLOW}  tmux attach-session -t ${repo_name}-monitor${NC}"
    
    return 0
}

# プロジェクト切り替え
switch_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        log_error "Project name required for switching"
        return 1
    fi
    
    log_header "🔄 SWITCHING TO PROJECT: $project_name"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    if python3 "${SCRIPT_DIR}/tmux-session-manager.py" switch "$project_name"; then
        log_success "Switched to project: $project_name"
    else
        log_error "Failed to switch to project: $project_name"
        return 1
    fi
}

# 並行実行管理
manage_parallel_execution() {
    log_header "⚡ PARALLEL EXECUTION MANAGER"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    # 現在のアクティブプロジェクト数をチェック
    local active_count
    active_count=$(python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from tmux_session_manager import TmuxSessionManager
manager = TmuxSessionManager()
projects = manager.get_project_sessions()
active_projects = [p for p in projects if p['status'] == 'active']
print(len(active_projects))
")
    
    log_info "Current active projects: $active_count/$MAX_PARALLEL_PROJECTS"
    
    if [ "$active_count" -ge "$MAX_PARALLEL_PROJECTS" ]; then
        log_warning "Maximum parallel projects reached ($MAX_PARALLEL_PROJECTS)"
        echo "Consider cleaning up some projects before starting new ones:"
        echo ""
        show_active_projects
        echo ""
        echo "To cleanup a project:"
        echo -e "${YELLOW}  $0 cleanup <project_name>${NC}"
        return 1
    fi
    
    log_success "Capacity available for new projects"
    return 0
}

# プロジェクトクリーンアップ
cleanup_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        log_error "Project name required for cleanup"
        return 1
    fi
    
    log_header "🧹 CLEANING UP PROJECT: $project_name"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    if python3 "${SCRIPT_DIR}/tmux-session-manager.py" cleanup "$project_name"; then
        log_success "Project cleaned up: $project_name"
    else
        log_error "Failed to cleanup project: $project_name"
        return 1
    fi
}

# ヘルプ表示
show_help() {
    echo "📖 WORKFLOW AUTOMATION SYSTEM - USAGE"
    echo "────────────────────────────────────────────────────────────────────────────────"
    echo ""
    echo "🚀 Start new project (interactive):"
    echo "   $0"
    echo ""
    echo "🚀 Start specific repository:"
    echo "   $0 start <repository_name>"
    echo ""
    echo "📊 List active projects:"
    echo "   $0 list"
    echo ""
    echo "🔄 Switch to project:"
    echo "   $0 switch <project_name>"
    echo ""
    echo "⚡ Enable parallel execution mode:"
    echo "   $0 --parallel"
    echo ""
    echo "🧹 Cleanup project:"
    echo "   $0 cleanup <project_name>"
    echo ""
    echo "💾 Save project state:"
    echo "   $0 save <project_name>"
    echo ""
    echo "🔍 Select repository only:"
    echo "   $0 select [repository_name]"
    echo ""
    echo "❓ Show this help:"
    echo "   $0 help"
    echo ""
}

# メイン実行ロジック
main() {
    local command="$1"
    local arg1="$2"
    local parallel_mode=false
    
    # パラレルモードフラグの処理
    if [ "$1" = "--parallel" ]; then
        parallel_mode=true
        command="$2"
        arg1="$3"
    fi
    
    # バナー表示
    show_banner
    
    # 前提条件チェック
    check_prerequisites
    check_github_auth
    
    # コマンド処理
    case "$command" in
        ""|"start")
            if [ "$parallel_mode" = true ]; then
                manage_parallel_execution || exit 1
            fi
            
            # リポジトリ選択
            if ! select_repository "$arg1"; then
                exit 1
            fi
            
            # プロジェクトセッション作成
            if ! create_project_session; then
                exit 1
            fi
            ;;
            
        "list")
            show_active_projects
            ;;
            
        "switch")
            if [ -z "$arg1" ]; then
                log_error "Project name required"
                show_help
                exit 1
            fi
            switch_project "$arg1"
            ;;
            
        "cleanup")
            if [ -z "$arg1" ]; then
                log_error "Project name required"
                show_help
                exit 1
            fi
            cleanup_project "$arg1"
            ;;
            
        "save")
            if [ -z "$arg1" ]; then
                log_error "Project name required"
                show_help
                exit 1
            fi
            python3 "${SCRIPT_DIR}/tmux-session-manager.py" save "$arg1"
            ;;
            
        "select")
            select_repository "$arg1"
            ;;
            
        "help"|"-h"|"--help")
            show_help
            ;;
            
        *)
            log_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"
#!/usr/bin/env python3
"""
Progress State Saver
作業進捗と重要情報の自動保存システム
"""

import os
import json
import time
import pickle
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class ProgressStateSaver:
    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.state_dir = f"progress-states/{project_name}"
        self.checkpoint_dir = f"{self.state_dir}/checkpoints"
        self.results_dir = f"{self.state_dir}/results"
        self.logs_dir = f"{self.state_dir}/logs"
        self.ensure_directories()
        
        # 現在の状態
        self.current_state = {
            "project": project_name,
            "started_at": datetime.now().isoformat(),
            "checkpoints": [],
            "results": {},
            "logs": [],
            "metrics": {},
            "last_updated": datetime.now().isoformat()
        }
        
        # 自動保存設定
        self.auto_save_interval = 300  # 5分ごと
        self.last_auto_save = time.time()
        
    def ensure_directories(self):
        """必要なディレクトリを作成"""
        for directory in [self.state_dir, self.checkpoint_dir, 
                         self.results_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def create_checkpoint(self, name: str, data: Any, description: str = "") -> str:
        """作業のチェックポイントを作成"""
        checkpoint_id = self.generate_checkpoint_id(name)
        checkpoint_data = {
            "id": checkpoint_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "data_type": type(data).__name__,
            "data_size": self.get_data_size(data)
        }
        
        # データを保存
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.pkl")
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(data, f)
        
        # メタデータを保存
        meta_file = os.path.join(self.checkpoint_dir, f"{checkpoint_id}_meta.json")
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # 状態に記録
        self.current_state["checkpoints"].append(checkpoint_data)
        self.auto_save_if_needed()
        
        print(f"✅ Checkpoint created: {name} (ID: {checkpoint_id})")
        return checkpoint_id
    
    def save_test_results(self, test_name: str, results: Dict) -> str:
        """テスト結果を保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        # 結果にメタデータを追加
        full_results = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "summary": self.generate_test_summary(results),
            "results": results
        }
        
        # ファイルに保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, indent=2)
        
        # 状態に記録
        self.current_state["results"][test_name] = {
            "file": filename,
            "timestamp": datetime.now().isoformat(),
            "summary": full_results["summary"]
        }
        
        self.auto_save_if_needed()
        
        print(f"📁 Test results saved: {filename}")
        return filepath
    
    def save_error_log(self, error_type: str, error_data: Any, context: Dict = None):
        """エラーログを保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"error_{error_type}_{timestamp}.json"
        filepath = os.path.join(self.logs_dir, filename)
        
        # エラー情報を構造化
        error_info = {
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "error_data": str(error_data),
            "context": context or {},
            "stack_trace": self.get_stack_trace()
        }
        
        # ファイルに保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2)
        
        # 状態に記録
        self.current_state["logs"].append({
            "type": "error",
            "file": filename,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type
        })
        
        self.auto_save_if_needed()
        
        print(f"🚨 Error log saved: {filename}")
        return filepath
    
    def update_metrics(self, metric_name: str, value: Any):
        """メトリクスを更新"""
        if metric_name not in self.current_state["metrics"]:
            self.current_state["metrics"][metric_name] = {
                "values": [],
                "last_value": None,
                "min": None,
                "max": None,
                "count": 0
            }
        
        metric = self.current_state["metrics"][metric_name]
        metric["values"].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
        metric["last_value"] = value
        metric["count"] += 1
        
        # 数値の場合は統計を更新
        if isinstance(value, (int, float)):
            if metric["min"] is None or value < metric["min"]:
                metric["min"] = value
            if metric["max"] is None or value > metric["max"]:
                metric["max"] = value
        
        # 最新100件のみ保持
        if len(metric["values"]) > 100:
            metric["values"] = metric["values"][-100:]
        
        self.auto_save_if_needed()
    
    def save_progress_snapshot(self, stage_name: str, progress_data: Dict):
        """進捗スナップショットを保存"""
        snapshot = {
            "stage": stage_name,
            "timestamp": datetime.now().isoformat(),
            "progress": progress_data,
            "metrics_snapshot": self.get_metrics_summary()
        }
        
        # スナップショットファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{stage_name}_{timestamp}.json"
        filepath = os.path.join(self.state_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"📸 Progress snapshot saved: {stage_name}")
        return filepath
    
    def generate_checkpoint_id(self, name: str) -> str:
        """チェックポイントIDを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"cp_{timestamp}_{name_hash}"
    
    def get_data_size(self, data: Any) -> int:
        """データサイズを取得（バイト）"""
        try:
            import sys
            return sys.getsizeof(data)
        except:
            return -1
    
    def generate_test_summary(self, results: Dict) -> Dict:
        """テスト結果の要約を生成"""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # 結果から統計を抽出（実装は結果の形式に依存）
        if isinstance(results, dict):
            summary["total_tests"] = results.get("total", 0)
            summary["passed"] = results.get("passed", 0)
            summary["failed"] = results.get("failed", 0)
            summary["errors"] = results.get("errors", 0)
            summary["skipped"] = results.get("skipped", 0)
        
        return summary
    
    def get_stack_trace(self) -> str:
        """スタックトレースを取得"""
        import traceback
        return traceback.format_exc()
    
    def get_metrics_summary(self) -> Dict:
        """メトリクスの要約を取得"""
        summary = {}
        
        for name, metric in self.current_state["metrics"].items():
            summary[name] = {
                "last_value": metric["last_value"],
                "count": metric["count"],
                "min": metric.get("min"),
                "max": metric.get("max")
            }
        
        return summary
    
    def auto_save_if_needed(self):
        """必要に応じて自動保存"""
        current_time = time.time()
        
        if current_time - self.last_auto_save >= self.auto_save_interval:
            self.save_state()
            self.last_auto_save = current_time
    
    def save_state(self):
        """現在の状態を保存"""
        self.current_state["last_updated"] = datetime.now().isoformat()
        
        # メインの状態ファイル
        state_file = os.path.join(self.state_dir, "current_state.json")
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_state, f, indent=2)
        
        # バックアップも作成
        backup_file = os.path.join(
            self.state_dir, 
            f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_state, f, indent=2)
        
        # 古いバックアップを削除（最新10件のみ保持）
        self.cleanup_old_backups()
    
    def cleanup_old_backups(self):
        """古いバックアップをクリーンアップ"""
        backup_files = [f for f in os.listdir(self.state_dir) 
                       if f.startswith("state_backup_")]
        backup_files.sort(reverse=True)
        
        # 10件より多い場合は削除
        for old_file in backup_files[10:]:
            os.remove(os.path.join(self.state_dir, old_file))
    
    def load_checkpoint(self, checkpoint_id: str) -> Any:
        """チェックポイントをロード"""
        checkpoint_file = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.pkl")
        
        if not os.path.exists(checkpoint_file):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        
        with open(checkpoint_file, 'rb') as f:
            return pickle.load(f)
    
    def get_progress_report(self) -> str:
        """進捗レポートを生成"""
        report_lines = []
        
        report_lines.append("📊 PROGRESS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Project: {self.project_name}")
        report_lines.append(f"Started: {self.current_state['started_at']}")
        report_lines.append(f"Last Updated: {self.current_state['last_updated']}")
        report_lines.append("")
        
        # チェックポイント
        report_lines.append(f"📍 Checkpoints: {len(self.current_state['checkpoints'])}")
        for cp in self.current_state['checkpoints'][-5:]:  # 最新5件
            report_lines.append(f"  - {cp['name']} ({cp['created_at'][:19]})")
        
        # テスト結果
        report_lines.append("")
        report_lines.append(f"🧪 Test Results: {len(self.current_state['results'])}")
        for test_name, result in list(self.current_state['results'].items())[-5:]:
            summary = result.get('summary', {})
            report_lines.append(f"  - {test_name}: "
                              f"{summary.get('passed', 0)}/{summary.get('total_tests', 0)} passed")
        
        # メトリクス
        report_lines.append("")
        report_lines.append(f"📈 Metrics:")
        for name, summary in self.get_metrics_summary().items():
            report_lines.append(f"  - {name}: {summary['last_value']} "
                              f"(min: {summary['min']}, max: {summary['max']})")
        
        # エラーログ
        error_count = sum(1 for log in self.current_state['logs'] 
                         if log['type'] == 'error')
        report_lines.append("")
        report_lines.append(f"🚨 Error Logs: {error_count}")
        
        return '\n'.join(report_lines)

class AutoSaveContext:
    """自動保存コンテキストマネージャー"""
    
    def __init__(self, saver: ProgressStateSaver, checkpoint_name: str):
        self.saver = saver
        self.checkpoint_name = checkpoint_name
        self.data = {}
        
    def __enter__(self):
        # 開始時のチェックポイント
        self.saver.create_checkpoint(
            f"{self.checkpoint_name}_start",
            {"status": "started"},
            "Context started"
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 終了時の状態を保存
        if exc_type is None:
            # 正常終了
            self.saver.create_checkpoint(
                f"{self.checkpoint_name}_complete",
                self.data,
                "Context completed successfully"
            )
        else:
            # エラー発生
            self.saver.save_error_log(
                exc_type.__name__,
                str(exc_val),
                {"checkpoint": self.checkpoint_name}
            )
        
        # 状態を保存
        self.saver.save_state()
        
        return False  # 例外は再発生

def demo_progress_saver():
    """進捗保存システムのデモ"""
    saver = ProgressStateSaver("demo_project")
    
    print("🎯 PROGRESS STATE SAVER DEMO")
    print("=" * 60)
    
    # 1. チェックポイント作成
    data = {"test_data": list(range(100)), "config": {"version": "1.0"}}
    checkpoint_id = saver.create_checkpoint("initial_data", data, "Initial test data")
    
    # 2. テスト結果保存
    test_results = {
        "total": 100,
        "passed": 95,
        "failed": 5,
        "errors": 0,
        "details": ["Test details would go here"]
    }
    saver.save_test_results("unit_tests", test_results)
    
    # 3. メトリクス更新
    for i in range(10):
        saver.update_metrics("processing_speed", 100 + i * 10)
        saver.update_metrics("accuracy", 0.95 + i * 0.001)
    
    # 4. エラーログ
    try:
        1 / 0
    except ZeroDivisionError as e:
        saver.save_error_log("calculation_error", e, {"operation": "division"})
    
    # 5. 進捗スナップショット
    progress_data = {
        "completed_steps": 5,
        "total_steps": 10,
        "current_step": "Data validation",
        "percentage": 50
    }
    saver.save_progress_snapshot("midpoint", progress_data)
    
    # 6. レポート生成
    print("\n" + saver.get_progress_report())
    
    # 7. 自動保存コンテキスト使用例
    print("\n\nUsing AutoSave Context:")
    with AutoSaveContext(saver, "data_processing") as ctx:
        # 作業実行
        ctx.data["processed_items"] = 1000
        ctx.data["success_rate"] = 0.98
        print("Processing completed within context")
    
    print("\n✅ Demo completed!")
    print(f"📁 All data saved in: {saver.state_dir}")

if __name__ == "__main__":
    demo_progress_saver()
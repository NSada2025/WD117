#!/usr/bin/env python3
"""
Output Management System
出力量管理・安定化措置 - dev3品質管理役割用最適化
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

class OutputManager:
    def __init__(self):
        self.output_dir = "managed-outputs"
        self.summary_dir = "output-summaries"
        self.archive_dir = "output-archives"
        self.ensure_directories()
        
        # 出力制限設定
        self.limits = {
            "max_lines_per_output": 100,      # 1回の出力での最大行数
            "summary_threshold": 50,           # 要約を開始する行数
            "file_output_threshold": 200,      # ファイル出力に切り替える行数
            "error_context_lines": 5,          # エラー前後の表示行数
            "test_result_preview": 10          # テスト結果プレビュー行数
        }
        
    def ensure_directories(self):
        """必要なディレクトリを作成"""
        for directory in [self.output_dir, self.summary_dir, self.archive_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def summarize_output(self, output: str, output_type: str = "general") -> Dict:
        """大量出力を要約"""
        lines = output.strip().split('\n')
        total_lines = len(lines)
        
        if total_lines <= self.limits["summary_threshold"]:
            # 要約不要
            return {
                "needs_summary": False,
                "full_output": output,
                "line_count": total_lines
            }
        
        # 出力タイプ別の要約処理
        if output_type == "test_results":
            summary = self.summarize_test_results(lines)
        elif output_type == "error_log":
            summary = self.summarize_error_log(lines)
        elif output_type == "data_analysis":
            summary = self.summarize_data_analysis(lines)
        else:
            summary = self.summarize_general(lines)
        
        # ファイルに完全出力を保存
        file_path = self.save_full_output(output, output_type)
        
        return {
            "needs_summary": True,
            "summary": summary,
            "full_output_file": file_path,
            "line_count": total_lines,
            "output_type": output_type
        }
    
    def summarize_test_results(self, lines: List[str]) -> str:
        """テスト結果を要約"""
        summary_parts = []
        
        # ヘッダー
        summary_parts.append("📊 TEST RESULTS SUMMARY")
        summary_parts.append("=" * 50)
        
        # 統計情報を抽出
        stats = self.extract_test_statistics(lines)
        
        if stats:
            summary_parts.append(f"Total Tests: {stats.get('total', 'N/A')}")
            summary_parts.append(f"✅ Passed: {stats.get('passed', 0)}")
            summary_parts.append(f"❌ Failed: {stats.get('failed', 0)}")
            summary_parts.append(f"⚠️  Warnings: {stats.get('warnings', 0)}")
            summary_parts.append("")
        
        # 失敗したテストのみ表示
        failures = self.extract_test_failures(lines)
        if failures:
            summary_parts.append("FAILED TESTS:")
            summary_parts.append("-" * 30)
            for failure in failures[:5]:  # 最大5件
                summary_parts.append(f"  ❌ {failure}")
            if len(failures) > 5:
                summary_parts.append(f"  ... and {len(failures) - 5} more failures")
        
        # プレビュー
        summary_parts.append("")
        summary_parts.append("PREVIEW (first 10 lines):")
        summary_parts.append("-" * 30)
        summary_parts.extend(lines[:self.limits["test_result_preview"]])
        
        # フッター
        summary_parts.append("")
        summary_parts.append(f"📁 Full output saved ({len(lines)} lines)")
        
        return '\n'.join(summary_parts)
    
    def summarize_error_log(self, lines: List[str]) -> str:
        """エラーログを要約"""
        summary_parts = []
        
        # ヘッダー
        summary_parts.append("🚨 ERROR LOG SUMMARY")
        summary_parts.append("=" * 50)
        
        # エラーを分類
        errors = self.classify_errors(lines)
        
        # エラー統計
        summary_parts.append(f"Total Errors: {errors['total']}")
        summary_parts.append("")
        
        # エラータイプ別集計
        if errors['by_type']:
            summary_parts.append("ERROR TYPES:")
            for error_type, count in sorted(errors['by_type'].items(), 
                                          key=lambda x: x[1], reverse=True):
                summary_parts.append(f"  {error_type}: {count}")
        
        # 重要なエラーをハイライト
        if errors['critical']:
            summary_parts.append("")
            summary_parts.append("CRITICAL ERRORS:")
            summary_parts.append("-" * 30)
            for error in errors['critical'][:3]:
                summary_parts.append(f"  🔴 {error['message']}")
                if error.get('context'):
                    for ctx_line in error['context'][:3]:
                        summary_parts.append(f"     {ctx_line}")
        
        # 最新のエラー
        summary_parts.append("")
        summary_parts.append("LATEST ERRORS:")
        summary_parts.append("-" * 30)
        recent_errors = self.extract_recent_errors(lines, limit=5)
        for error in recent_errors:
            summary_parts.append(f"  {error}")
        
        # フッター
        summary_parts.append("")
        summary_parts.append(f"📁 Full log saved ({len(lines)} lines)")
        
        return '\n'.join(summary_parts)
    
    def summarize_data_analysis(self, lines: List[str]) -> str:
        """データ分析結果を要約"""
        summary_parts = []
        
        # ヘッダー
        summary_parts.append("📈 DATA ANALYSIS SUMMARY")
        summary_parts.append("=" * 50)
        
        # 重要な統計情報を抽出
        stats = self.extract_analysis_statistics(lines)
        
        if stats:
            summary_parts.append("KEY METRICS:")
            for key, value in stats.items():
                summary_parts.append(f"  {key}: {value}")
        
        # 結果のハイライト
        highlights = self.extract_analysis_highlights(lines)
        if highlights:
            summary_parts.append("")
            summary_parts.append("HIGHLIGHTS:")
            summary_parts.append("-" * 30)
            for highlight in highlights[:5]:
                summary_parts.append(f"  • {highlight}")
        
        # データプレビュー
        summary_parts.append("")
        summary_parts.append("DATA PREVIEW:")
        summary_parts.append("-" * 30)
        data_lines = [line for line in lines if self.is_data_line(line)]
        summary_parts.extend(data_lines[:10])
        if len(data_lines) > 10:
            summary_parts.append(f"  ... and {len(data_lines) - 10} more data rows")
        
        # フッター
        summary_parts.append("")
        summary_parts.append(f"📁 Full analysis saved ({len(lines)} lines)")
        
        return '\n'.join(summary_parts)
    
    def summarize_general(self, lines: List[str]) -> str:
        """一般的な出力を要約"""
        summary_parts = []
        
        # ヘッダー
        summary_parts.append("📋 OUTPUT SUMMARY")
        summary_parts.append("=" * 50)
        summary_parts.append(f"Total Lines: {len(lines)}")
        summary_parts.append("")
        
        # 最初と最後を表示
        preview_lines = 10
        summary_parts.append(f"FIRST {preview_lines} LINES:")
        summary_parts.append("-" * 30)
        summary_parts.extend(lines[:preview_lines])
        
        if len(lines) > preview_lines * 2:
            summary_parts.append("")
            summary_parts.append("... [content omitted] ...")
            summary_parts.append("")
            summary_parts.append(f"LAST {preview_lines} LINES:")
            summary_parts.append("-" * 30)
            summary_parts.extend(lines[-preview_lines:])
        
        # フッター
        summary_parts.append("")
        summary_parts.append(f"📁 Full output saved ({len(lines)} lines)")
        
        return '\n'.join(summary_parts)
    
    def extract_test_statistics(self, lines: List[str]) -> Dict:
        """テスト統計を抽出"""
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
        
        for line in lines:
            line_lower = line.lower()
            
            # 様々なテストフレームワークのパターン
            if "tests passed" in line_lower or "test passed" in line_lower:
                # 数値を抽出
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    stats["passed"] += int(numbers[0])
            
            elif "tests failed" in line_lower or "test failed" in line_lower:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    stats["failed"] += int(numbers[0])
            
            elif "warning" in line_lower:
                stats["warnings"] += 1
            
            # 合計テスト数
            if "total tests" in line_lower or "tests total" in line_lower:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    stats["total"] = int(numbers[0])
        
        # 合計が設定されていない場合は計算
        if stats["total"] == 0:
            stats["total"] = stats["passed"] + stats["failed"]
        
        return stats
    
    def extract_test_failures(self, lines: List[str]) -> List[str]:
        """失敗したテストを抽出"""
        failures = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # 失敗パターン
            if any(pattern in line_lower for pattern in ["fail", "error", "assert"]):
                # テスト名を推測
                if "test" in line_lower:
                    failures.append(line.strip())
                elif i > 0 and "test" in lines[i-1].lower():
                    failures.append(lines[i-1].strip() + " - " + line.strip())
        
        return failures
    
    def classify_errors(self, lines: List[str]) -> Dict:
        """エラーを分類"""
        errors = {
            "total": 0,
            "by_type": {},
            "critical": []
        }
        
        error_patterns = {
            "SyntaxError": "syntax",
            "TypeError": "type",
            "ValueError": "value",
            "KeyError": "key",
            "AttributeError": "attribute",
            "ImportError": "import",
            "FileNotFoundError": "file",
            "Exception": "general"
        }
        
        for i, line in enumerate(lines):
            if "error" in line.lower() or "exception" in line.lower():
                errors["total"] += 1
                
                # エラータイプを特定
                for pattern, error_type in error_patterns.items():
                    if pattern in line:
                        errors["by_type"][error_type] = errors["by_type"].get(error_type, 0) + 1
                        
                        # クリティカルエラーチェック
                        if any(critical in line.lower() for critical in ["critical", "fatal", "severe"]):
                            context = lines[max(0, i-2):min(len(lines), i+3)]
                            errors["critical"].append({
                                "message": line.strip(),
                                "context": context
                            })
                        break
        
        return errors
    
    def extract_recent_errors(self, lines: List[str], limit: int = 5) -> List[str]:
        """最新のエラーを抽出"""
        errors = []
        
        for line in reversed(lines):
            if "error" in line.lower() or "exception" in line.lower():
                errors.append(line.strip())
                if len(errors) >= limit:
                    break
        
        return errors
    
    def extract_analysis_statistics(self, lines: List[str]) -> Dict:
        """分析統計を抽出"""
        stats = {}
        
        import re
        
        for line in lines:
            # 一般的な統計パターン
            patterns = [
                (r'accuracy[:\s]+(\d+\.?\d*)%?', 'Accuracy'),
                (r'precision[:\s]+(\d+\.?\d*)%?', 'Precision'),
                (r'recall[:\s]+(\d+\.?\d*)%?', 'Recall'),
                (r'mean[:\s]+(\d+\.?\d*)', 'Mean'),
                (r'std[:\s]+(\d+\.?\d*)', 'Std Dev'),
                (r'total[:\s]+(\d+)', 'Total'),
                (r'count[:\s]+(\d+)', 'Count')
            ]
            
            for pattern, name in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and name not in stats:
                    stats[name] = match.group(1)
        
        return stats
    
    def extract_analysis_highlights(self, lines: List[str]) -> List[str]:
        """分析のハイライトを抽出"""
        highlights = []
        
        keywords = ["significant", "important", "notable", "key finding", 
                   "conclusion", "result", "discovered", "found"]
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                highlights.append(line.strip())
        
        return highlights
    
    def is_data_line(self, line: str) -> bool:
        """データ行かどうか判定"""
        # CSV形式やタブ区切りなど
        return (',' in line or '\t' in line) and len(line.split()) > 3
    
    def save_full_output(self, output: str, output_type: str) -> str:
        """完全な出力をファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ファイル名生成
        content_hash = hashlib.md5(output.encode()).hexdigest()[:8]
        filename = f"{output_type}_{timestamp}_{content_hash}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        # ファイルに保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Output Type: {output_type}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Lines: {len(output.strip().split(chr(10)))}\n")
            f.write("=" * 80 + "\n")
            f.write(output)
        
        return filepath
    
    def create_staged_output(self, stages: List[Dict]) -> str:
        """段階的な出力を作成"""
        output_parts = []
        
        for i, stage in enumerate(stages, 1):
            output_parts.append(f"STAGE {i}/{len(stages)}: {stage.get('name', 'Processing')}")
            output_parts.append("-" * 50)
            
            # ステージの概要
            if stage.get('summary'):
                output_parts.append(stage['summary'])
            
            # 詳細が必要な場合のみ表示
            if stage.get('show_details', False):
                details = stage.get('details', '')
                if isinstance(details, list):
                    output_parts.extend(details[:20])  # 最大20行
                    if len(details) > 20:
                        output_parts.append(f"... ({len(details) - 20} more lines)")
                else:
                    output_parts.append(str(details))
            
            # 進捗状況
            if stage.get('progress'):
                output_parts.append(f"Progress: {stage['progress']}")
            
            output_parts.append("")  # 空行
        
        return '\n'.join(output_parts)
    
    def optimize_repetitive_output(self, lines: List[str]) -> List[str]:
        """繰り返し出力を最適化"""
        optimized = []
        last_line = None
        repeat_count = 0
        
        for line in lines:
            if line == last_line:
                repeat_count += 1
            else:
                if repeat_count > 1:
                    optimized.append(f"[Previous line repeated {repeat_count} times]")
                if last_line is not None:
                    optimized.append(last_line)
                last_line = line
                repeat_count = 1
        
        # 最後の行を処理
        if repeat_count > 1:
            optimized.append(f"[Previous line repeated {repeat_count} times]")
        if last_line is not None:
            optimized.append(last_line)
        
        return optimized

class SmartOutputWrapper:
    """既存のprint文を置き換えるスマート出力ラッパー"""
    
    def __init__(self, output_manager: OutputManager):
        self.output_manager = output_manager
        self.buffer = []
        self.output_type = "general"
        
    def set_output_type(self, output_type: str):
        """出力タイプを設定"""
        self.output_type = output_type
        
    def print(self, *args, **kwargs):
        """print関数の代替"""
        # 通常のprint処理
        output = ' '.join(str(arg) for arg in args)
        
        # バッファに追加
        self.buffer.append(output)
        
        # バッファサイズチェック
        if len(self.buffer) >= self.output_manager.limits["max_lines_per_output"]:
            self.flush()
        else:
            # 即座に表示（要約なし）
            print(output, **kwargs)
    
    def flush(self):
        """バッファをフラッシュして要約"""
        if not self.buffer:
            return
        
        full_output = '\n'.join(self.buffer)
        result = self.output_manager.summarize_output(full_output, self.output_type)
        
        if result["needs_summary"]:
            print("\n" + "="*60)
            print("📦 OUTPUT SUMMARIZED")
            print("="*60)
            print(result["summary"])
            print("="*60)
            print(f"📁 Full output: {result['full_output_file']}")
            print("="*60 + "\n")
        
        self.buffer.clear()

def demo_output_management():
    """出力管理システムのデモ"""
    manager = OutputManager()
    
    print("🎯 OUTPUT MANAGEMENT SYSTEM DEMO")
    print("="*60)
    
    # テスト結果の例
    test_output = """Running test suite...
Test 1: test_addition ... PASSED
Test 2: test_subtraction ... PASSED
Test 3: test_multiplication ... FAILED
  AssertionError: Expected 20, got 21
Test 4: test_division ... PASSED
Test 5: test_complex_calculation ... FAILED
  ValueError: Invalid input
Test 6: test_edge_case_1 ... PASSED
Test 7: test_edge_case_2 ... WARNING: Deprecated function used
Test 8: test_performance ... PASSED
Test 9: test_integration ... FAILED
  ConnectionError: Database not available
Test 10: test_validation ... PASSED

Summary: 7 passed, 3 failed, 1 warning
Total time: 12.34s
""" + "\n".join([f"Additional test line {i}" for i in range(100)])
    
    print("\n1. TEST RESULTS SUMMARY:")
    result = manager.summarize_output(test_output, "test_results")
    print(result["summary"])
    
    # エラーログの例
    error_output = """2024-01-15 10:23:45 ERROR: Connection timeout
2024-01-15 10:23:46 ERROR: Retry attempt 1 failed
2024-01-15 10:23:47 ERROR: Retry attempt 2 failed
2024-01-15 10:23:48 CRITICAL: Maximum retries exceeded
2024-01-15 10:23:49 ERROR: ValueError in data processing
  File "process.py", line 45, in process_data
    value = int(data['field'])
ValueError: invalid literal for int() with base 10: 'abc'
2024-01-15 10:23:50 ERROR: KeyError: 'required_field'
2024-01-15 10:23:51 WARNING: Deprecated API endpoint used
2024-01-15 10:23:52 ERROR: FileNotFoundError: config.json
2024-01-15 10:23:53 CRITICAL: System shutdown initiated
""" + "\n".join([f"2024-01-15 10:24:{i:02d} ERROR: Generic error {i}" for i in range(60)])
    
    print("\n2. ERROR LOG SUMMARY:")
    result = manager.summarize_output(error_output, "error_log")
    print(result["summary"])

if __name__ == "__main__":
    demo_output_management()
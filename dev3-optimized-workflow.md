# Dev3 最適化ワークフローガイドライン

## 📋 概要

品質管理・テスト役割での大量出力によるauto-compact問題を防ぐための最適化されたワークフロー。

## 🎯 基本原則

### 1. 出力前に考える
- **必要な情報のみ**を出力
- **要約優先**、詳細は後で
- **段階的表示**で理解しやすく

### 2. 外部ファイル活用
- 大量データは即座にファイル保存
- 画面には要約のみ表示
- 必要時にファイル参照

### 3. 作業の分割実行
- 大きなタスクは小さく分割
- 各ステップで進捗確認
- バッファクリアのタイミング確保

## 💡 具体的な実装方法

### テスト実行時の最適化

```python
# 悪い例 ❌ - 全結果を一度に出力
for test in all_tests:
    result = run_test(test)
    print(f"Test {test}: {result}")  # 1000件のテストで大量出力

# 良い例 ✅ - 段階的な要約表示
def run_tests_optimized(tests):
    # 1. 進捗表示のみ
    print(f"🧪 Running {len(tests)} tests...")
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    # 2. バッチ処理
    batch_size = 50
    for i in range(0, len(tests), batch_size):
        batch = tests[i:i+batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{len(tests)//batch_size + 1}")
        
        for test in batch:
            result = run_test(test)
            if result.passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"{test}: {result.error}")
    
    # 3. 要約のみ表示
    print(f"\n✅ Test Summary:")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    
    # 4. エラーは最初の5件のみ
    if results["errors"]:
        print(f"\n❌ First 5 errors:")
        for error in results["errors"][:5]:
            print(f"  - {error}")
        if len(results["errors"]) > 5:
            print(f"  ... and {len(results["errors"]) - 5} more")
    
    # 5. 詳細はファイルに保存
    save_detailed_results("test_results.json", results)
    print(f"\n📁 Full results saved to: test_results.json")
```

### エラー分析時の最適化

```python
# 悪い例 ❌ - 全エラーログを表示
with open("error.log", "r") as f:
    print(f.read())  # 10万行のログで画面が埋まる

# 良い例 ✅ - スマートな要約
def analyze_errors_optimized(log_file):
    # 1. エラーを分類
    error_summary = {
        "total": 0,
        "by_type": {},
        "critical": [],
        "recent": []
    }
    
    with open(log_file, "r") as f:
        for line in f:
            if "ERROR" in line:
                error_summary["total"] += 1
                # エラータイプ分類
                error_type = extract_error_type(line)
                error_summary["by_type"][error_type] = \
                    error_summary["by_type"].get(error_type, 0) + 1
                
                # クリティカルエラー抽出
                if "CRITICAL" in line:
                    error_summary["critical"].append(line.strip())
    
    # 2. 要約表示
    print("🚨 Error Analysis Summary")
    print(f"Total Errors: {error_summary['total']}")
    print("\nError Types:")
    for error_type, count in sorted(error_summary["by_type"].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {error_type}: {count}")
    
    if error_summary["critical"]:
        print(f"\n🔴 Critical Errors: {len(error_summary['critical'])}")
        for error in error_summary["critical"][:3]:
            print(f"  {error[:80]}...")
    
    # 3. 詳細分析はファイルに
    save_error_analysis("error_analysis.json", error_summary)
    print(f"\n📁 Detailed analysis: error_analysis.json")
```

### データ検証時の最適化

```python
# 悪い例 ❌ - 全データを表示
data = load_large_dataset()
for row in data:
    print(validate_row(row))  # 10万行で画面占有

# 良い例 ✅ - 進捗と要約のみ
def validate_data_optimized(data):
    print(f"🔍 Validating {len(data)} records...")
    
    validation_summary = {
        "total": len(data),
        "valid": 0,
        "invalid": 0,
        "issues": []
    }
    
    # プログレスバー表示
    for i, row in enumerate(data):
        if i % 1000 == 0:
            progress = (i / len(data)) * 100
            print(f"\rProgress: {progress:.1f}% [{i}/{len(data)}]", end="")
        
        result = validate_row(row)
        if result.is_valid:
            validation_summary["valid"] += 1
        else:
            validation_summary["invalid"] += 1
            if len(validation_summary["issues"]) < 10:
                validation_summary["issues"].append({
                    "row": i,
                    "error": result.error
                })
    
    # 要約表示
    print(f"\n\n✅ Validation Complete:")
    print(f"  Valid: {validation_summary['valid']} ({validation_summary['valid']/validation_summary['total']*100:.1f}%)")
    print(f"  Invalid: {validation_summary['invalid']}")
    
    # 最初の数件のみ表示
    if validation_summary["issues"]:
        print("\nSample Issues:")
        for issue in validation_summary["issues"][:5]:
            print(f"  Row {issue['row']}: {issue['error']}")
    
    # 完全レポートは外部ファイル
    save_validation_report("validation_report.csv", validation_summary)
    print(f"\n📁 Full report: validation_report.csv")
```

## 🛠️ 便利なヘルパー関数

### 1. スマート出力関数
```python
def smart_print(content, max_lines=50):
    """大量出力を自動的に要約"""
    lines = str(content).split('\n')
    
    if len(lines) <= max_lines:
        print(content)
    else:
        print(f"[Showing first {max_lines//2} and last {max_lines//2} lines of {len(lines)} total]")
        print('\n'.join(lines[:max_lines//2]))
        print("\n... [content omitted] ...\n")
        print('\n'.join(lines[-max_lines//2:]))
        
        # ファイルに保存
        filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(content)
        print(f"\n📁 Full output saved to: {filename}")
```

### 2. プログレストラッカー
```python
class ProgressTracker:
    def __init__(self, total, description="Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.last_update = 0
        
    def update(self, increment=1):
        self.current += increment
        progress = (self.current / self.total) * 100
        
        # 1%ごとに更新
        if progress - self.last_update >= 1:
            print(f"\r{self.description}: {progress:.0f}% [{self.current}/{self.total}]", end="")
            self.last_update = progress
            
        if self.current >= self.total:
            print()  # 改行
```

### 3. 自動要約デコレータ
```python
def auto_summarize(output_type="general", max_lines=100):
    """関数の出力を自動的に要約するデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 出力をキャプチャ
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                result = func(*args, **kwargs)
                output = buffer.getvalue()
                
                # 要約処理
                manager = OutputManager()
                summary_result = manager.summarize_output(output, output_type)
                
                # 元のstdoutに戻す
                sys.stdout = old_stdout
                
                if summary_result["needs_summary"]:
                    print(summary_result["summary"])
                    print(f"\n📁 Full output: {summary_result['full_output_file']}")
                else:
                    print(output)
                
                return result
                
            finally:
                sys.stdout = old_stdout
                
        return wrapper
    return decorator

# 使用例
@auto_summarize(output_type="test_results")
def run_comprehensive_tests():
    # 大量のテスト出力があっても自動的に要約される
    for i in range(1000):
        print(f"Test {i}: {'PASSED' if i % 7 != 0 else 'FAILED'}")
```

## 📊 tmuxバッファ管理

### 定期的なバッファクリア
```bash
# 30分ごとに自動クリア
*/30 * * * * tmux clear-history -t dev3-session

# 作業の区切りで手動クリア
alias clearb='tmux clear-history'
```

### セッションローテーション
```bash
# 2時間ごとに新しいセッションに切り替え
function rotate_session() {
    OLD_SESSION=$(tmux display-message -p '#S')
    NEW_SESSION="${OLD_SESSION}_$(date +%H%M)"
    
    # 新セッション作成
    tmux new-session -d -s $NEW_SESSION
    
    # 作業状態を保存
    tmux capture-pane -t $OLD_SESSION -p > session_backup_$(date +%Y%m%d_%H%M%S).txt
    
    # 新セッションに切り替え
    tmux switch-client -t $NEW_SESSION
    
    echo "Rotated from $OLD_SESSION to $NEW_SESSION"
}
```

## 🎯 チェックリスト

作業開始前に確認:

- [ ] 出力管理システムが有効か
- [ ] tmux健全性モニターが起動しているか
- [ ] 作業の分割計画を立てたか
- [ ] 要約表示の準備ができているか
- [ ] 外部ファイル保存ディレクトリが準備されているか

作業中に確認:

- [ ] 出力が100行を超えていないか
- [ ] 定期的にバッファをクリアしているか
- [ ] 重要な結果は即座に保存しているか
- [ ] プログレス表示を使用しているか

作業後に確認:

- [ ] すべての結果がファイルに保存されているか
- [ ] 要約レポートが作成されているか
- [ ] 不要な大量出力がクリアされているか
- [ ] 次回のための改善点をメモしたか

---

このガイドラインに従うことで、auto-compact問題を防ぎながら効率的な品質管理作業が可能になります。
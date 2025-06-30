#!/usr/bin/env python3
"""
APIエンドポイント動作確認スクリプト
全エンドポイントの基本的な動作を確認
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple

# APIベースURL
BASE_URL = "http://localhost:8000"

# テスト結果を格納
test_results = []


def check_endpoint(method: str, path: str, description: str, **kwargs) -> Tuple[bool, str]:
    """エンドポイントをチェック"""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.request(method, url, **kwargs)
        if response.status_code < 400:
            return True, f"OK ({response.status_code})"
        else:
            return False, f"Error ({response.status_code}): {response.text[:100]}"
    except Exception as e:
        return False, f"Exception: {str(e)}"


def test_basic_endpoints():
    """基本エンドポイントのテスト"""
    print("\n=== 基本エンドポイント ===")
    
    # ルート
    success, message = check_endpoint("GET", "/", "APIルート")
    test_results.append(("GET /", success, message))
    print(f"GET / - {message}")
    
    # OpenAPIドキュメント
    success, message = check_endpoint("GET", "/docs", "APIドキュメント")
    test_results.append(("GET /docs", success, message))
    print(f"GET /docs - {message}")


def test_patient_endpoints():
    """患者管理エンドポイントのテスト"""
    print("\n=== 患者管理エンドポイント ===")
    
    # 患者リスト
    success, message = check_endpoint("GET", "/patients", "患者リスト取得")
    test_results.append(("GET /patients", success, message))
    print(f"GET /patients - {message}")
    
    # ページネーション
    success, message = check_endpoint("GET", "/patients", "患者リスト（ページネーション）", 
                                    params={"skip": 0, "limit": 10})
    test_results.append(("GET /patients?skip=0&limit=10", success, message))
    print(f"GET /patients?skip=0&limit=10 - {message}")
    
    # 個別患者
    patient_id = "2024-001"
    success, message = check_endpoint("GET", f"/patients/{patient_id}", "患者詳細取得")
    test_results.append((f"GET /patients/{patient_id}", success, message))
    print(f"GET /patients/{patient_id} - {message}")
    
    # 患者サマリー
    success, message = check_endpoint("GET", f"/patients/{patient_id}/summary", "患者サマリー")
    test_results.append((f"GET /patients/{patient_id}/summary", success, message))
    print(f"GET /patients/{patient_id}/summary - {message}")


def test_analysis_endpoints():
    """分析エンドポイントのテスト"""
    print("\n=== 分析エンドポイント ===")
    
    # 分析実行
    analysis_data = {
        "patient_id": "2024-001",
        "analysis_type": "cephalometric",
        "data": {}
    }
    success, message = check_endpoint("POST", "/analyze", "分析実行", json=analysis_data)
    test_results.append(("POST /analyze", success, message))
    print(f"POST /analyze - {message}")


def test_treatment_plan_endpoints():
    """治療計画エンドポイントのテスト"""
    print("\n=== 治療計画エンドポイント ===")
    
    patient_id = "2024-001"
    
    # 治療計画生成
    success, message = check_endpoint(
        "POST", 
        f"/patients/{patient_id}/treatment-plan", 
        "治療計画生成",
        params={"patient_age": 15}
    )
    test_results.append((f"POST /patients/{patient_id}/treatment-plan", success, message))
    print(f"POST /patients/{patient_id}/treatment-plan - {message}")
    
    # 治療計画レポート
    success, message = check_endpoint(
        "GET", 
        f"/patients/{patient_id}/treatment-plan-report", 
        "治療計画レポート",
        params={"patient_age": 15}
    )
    test_results.append((f"GET /patients/{patient_id}/treatment-plan-report", success, message))
    print(f"GET /patients/{patient_id}/treatment-plan-report - {message}")
    
    # 治療シミュレーション
    simulation_data = {
        "patient_id": patient_id,
        "patient_age": 15
    }
    success, message = check_endpoint(
        "POST", 
        "/treatment-simulation", 
        "治療シミュレーション",
        json=simulation_data
    )
    test_results.append(("POST /treatment-simulation", success, message))
    print(f"POST /treatment-simulation - {message}")


def test_stats_endpoint():
    """統計エンドポイントのテスト"""
    print("\n=== 統計エンドポイント ===")
    
    success, message = check_endpoint("GET", "/stats", "統計情報")
    test_results.append(("GET /stats", success, message))
    print(f"GET /stats - {message}")


def generate_report():
    """テスト結果レポートを生成"""
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success, _ in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"\n総テスト数: {total_tests}")
    print(f"成功: {passed_tests}")
    print(f"失敗: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print("\n失敗したエンドポイント:")
        for endpoint, success, message in test_results:
            if not success:
                print(f"  - {endpoint}: {message}")
    
    # レポートファイルに保存
    report_data = {
        "test_date": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%",
        "results": [
            {
                "endpoint": endpoint,
                "success": success,
                "message": message
            }
            for endpoint, success, message in test_results
        ]
    }
    
    with open("/mnt/d/multiagent-system/src/backend/endpoint_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print("\n詳細レポートを endpoint_test_report.json に保存しました")


def main():
    """メイン実行関数"""
    print("APIエンドポイント動作確認開始")
    print("=" * 60)
    
    try:
        # APIサーバーの生存確認
        response = requests.get(BASE_URL, timeout=5)
        print(f"✓ APIサーバー稼働中 (version: {response.json().get('version', 'unknown')})")
        
        # 各エンドポイントのテスト
        test_basic_endpoints()
        test_patient_endpoints()
        test_analysis_endpoints()
        test_treatment_plan_endpoints()
        test_stats_endpoint()
        
        # レポート生成
        generate_report()
        
    except requests.exceptions.ConnectionError:
        print("✗ エラー: APIサーバーに接続できません")
        print("  start_backend.sh を実行してAPIサーバーを起動してください")
        return 1
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
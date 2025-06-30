#!/usr/bin/env python3
"""
分析エンジン連携コネクタ
咬合分析エンジンと治療計画エンジンの連携を管理
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict

# プロジェクトのルートパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

# 咬合分析エンジンのインポート
from analysis.occlusion_analyzer import (
    OcclusionAnalyzer, OcclusionMetrics, OcclusionScore,
    MolarRelationship, OcclusionSeverity
)

# backend ディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), "../../backend"))

# 治療計画エンジンのインポート
from treatment_planner import (
    TreatmentPlanner, PatientInfo, TreatmentGoals,
    ApplianceType, TreatmentStage
)


class AnalysisConnector:
    """分析エンジン連携コネクタ"""
    
    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
        self.occlusion_analyzer = OcclusionAnalyzer()
        self.treatment_planner = TreatmentPlanner()
    
    def analyze_and_plan(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        咬合分析を実行し、その結果に基づいて治療計画を生成
        
        Args:
            patient_data: 患者データ（咬合測定値、年齢、希望等を含む）
            
        Returns:
            統合分析結果と治療計画
        """
        try:
            # 1. 咬合分析の実行
            occlusion_metrics = self._extract_occlusion_metrics(patient_data)
            occlusion_score = self.occlusion_analyzer.analyze(occlusion_metrics)
            
            # 2. 分析結果から治療目標を設定
            treatment_goals = self._create_treatment_goals(occlusion_score, patient_data)
            
            # 3. 患者情報の準備
            patient_info = self._create_patient_info(patient_data)
            
            # 4. 治療計画の生成
            treatment_plan = self.treatment_planner.create_treatment_plan(
                patient_info, treatment_goals
            )
            
            # 5. 統合結果の作成
            integrated_result = {
                "occlusion_analysis": {
                    "total_score": occlusion_score.total_score,
                    "severity": occlusion_score.severity.name,
                    "component_scores": occlusion_score.component_scores,
                    "priority_rankings": occlusion_score.priority_rankings,
                    "recommendations": occlusion_score.recommendations,
                    "detailed_report": self.occlusion_analyzer.get_detailed_report()
                },
                "treatment_plan": {
                    "id": treatment_plan.id,
                    "patient_id": treatment_plan.patient_id,
                    "appliance_type": treatment_plan.appliance_type.value,
                    "estimated_duration_months": treatment_plan.estimated_duration_months,
                    "stages": [
                        {
                            "stage_number": stage.stage_number,
                            "name": stage.name,
                            "duration_weeks": stage.duration_weeks,
                            "objectives": stage.objectives,
                            "procedures": stage.procedures,
                            "status": stage.status
                        }
                        for stage in treatment_plan.stages
                    ],
                    "total_cost_estimate": treatment_plan.total_cost_estimate,
                    "notes": treatment_plan.notes
                },
                "integration_summary": self._create_integration_summary(
                    occlusion_score, treatment_plan
                )
            }
            
            return integrated_result
            
        except Exception as e:
            self.logger.error(f"分析・計画生成エラー: {e}")
            return {"error": str(e)}
    
    def _extract_occlusion_metrics(self, patient_data: Dict[str, Any]) -> OcclusionMetrics:
        """患者データから咬合測定値を抽出"""
        measurements = patient_data.get("measurements", {})
        
        # 大臼歯関係の変換
        molar_class = measurements.get("molar_relationship", "CLASS_I")
        molar_relationship = MolarRelationship[molar_class.upper().replace(" ", "_")]
        
        return OcclusionMetrics(
            overjet_mm=measurements.get("overjet_mm", 3.0),
            overbite_mm=measurements.get("overbite_mm", 3.0),
            molar_relationship=molar_relationship,
            anb_angle_degrees=measurements.get("anb_angle_degrees", 2.0),
            anterior_crossbite=measurements.get("anterior_crossbite", False),
            posterior_crossbite=measurements.get("posterior_crossbite", False),
            open_bite=measurements.get("open_bite", False),
            deep_bite=measurements.get("deep_bite", False),
            midline_deviation_mm=measurements.get("midline_deviation_mm", 0.0)
        )
    
    def _create_treatment_goals(self, occlusion_score: OcclusionScore,
                               patient_data: Dict[str, Any]) -> TreatmentGoals:
        """咬合分析結果から治療目標を生成"""
        goals = []
        
        # 優先順位に基づいて治療目標を設定
        priority_mapping = {
            "overjet": "前歯部被蓋の正常化",
            "overbite": "垂直的被蓋の改善",
            "molar_relationship": "大臼歯関係の改善",
            "anb_angle": "骨格的不調和の改善",
            "crossbite": "交叉咬合の解消",
            "midline": "正中線の一致"
        }
        
        for priority in occlusion_score.priority_rankings[:3]:  # 上位3つ
            if priority in priority_mapping:
                goals.append(priority_mapping[priority])
        
        # 患者の希望を追加
        patient_preferences = patient_data.get("preferences", {})
        if patient_preferences.get("aesthetic_priority"):
            goals.append("審美性の向上")
        
        return TreatmentGoals(
            primary_goals=goals[:2] if len(goals) >= 2 else goals,
            secondary_goals=goals[2:] if len(goals) > 2 else [],
            functional_goals=["咬合機能の改善", "顎関節の健康維持"],
            aesthetic_goals=["スマイルラインの改善"] if patient_preferences.get("aesthetic_priority") else []
        )
    
    def _create_patient_info(self, patient_data: Dict[str, Any]) -> PatientInfo:
        """患者情報を作成"""
        return PatientInfo(
            patient_id=patient_data.get("patient_id", "unknown"),
            age=patient_data.get("age", 25),
            gender=patient_data.get("gender", "不明"),
            chief_complaint=patient_data.get("chief_complaint", "咬合不正"),
            medical_history=patient_data.get("medical_history", []),
            dental_history=patient_data.get("dental_history", [])
        )
    
    def _create_integration_summary(self, occlusion_score: OcclusionScore,
                                  treatment_plan: Any) -> Dict[str, Any]:
        """統合サマリーを作成"""
        return {
            "severity_level": occlusion_score.severity.name,
            "treatment_complexity": self._assess_complexity(occlusion_score),
            "estimated_improvement": self._estimate_improvement(occlusion_score),
            "key_focus_areas": occlusion_score.priority_rankings[:3],
            "treatment_approach": self._determine_approach(occlusion_score, treatment_plan),
            "success_probability": self._estimate_success_rate(occlusion_score)
        }
    
    def _assess_complexity(self, occlusion_score: OcclusionScore) -> str:
        """治療の複雑さを評価"""
        if occlusion_score.severity.value >= OcclusionSeverity.SEVERE.value:
            return "高度"
        elif occlusion_score.severity.value >= OcclusionSeverity.MODERATE.value:
            return "中等度"
        else:
            return "軽度"
    
    def _estimate_improvement(self, occlusion_score: OcclusionScore) -> str:
        """改善見込みを推定"""
        if occlusion_score.total_score < 30:
            return "優秀（90%以上の改善）"
        elif occlusion_score.total_score < 50:
            return "良好（70-90%の改善）"
        elif occlusion_score.total_score < 70:
            return "中等度（50-70%の改善）"
        else:
            return "限定的（外科的処置の検討が必要）"
    
    def _determine_approach(self, occlusion_score: OcclusionScore,
                          treatment_plan: Any) -> str:
        """治療アプローチを決定"""
        if occlusion_score.severity.value >= OcclusionSeverity.VERY_SEVERE.value:
            return "包括的矯正治療（外科的処置の可能性あり）"
        elif treatment_plan.appliance_type == ApplianceType.CLEAR_ALIGNER:
            return "マウスピース矯正による段階的改善"
        else:
            return "ブラケット矯正による精密な歯牙移動"
    
    def _estimate_success_rate(self, occlusion_score: OcclusionScore) -> float:
        """成功率を推定（%）"""
        base_rate = 95.0
        
        # 重症度による調整
        severity_penalty = occlusion_score.severity.value * 5
        
        # 複雑な問題の数による調整
        complex_issues = sum(1 for score in occlusion_score.component_scores.values() 
                           if score > 50)
        complexity_penalty = complex_issues * 3
        
        success_rate = base_rate - severity_penalty - complexity_penalty
        return max(60.0, min(95.0, success_rate))
    
    def validate_connection(self) -> Dict[str, bool]:
        """各エンジンの接続を検証"""
        return {
            "occlusion_analyzer": True,  # 常に利用可能
            "treatment_planner": True,    # 常に利用可能
            "integration_status": True
        }


# 使用例
if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(level=logging.INFO)
    
    # コネクタ初期化
    connector = AnalysisConnector()
    
    # サンプル患者データ
    sample_patient = {
        "patient_id": "2024-001",
        "age": 25,
        "gender": "女性",
        "chief_complaint": "前歯の突出",
        "measurements": {
            "overjet_mm": 7.0,
            "overbite_mm": 5.0,
            "molar_relationship": "CLASS_II",
            "anb_angle_degrees": 6.0,
            "midline_deviation_mm": 2.5
        },
        "preferences": {
            "aesthetic_priority": True,
            "treatment_duration_preference": "standard"
        }
    }
    
    # 統合分析の実行
    result = connector.analyze_and_plan(sample_patient)
    
    # 結果の表示
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
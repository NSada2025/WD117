from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import numpy as np
from dataclasses import dataclass, field

from models import OrthodonticRecord, OcclusionRelation, JawRelation, TreatmentDifficulty


class ApplianceType(Enum):
    """矯正装置タイプ"""
    METAL_BRACKET = "メタルブラケット"
    CERAMIC_BRACKET = "セラミックブラケット"
    LINGUAL_BRACKET = "舌側矯正装置"
    CLEAR_ALIGNER = "マウスピース矯正"
    FUNCTIONAL_APPLIANCE = "機能的矯正装置"
    EXPANSION_APPLIANCE = "拡大装置"
    HEADGEAR = "ヘッドギア"
    RETENTION_APPLIANCE = "保定装置"


class TreatmentPhase(Enum):
    """治療フェーズ"""
    INITIAL_ALIGNMENT = "初期配列"
    LEVELING = "レベリング"
    SPACE_CLOSURE = "空隙閉鎖"
    OVERBITE_CORRECTION = "過蓋咬合改善"
    OVERJET_CORRECTION = "上顎前突改善"
    MIDLINE_CORRECTION = "正中線調整"
    DETAILING = "仕上げ"
    RETENTION = "保定"


@dataclass
class TreatmentGoal:
    """治療目標"""
    phase: TreatmentPhase
    description: str
    target_duration_weeks: int
    success_criteria: Dict[str, Any]
    priority: int = 1


@dataclass
class TreatmentStage:
    """治療ステージ"""
    stage_number: int
    name: str
    goals: List[TreatmentGoal]
    appliances: List[ApplianceType]
    duration_weeks: int
    key_procedures: List[str]
    monitoring_points: List[str]


@dataclass
class TreatmentPlan:
    """治療計画"""
    patient_id: str
    created_date: datetime
    total_duration_months: int
    stages: List[TreatmentStage]
    primary_appliance: ApplianceType
    auxiliary_appliances: List[ApplianceType]
    extraction_plan: Optional[Dict[str, Any]]
    special_considerations: List[str]
    follow_up_schedule: List[Dict[str, Any]]
    estimated_cost_range: Tuple[int, int]


class TreatmentPlannerEngine:
    """治療計画生成エンジン"""
    
    def __init__(self):
        # 治療期間の基準値（週単位）
        self.phase_durations = {
            TreatmentPhase.INITIAL_ALIGNMENT: (4, 8),
            TreatmentPhase.LEVELING: (8, 16),
            TreatmentPhase.SPACE_CLOSURE: (12, 24),
            TreatmentPhase.OVERBITE_CORRECTION: (8, 16),
            TreatmentPhase.OVERJET_CORRECTION: (12, 20),
            TreatmentPhase.MIDLINE_CORRECTION: (4, 8),
            TreatmentPhase.DETAILING: (8, 12),
            TreatmentPhase.RETENTION: (104, 156)  # 2-3年
        }
        
        # 装置選択の基準
        self.appliance_criteria = {
            ApplianceType.METAL_BRACKET: {
                "age_range": (10, 100),
                "complexity": ["低", "中", "高"],
                "cost_level": "低"
            },
            ApplianceType.CERAMIC_BRACKET: {
                "age_range": (15, 100),
                "complexity": ["低", "中", "高"],
                "cost_level": "中"
            },
            ApplianceType.CLEAR_ALIGNER: {
                "age_range": (16, 100),
                "complexity": ["低", "中"],
                "cost_level": "高"
            },
            ApplianceType.LINGUAL_BRACKET: {
                "age_range": (16, 100),
                "complexity": ["低", "中", "高"],
                "cost_level": "最高"
            }
        }
    
    def generate_treatment_plan(
        self,
        patient: OrthodonticRecord,
        occlusion_analysis: Dict[str, Any],
        patient_age: int,
        patient_preferences: Optional[Dict[str, Any]] = None
    ) -> TreatmentPlan:
        """咬合分析結果に基づいて治療計画を生成"""
        
        # 治療の必要性と優先順位を評価
        treatment_needs = self._assess_treatment_needs(patient, occlusion_analysis)
        
        # 適切な矯正装置を選択
        primary_appliance, auxiliary_appliances = self._select_appliances(
            patient, patient_age, patient_preferences
        )
        
        # 抜歯計画を検討
        extraction_plan = self._plan_extractions(patient, occlusion_analysis)
        
        # 治療ステージを生成
        stages = self._generate_treatment_stages(
            patient, occlusion_analysis, treatment_needs, extraction_plan
        )
        
        # 治療期間を予測
        total_duration = self._predict_treatment_duration(stages, patient)
        
        # フォローアップスケジュールを作成
        follow_up_schedule = self._create_follow_up_schedule(stages)
        
        # 費用範囲を推定
        cost_range = self._estimate_cost_range(primary_appliance, stages, extraction_plan)
        
        # 特別な配慮事項を特定
        special_considerations = self._identify_special_considerations(patient, patient_age)
        
        return TreatmentPlan(
            patient_id=patient.patient_id,
            created_date=datetime.now(),
            total_duration_months=total_duration,
            stages=stages,
            primary_appliance=primary_appliance,
            auxiliary_appliances=auxiliary_appliances,
            extraction_plan=extraction_plan,
            special_considerations=special_considerations,
            follow_up_schedule=follow_up_schedule,
            estimated_cost_range=cost_range
        )
    
    def _assess_treatment_needs(
        self,
        patient: OrthodonticRecord,
        occlusion_analysis: Dict[str, Any]
    ) -> Dict[str, int]:
        """治療の必要性と優先順位を評価"""
        needs = {}
        
        # 前歯部の評価
        overjet = patient.occlusion_relation.anterior.overjet
        if overjet and "増大" in overjet:
            needs["overjet_correction"] = 1
        
        overbite = patient.occlusion_relation.anterior.overbite
        if overbite and "深い" in overbite:
            needs["overbite_correction"] = 2
        
        # 叢生の評価
        upper_crowding = patient.dental_status.upper_arch.crowding
        if upper_crowding and "mm" in upper_crowding:
            crowding_amount = float(upper_crowding.replace("mm", ""))
            if crowding_amount > 3:
                needs["crowding_resolution"] = 1
        
        # 臼歯関係の評価
        molar_relation = patient.occlusion_relation.posterior.molar_relation
        if molar_relation and "II級" in molar_relation:
            needs["class_ii_correction"] = 1
        elif molar_relation and "III級" in molar_relation:
            needs["class_iii_correction"] = 1
        
        # 正中線の評価
        if occlusion_analysis.get("midline_deviation", 0) > 2:
            needs["midline_correction"] = 3
        
        return needs
    
    def _select_appliances(
        self,
        patient: OrthodonticRecord,
        patient_age: int,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Tuple[ApplianceType, List[ApplianceType]]:
        """適切な矯正装置を選択"""
        complexity = patient.treatment_difficulty.complexity_score
        growth_pattern = patient.jaw_relation.vertical.growth_pattern
        
        # デフォルトの選択
        primary_appliance = ApplianceType.METAL_BRACKET
        auxiliary_appliances = []
        
        # 患者の希望を考慮
        if preferences:
            if preferences.get("aesthetic_priority", False):
                if complexity in ["低", "中"]:
                    primary_appliance = ApplianceType.CLEAR_ALIGNER
                else:
                    primary_appliance = ApplianceType.CERAMIC_BRACKET
            
            if preferences.get("invisible_priority", False):
                primary_appliance = ApplianceType.LINGUAL_BRACKET
        
        # 成長期の患者の場合
        if "成長期" in growth_pattern:
            if patient_age < 12:
                auxiliary_appliances.append(ApplianceType.FUNCTIONAL_APPLIANCE)
            
            # 顎骨関係に基づく補助装置
            skeletal_class = patient.cephalometric_analysis.skeletal.skeletal_classification
            if "II級" in skeletal_class:
                auxiliary_appliances.append(ApplianceType.HEADGEAR)
        
        # 拡大が必要な場合
        if patient.dental_status.upper_arch.crowding:
            crowding = patient.dental_status.upper_arch.crowding
            if "mm" in crowding and float(crowding.replace("mm", "")) > 6:
                auxiliary_appliances.append(ApplianceType.EXPANSION_APPLIANCE)
        
        return primary_appliance, auxiliary_appliances
    
    def _plan_extractions(
        self,
        patient: OrthodonticRecord,
        occlusion_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """抜歯計画を立案"""
        extraction_plan = None
        
        # 叢生量の評価
        upper_crowding = patient.dental_status.upper_arch.crowding
        if upper_crowding and "mm" in upper_crowding:
            crowding_amount = float(upper_crowding.replace("mm", ""))
            
            # 重度叢生（>7mm）の場合
            if crowding_amount > 7:
                extraction_plan = {
                    "required": True,
                    "teeth": ["14", "24", "34", "44"],  # 第一小臼歯
                    "reason": "重度叢生の解消",
                    "timing": "治療開始時"
                }
            # 中等度叢生（4-7mm）でプロファイルの問題がある場合
            elif crowding_amount > 4:
                lip_position = patient.cephalometric_analysis.soft_tissue.lip_position
                if lip_position and "前方位" in lip_position:
                    extraction_plan = {
                        "required": True,
                        "teeth": ["14", "24"],  # 上顎第一小臼歯
                        "reason": "叢生解消と口唇前突の改善",
                        "timing": "レベリング後"
                    }
        
        # 上顎前突の評価
        overjet = patient.occlusion_relation.anterior.overjet
        if overjet and "過大" in overjet:
            if not extraction_plan:
                extraction_plan = {
                    "required": True,
                    "teeth": ["14", "24"],
                    "reason": "上顎前突の改善",
                    "timing": "治療開始時"
                }
        
        return extraction_plan
    
    def _generate_treatment_stages(
        self,
        patient: OrthodonticRecord,
        occlusion_analysis: Dict[str, Any],
        treatment_needs: Dict[str, int],
        extraction_plan: Optional[Dict[str, Any]]
    ) -> List[TreatmentStage]:
        """治療ステージを生成"""
        stages = []
        stage_number = 1
        
        # ステージ1: 初期準備と配列
        initial_goals = [
            TreatmentGoal(
                phase=TreatmentPhase.INITIAL_ALIGNMENT,
                description="歯列の初期配列と軽度の叢生解消",
                target_duration_weeks=8,
                success_criteria={
                    "alignment": "歯列弓上に全歯が配列",
                    "rotation": "回転の改善"
                }
            )
        ]
        
        initial_procedures = ["ブラケット装着", "初期ワイヤー装着"]
        if extraction_plan and extraction_plan["timing"] == "治療開始時":
            initial_procedures.append("抜歯")
        
        stages.append(
            TreatmentStage(
                stage_number=stage_number,
                name="初期治療",
                goals=initial_goals,
                appliances=[ApplianceType.METAL_BRACKET],
                duration_weeks=8,
                key_procedures=initial_procedures,
                monitoring_points=["ワイヤー交換（2-4週毎）", "口腔衛生指導"]
            )
        )
        stage_number += 1
        
        # ステージ2: レベリング
        if "crowding_resolution" in treatment_needs:
            leveling_goals = [
                TreatmentGoal(
                    phase=TreatmentPhase.LEVELING,
                    description="歯列のレベリングと叢生の解消",
                    target_duration_weeks=16,
                    success_criteria={
                        "arch_form": "理想的な歯列弓形態の確立",
                        "leveling": "咬合平面の平坦化"
                    }
                )
            ]
            
            stages.append(
                TreatmentStage(
                    stage_number=stage_number,
                    name="レベリング",
                    goals=leveling_goals,
                    appliances=[ApplianceType.METAL_BRACKET],
                    duration_weeks=16,
                    key_procedures=["段階的なワイヤーサイズアップ", "歯間拡大"],
                    monitoring_points=["月1回の調整", "歯根吸収の確認"]
                )
            )
            stage_number += 1
        
        # ステージ3: 空隙閉鎖（抜歯症例の場合）
        if extraction_plan:
            space_closure_goals = [
                TreatmentGoal(
                    phase=TreatmentPhase.SPACE_CLOSURE,
                    description="抜歯空隙の閉鎖",
                    target_duration_weeks=20,
                    success_criteria={
                        "space": "抜歯空隙の完全閉鎖",
                        "anchorage": "固定源の維持"
                    }
                )
            ]
            
            stages.append(
                TreatmentStage(
                    stage_number=stage_number,
                    name="空隙閉鎖",
                    goals=space_closure_goals,
                    appliances=[ApplianceType.METAL_BRACKET],
                    duration_weeks=20,
                    key_procedures=["パワーチェーン装着", "スライディングメカニクス"],
                    monitoring_points=["固定源管理", "歯根平行性確認"]
                )
            )
            stage_number += 1
        
        # ステージ4: 前歯部関係の改善
        if "overjet_correction" in treatment_needs or "overbite_correction" in treatment_needs:
            anterior_goals = []
            
            if "overjet_correction" in treatment_needs:
                anterior_goals.append(
                    TreatmentGoal(
                        phase=TreatmentPhase.OVERJET_CORRECTION,
                        description="上顎前突の改善",
                        target_duration_weeks=16,
                        success_criteria={
                            "overjet": "2-3mmの正常範囲",
                            "inclination": "適切な前歯傾斜"
                        }
                    )
                )
            
            if "overbite_correction" in treatment_needs:
                anterior_goals.append(
                    TreatmentGoal(
                        phase=TreatmentPhase.OVERBITE_CORRECTION,
                        description="過蓋咬合の改善",
                        target_duration_weeks=12,
                        success_criteria={
                            "overbite": "2-3mmの正常範囲",
                            "curve_of_spee": "スピー彎曲の平坦化"
                        }
                    )
                )
            
            stages.append(
                TreatmentStage(
                    stage_number=stage_number,
                    name="前歯部改善",
                    goals=anterior_goals,
                    appliances=[ApplianceType.METAL_BRACKET],
                    duration_weeks=16,
                    key_procedures=["前歯部トルクコントロール", "垂直的コントロール"],
                    monitoring_points=["前歯部関係の評価", "側貌の改善確認"]
                )
            )
            stage_number += 1
        
        # ステージ5: 仕上げ
        detailing_goals = [
            TreatmentGoal(
                phase=TreatmentPhase.DETAILING,
                description="咬合の緊密化と審美的仕上げ",
                target_duration_weeks=12,
                success_criteria={
                    "occlusion": "緊密な咬合関係",
                    "aesthetics": "審美的な歯列",
                    "function": "良好な咀嚼機能"
                }
            )
        ]
        
        stages.append(
            TreatmentStage(
                stage_number=stage_number,
                name="仕上げ",
                goals=detailing_goals,
                appliances=[ApplianceType.METAL_BRACKET],
                duration_weeks=12,
                key_procedures=["ディテーリングベンド", "咬合調整"],
                monitoring_points=["最終咬合確認", "セファロ評価"]
            )
        )
        stage_number += 1
        
        # ステージ6: 保定
        retention_goals = [
            TreatmentGoal(
                phase=TreatmentPhase.RETENTION,
                description="治療結果の維持",
                target_duration_weeks=104,  # 2年
                success_criteria={
                    "stability": "歯列の安定性維持",
                    "relapse": "後戻りの防止"
                }
            )
        ]
        
        stages.append(
            TreatmentStage(
                stage_number=stage_number,
                name="保定",
                goals=retention_goals,
                appliances=[ApplianceType.RETENTION_APPLIANCE],
                duration_weeks=104,
                key_procedures=["リテーナー装着", "定期観察"],
                monitoring_points=["3ヶ月毎の確認", "年1回のレントゲン"]
            )
        )
        
        return stages
    
    def _predict_treatment_duration(
        self,
        stages: List[TreatmentStage],
        patient: OrthodonticRecord
    ) -> int:
        """治療期間を予測（月単位）"""
        total_weeks = sum(stage.duration_weeks for stage in stages if stage.name != "保定")
        
        # 複雑度による調整
        complexity = patient.treatment_difficulty.complexity_score
        if "高" in complexity:
            total_weeks *= 1.2
        elif "低" in complexity:
            total_weeks *= 0.9
        
        # 成長による調整
        growth = patient.jaw_relation.vertical.growth_pattern
        if "成長期" in growth:
            total_weeks *= 0.85  # 成長期は治療が早い
        
        # 週から月に変換
        total_months = int(total_weeks / 4.33)
        
        return total_months
    
    def _create_follow_up_schedule(self, stages: List[TreatmentStage]) -> List[Dict[str, Any]]:
        """フォローアップスケジュールを作成"""
        schedule = []
        current_date = datetime.now()
        
        for stage in stages:
            if stage.name == "保定":
                # 保定期間は頻度を下げる
                for month in range(0, 24, 3):
                    schedule.append({
                        "date": (current_date + timedelta(days=30 * month)).isoformat(),
                        "type": "保定確認",
                        "procedures": ["リテーナー調整", "後戻り確認"]
                    })
            else:
                # 動的治療期間は月1回
                weeks = stage.duration_weeks
                for week in range(0, weeks, 4):
                    schedule.append({
                        "date": (current_date + timedelta(weeks=week)).isoformat(),
                        "type": "調整",
                        "procedures": stage.monitoring_points
                    })
                current_date += timedelta(weeks=weeks)
        
        return schedule
    
    def _estimate_cost_range(
        self,
        primary_appliance: ApplianceType,
        stages: List[TreatmentStage],
        extraction_plan: Optional[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """治療費用範囲を推定（円）"""
        base_costs = {
            ApplianceType.METAL_BRACKET: (600000, 800000),
            ApplianceType.CERAMIC_BRACKET: (700000, 900000),
            ApplianceType.CLEAR_ALIGNER: (800000, 1200000),
            ApplianceType.LINGUAL_BRACKET: (1000000, 1500000)
        }
        
        min_cost, max_cost = base_costs.get(primary_appliance, (600000, 800000))
        
        # 治療期間による調整
        total_months = sum(s.duration_weeks / 4.33 for s in stages if s.name != "保定")
        if total_months > 24:
            min_cost *= 1.2
            max_cost *= 1.2
        
        # 抜歯費用
        if extraction_plan:
            teeth_count = len(extraction_plan.get("teeth", []))
            min_cost += teeth_count * 5000
            max_cost += teeth_count * 10000
        
        return (int(min_cost), int(max_cost))
    
    def _identify_special_considerations(
        self,
        patient: OrthodonticRecord,
        patient_age: int
    ) -> List[str]:
        """特別な配慮事項を特定"""
        considerations = []
        
        # 成長期の配慮
        growth = patient.jaw_relation.vertical.growth_pattern
        if "成長期" in growth:
            considerations.append("成長期のため定期的な成長評価が必要")
            considerations.append("顎骨成長を考慮した治療計画の調整が必要")
        
        # 顎関節症状
        tmj = patient.occlusion_relation.functional.tmj_symptoms
        if tmj and tmj != "":
            considerations.append("顎関節症状に配慮した治療が必要")
            considerations.append("スプリント療法の併用を検討")
        
        # 骨格性不正咬合
        skeletal = patient.cephalometric_analysis.skeletal.skeletal_classification
        if "III級" in skeletal and patient_age > 16:
            considerations.append("外科的矯正治療の可能性を考慮")
            considerations.append("術前矯正の計画が必要")
        
        # 歯周病リスク
        if patient_age > 40:
            considerations.append("歯周病リスクが高いため歯周管理が重要")
            considerations.append("矯正力を弱めに設定")
        
        return considerations
    
    def generate_treatment_report(self, treatment_plan: TreatmentPlan) -> str:
        """治療計画レポートを生成"""
        report = f"""
# 矯正治療計画書

## 患者ID: {treatment_plan.patient_id}
## 作成日: {treatment_plan.created_date.strftime('%Y年%m月%d日')}

## 治療概要
- **予想治療期間**: {treatment_plan.total_duration_months}ヶ月（保定期間除く）
- **主装置**: {treatment_plan.primary_appliance.value}
- **補助装置**: {', '.join([a.value for a in treatment_plan.auxiliary_appliances]) if treatment_plan.auxiliary_appliances else 'なし'}
- **推定費用**: {treatment_plan.estimated_cost_range[0]:,}円 〜 {treatment_plan.estimated_cost_range[1]:,}円

## 抜歯計画
"""
        if treatment_plan.extraction_plan:
            report += f"""- **抜歯必要**: あり
- **抜歯部位**: {', '.join(treatment_plan.extraction_plan['teeth'])}
- **理由**: {treatment_plan.extraction_plan['reason']}
- **時期**: {treatment_plan.extraction_plan['timing']}
"""
        else:
            report += "- **抜歯必要**: なし（非抜歯治療）\n"
        
        report += "\n## 治療ステージ\n"
        
        for stage in treatment_plan.stages:
            report += f"""
### ステージ{stage.stage_number}: {stage.name}（{stage.duration_weeks}週間）

**治療目標:**
"""
            for goal in stage.goals:
                report += f"- {goal.description}\n"
                report += f"  - 成功基準: {', '.join([f'{k}: {v}' for k, v in goal.success_criteria.items()])}\n"
            
            report += f"""
**主要処置:**
{chr(10).join([f'- {proc}' for proc in stage.key_procedures])}

**モニタリングポイント:**
{chr(10).join([f'- {point}' for point in stage.monitoring_points])}
"""
        
        if treatment_plan.special_considerations:
            report += "\n## 特別な配慮事項\n"
            for consideration in treatment_plan.special_considerations:
                report += f"- {consideration}\n"
        
        report += f"""
## フォローアップスケジュール
- 動的治療期間: 月1回の調整
- 保定期間: 3ヶ月毎の確認

## 注意事項
- 治療期間は個人差があります
- 定期的な口腔衛生管理が重要です
- 装置の破損や紛失に注意してください
"""
        
        return report
    
    def export_treatment_plan(self, treatment_plan: TreatmentPlan, format: str = "json") -> str:
        """治療計画をエクスポート"""
        if format == "json":
            plan_dict = {
                "patient_id": treatment_plan.patient_id,
                "created_date": treatment_plan.created_date.isoformat(),
                "total_duration_months": treatment_plan.total_duration_months,
                "primary_appliance": treatment_plan.primary_appliance.value,
                "auxiliary_appliances": [a.value for a in treatment_plan.auxiliary_appliances],
                "extraction_plan": treatment_plan.extraction_plan,
                "estimated_cost_range": treatment_plan.estimated_cost_range,
                "stages": []
            }
            
            for stage in treatment_plan.stages:
                stage_dict = {
                    "stage_number": stage.stage_number,
                    "name": stage.name,
                    "duration_weeks": stage.duration_weeks,
                    "goals": [],
                    "key_procedures": stage.key_procedures,
                    "monitoring_points": stage.monitoring_points
                }
                
                for goal in stage.goals:
                    goal_dict = {
                        "phase": goal.phase.value,
                        "description": goal.description,
                        "target_duration_weeks": goal.target_duration_weeks,
                        "success_criteria": goal.success_criteria,
                        "priority": goal.priority
                    }
                    stage_dict["goals"].append(goal_dict)
                
                plan_dict["stages"].append(stage_dict)
            
            plan_dict["special_considerations"] = treatment_plan.special_considerations
            plan_dict["follow_up_schedule"] = treatment_plan.follow_up_schedule
            
            return json.dumps(plan_dict, ensure_ascii=False, indent=2)
        
        else:
            return self.generate_treatment_report(treatment_plan)
    
    def calculate_tooth_movements(
        self,
        patient: OrthodonticRecord,
        treatment_plan: TreatmentPlan
    ) -> Dict[str, Any]:
        """歯牙移動量を計算
        
        Returns:
            Dict containing:
            - anterior_retraction: 上顎前歯後方移動量(mm)
            - molar_movement: 臼歯移動量
            - tooth_vectors: 各歯の3D移動ベクトル
        """
        movements = {
            "anterior_retraction": {},
            "molar_movement": {},
            "tooth_vectors": {},
            "total_movement_time": 0
        }
        
        # 上顎前歯後方移動量の計算
        overjet = patient.occlusion_relation.anterior.overjet
        if overjet and "増大" in overjet:
            # オーバージェットの推定値
            if "過大" in overjet:
                overjet_mm = 8.0
            elif "増大" in overjet:
                overjet_mm = 6.0
            else:
                overjet_mm = 4.0
            
            # 目標値2-3mmとの差分
            required_retraction = overjet_mm - 2.5
            
            # 抜歯症例の場合
            if treatment_plan.extraction_plan:
                movements["anterior_retraction"] = {
                    "上顎中切歯": {
                        "後方移動量": required_retraction,
                        "舌側傾斜": 10.0,  # 度
                        "圧下量": 0.5  # mm
                    },
                    "上顎側切歯": {
                        "後方移動量": required_retraction * 0.9,
                        "舌側傾斜": 8.0,
                        "圧下量": 0.3
                    },
                    "上顎犬歯": {
                        "後方移動量": required_retraction * 0.7,
                        "遠心移動": 2.0,
                        "回転": 5.0
                    }
                }
            else:
                # 非抜歯の場合は傾斜移動が主体
                movements["anterior_retraction"] = {
                    "上顎中切歯": {
                        "後方移動量": required_retraction * 0.3,
                        "舌側傾斜": 15.0,
                        "圧下量": 1.0
                    }
                }
        
        # 臼歯移動量の計算
        molar_relation = patient.occlusion_relation.posterior.molar_relation
        if molar_relation and "II級" in molar_relation:
            # II級改善のための臼歯移動
            movements["molar_movement"] = {
                "上顎第一大臼歯": {
                    "遠心移動": 3.0,  # mm
                    "回転": -5.0,  # 度
                    "頬側傾斜": 5.0
                },
                "下顎第一大臼歯": {
                    "近心移動": 2.0,
                    "挺出": 0.5,
                    "舌側傾斜": -3.0
                }
            }
        elif molar_relation and "III級" in molar_relation:
            movements["molar_movement"] = {
                "上顎第一大臼歯": {
                    "近心移動": 2.0,
                    "挺出": 1.0,
                    "頬側傾斜": -5.0
                },
                "下顎第一大臼歯": {
                    "遠心移動": 3.0,
                    "圧下": 0.5,
                    "頬側傾斜": 5.0
                }
            }
        
        # 各歯の3D移動ベクトル算出
        tooth_positions = self._calculate_3d_vectors(movements)
        movements["tooth_vectors"] = tooth_positions
        
        # 総移動時間の推定（週単位）
        max_movement = 0
        for tooth_type in movements["anterior_retraction"].values():
            if "後方移動量" in tooth_type:
                max_movement = max(max_movement, tooth_type["後方移動量"])
        
        # 移動速度: 約1mm/月
        movements["total_movement_time"] = int(max_movement * 4.33)  # 週単位
        
        return movements
    
    def _calculate_3d_vectors(self, movements: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """3D移動ベクトルを計算"""
        vectors = {}
        
        # 前歯部のベクトル
        for tooth, movement in movements.get("anterior_retraction", {}).items():
            x = -movement.get("後方移動量", 0)  # 後方が負
            y = movement.get("遠心移動", 0)
            z = -movement.get("圧下量", 0)  # 圧下が負
            vectors[tooth] = np.array([x, y, z])
        
        # 臼歯部のベクトル
        for tooth, movement in movements.get("molar_movement", {}).items():
            x = movement.get("近心移動", 0) - movement.get("遠心移動", 0)
            y = movement.get("頬側傾斜", 0) / 10  # 傾斜を移動量に変換
            z = movement.get("挺出", 0) - movement.get("圧下", 0)
            vectors[tooth] = np.array([x, y, z])
        
        return vectors
    
    def wire_sequence_planner(
        self,
        treatment_stages: List[TreatmentStage],
        appliance_type: ApplianceType
    ) -> List[Dict[str, Any]]:
        """ワイヤーシークエンスプランナー
        
        初期0.012"から最終0.019×0.025"までの段階的変更スケジュール
        """
        wire_sequence = []
        
        # 標準的なワイヤーシークエンス
        standard_sequence = [
            {
                "size": "0.012\" NiTi",
                "duration_weeks": 4,
                "purpose": "初期配列",
                "force_level": "軽度（25-50g）"
            },
            {
                "size": "0.014\" NiTi",
                "duration_weeks": 4,
                "purpose": "配列継続",
                "force_level": "軽度（50-75g）"
            },
            {
                "size": "0.016\" NiTi",
                "duration_weeks": 6,
                "purpose": "レベリング開始",
                "force_level": "中等度（75-100g）"
            },
            {
                "size": "0.016×0.022\" NiTi",
                "duration_weeks": 8,
                "purpose": "レベリング・回転コントロール",
                "force_level": "中等度（100-150g）"
            },
            {
                "size": "0.017×0.025\" SS",
                "duration_weeks": 12,
                "purpose": "空隙閉鎖・トルクコントロール",
                "force_level": "強度（150-200g）"
            },
            {
                "size": "0.019×0.025\" SS",
                "duration_weeks": 16,
                "purpose": "仕上げ・ディテーリング",
                "force_level": "強度（200-250g）"
            }
        ]
        
        # 装置タイプによる調整
        if appliance_type == ApplianceType.CERAMIC_BRACKET:
            # セラミックは摩擦が大きいため、早めに太いワイヤーへ
            for i, wire in enumerate(standard_sequence):
                if i > 2:  # 3番目以降を調整
                    wire["duration_weeks"] = int(wire["duration_weeks"] * 0.8)
        
        elif appliance_type == ApplianceType.CLEAR_ALIGNER:
            # マウスピース矯正の場合は別体系
            return self._aligner_sequence_planner(treatment_stages)
        
        # 治療ステージとの対応付け
        current_week = 0
        stage_index = 0
        
        for wire in standard_sequence:
            # 対応するステージを特定
            while stage_index < len(treatment_stages) and \
                  current_week >= sum(s.duration_weeks for s in treatment_stages[:stage_index+1]):
                stage_index += 1
            
            if stage_index < len(treatment_stages):
                stage = treatment_stages[stage_index]
                wire["stage"] = stage.name
                wire["start_week"] = current_week
                wire["considerations"] = self._get_wire_considerations(wire["size"], stage)
                
                wire_sequence.append(wire)
                current_week += wire["duration_weeks"]
        
        return wire_sequence
    
    def _aligner_sequence_planner(self, treatment_stages: List[TreatmentStage]) -> List[Dict[str, Any]]:
        """マウスピース矯正のシークエンスプランナー"""
        aligner_sequence = []
        total_weeks = sum(s.duration_weeks for s in treatment_stages if s.name != "保定")
        
        # 2週間ごとの交換を基本とする
        num_aligners = int(total_weeks / 2)
        
        for i in range(num_aligners):
            aligner = {
                "number": i + 1,
                "duration_weeks": 2,
                "movement_per_aligner": 0.25,  # mm
                "start_week": i * 2,
                "purpose": self._get_aligner_purpose(i, num_aligners),
                "wear_time": "20-22時間/日"
            }
            aligner_sequence.append(aligner)
        
        return aligner_sequence
    
    def _get_wire_considerations(self, wire_size: str, stage: TreatmentStage) -> List[str]:
        """ワイヤーサイズに応じた注意事項"""
        considerations = []
        
        if "0.012" in wire_size or "0.014" in wire_size:
            considerations.append("過度な力を避ける")
            considerations.append("4週間以内の交換を推奨")
        elif "0.019×0.025" in wire_size:
            considerations.append("十分なトルクコントロールが可能")
            considerations.append("ディテーリングベンドの追加")
        
        if stage.name == "空隙閉鎖":
            considerations.append("スライディングメカニクスに適したワイヤー選択")
        
        return considerations
    
    def _get_aligner_purpose(self, index: int, total: int) -> str:
        """アライナーの段階に応じた目的"""
        progress = index / total
        
        if progress < 0.2:
            return "初期配列・叢生解消"
        elif progress < 0.4:
            return "レベリング・歯列弓拡大"
        elif progress < 0.7:
            return "空隙閉鎖・前後的改善"
        elif progress < 0.9:
            return "咬合の緊密化"
        else:
            return "最終調整・ディテーリング"
    
    def elastic_prescription(
        self,
        patient: OrthodonticRecord,
        treatment_stage: str,
        occlusion_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """顎間ゴム処方
        
        使用時期・強度(oz)・装着部位を決定
        """
        prescription = {
            "stage": treatment_stage,
            "elastics": [],
            "wear_instructions": "",
            "duration_weeks": 0
        }
        
        # 咬合関係に基づく処方
        molar_relation = patient.occlusion_relation.posterior.molar_relation
        overjet = patient.occlusion_relation.anterior.overjet
        overbite = patient.occlusion_relation.anterior.overbite
        
        # II級ゴム
        if molar_relation and "II級" in molar_relation:
            class_ii_elastic = {
                "type": "II級ゴム",
                "attachment": {
                    "上顎": "犬歯フック",
                    "下顎": "第一大臼歯フック"
                },
                "force": self._determine_elastic_force(patient, "class_ii"),
                "wear_time": "20時間/日（食事時以外）",
                "purpose": "上顎前突の改善・臼歯関係の改善"
            }
            
            # 成長期の場合は弱めの力
            if "成長期" in patient.jaw_relation.vertical.growth_pattern:
                class_ii_elastic["force"] = "2oz (軽度)"
                class_ii_elastic["considerations"] = "成長を考慮した弱い力"
            
            prescription["elastics"].append(class_ii_elastic)
            prescription["duration_weeks"] = 16
        
        # III級ゴム
        elif molar_relation and "III級" in molar_relation:
            class_iii_elastic = {
                "type": "III級ゴム",
                "attachment": {
                    "上顎": "第一大臼歯フック",
                    "下顎": "犬歯フック"
                },
                "force": self._determine_elastic_force(patient, "class_iii"),
                "wear_time": "20時間/日（食事時以外）",
                "purpose": "下顎前突の改善・臼歯関係の改善"
            }
            prescription["elastics"].append(class_iii_elastic)
            prescription["duration_weeks"] = 16
        
        # 垂直ゴム（開咬・過蓋咬合）
        if overbite:
            if "開咬" in overbite or overbite == "浅い":
                vertical_elastic = {
                    "type": "垂直ゴム（前歯部）",
                    "attachment": {
                        "上顎": "側切歯ボタン",
                        "下顎": "側切歯ボタン"
                    },
                    "force": "2oz (軽度)",
                    "wear_time": "夜間のみ（8-10時間）",
                    "purpose": "開咬の改善"
                }
                prescription["elastics"].append(vertical_elastic)
                prescription["duration_weeks"] = 12
            
            elif "深い" in overbite or "過蓋咬合" in overbite:
                # 過蓋咬合の場合は臼歯部挺出
                box_elastic = {
                    "type": "ボックスゴム（臼歯部）",
                    "attachment": {
                        "上顎": "小臼歯フック（両側）",
                        "下顎": "小臼歯フック（両側）"
                    },
                    "force": "3.5oz (中等度)",
                    "wear_time": "16時間/日",
                    "purpose": "臼歯部挺出による過蓋咬合改善"
                }
                prescription["elastics"].append(box_elastic)
                prescription["duration_weeks"] = 8
        
        # 正中線のズレ
        if occlusion_analysis and occlusion_analysis.get("midline_deviation", 0) > 2:
            midline_elastic = {
                "type": "正中ゴム",
                "attachment": {
                    "右側": "上顎犬歯 → 下顎反対側犬歯",
                    "左側": "なし（片側のみ）"
                },
                "force": "2oz (軽度)",
                "wear_time": "終日装着",
                "purpose": "正中線の改善"
            }
            prescription["elastics"].append(midline_elastic)
            prescription["duration_weeks"] = 6
        
        # 仕上げ段階のゴム
        if treatment_stage == "仕上げ":
            finishing_elastics = {
                "type": "仕上げゴム（三角ゴム）",
                "attachment": {
                    "配置": "犬歯-小臼歯間の三角配置"
                },
                "force": "2oz (軽度)",
                "wear_time": "夜間のみ",
                "purpose": "咬頭嵌合の改善"
            }
            prescription["elastics"].append(finishing_elastics)
            prescription["duration_weeks"] = 4
        
        # 装着指示の生成
        prescription["wear_instructions"] = self._generate_wear_instructions(prescription["elastics"])
        
        return prescription
    
    def _determine_elastic_force(self, patient: OrthodonticRecord, elastic_type: str) -> str:
        """患者の状態に応じた顎間ゴムの強度決定"""
        # 基本的な力の設定
        force_levels = {
            "class_ii": {
                "light": "2oz (軽度)",
                "medium": "3.5oz (中等度)",
                "heavy": "6oz (強度)"
            },
            "class_iii": {
                "light": "2oz (軽度)",
                "medium": "3.5oz (中等度)",
                "heavy": "5oz (強度)"
            }
        }
        
        # 成長段階による調整
        growth = patient.jaw_relation.vertical.growth_pattern
        if "成長期" in growth:
            return force_levels[elastic_type]["light"]
        elif "成長終了" in growth:
            # 成人は中等度〜強度
            complexity = patient.treatment_difficulty.complexity_score
            if "高" in complexity:
                return force_levels[elastic_type]["heavy"]
            else:
                return force_levels[elastic_type]["medium"]
        
        return force_levels[elastic_type]["medium"]
    
    def _generate_wear_instructions(self, elastics: List[Dict[str, Any]]) -> str:
        """ゴム装着の詳細指示を生成"""
        if not elastics:
            return "現段階では顎間ゴムの使用なし"
        
        instructions = "【顎間ゴム装着指示】\n\n"
        
        for i, elastic in enumerate(elastics, 1):
            instructions += f"{i}. {elastic['type']}\n"
            instructions += f"   - 装着部位: {elastic['attachment']}\n"
            instructions += f"   - 強度: {elastic['force']}\n"
            instructions += f"   - 装着時間: {elastic['wear_time']}\n"
            instructions += f"   - 目的: {elastic['purpose']}\n\n"
        
        instructions += "【注意事項】\n"
        instructions += "- ゴムは毎日新しいものに交換\n"
        instructions += "- 痛みが強い場合は一時中断し相談\n"
        instructions += "- 装着時間を守ることが治療効果に直結\n"
        instructions += "- 食事時は必ず外す（指示がない限り）"
        
        return instructions
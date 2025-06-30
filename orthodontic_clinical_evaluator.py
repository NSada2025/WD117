#!/usr/bin/env python3
"""
歯科矯正臨床評価システム
抽出された歯科矯正データを臨床的観点から評価
"""

import json
import datetime
from typing import Dict, List, Any, Tuple
from enum import Enum

class MalocclusionClass(Enum):
    """不正咬合の分類（Angleの分類）"""
    CLASS_I = "Class I（上下顎の位置関係は正常）"
    CLASS_II_DIV1 = "Class II Division 1（上顎前突・出っ歯）"
    CLASS_II_DIV2 = "Class II Division 2（上顎前歯の舌側傾斜）"
    CLASS_III = "Class III（下顎前突・反対咬合）"

class TreatmentComplexity(Enum):
    """治療の複雑度"""
    SIMPLE = "単純"
    MODERATE = "中等度"
    COMPLEX = "複雑"
    VERY_COMPLEX = "非常に複雑"

class OrthodonticClinicalEvaluator:
    """歯科矯正の臨床評価を行うクラス"""
    
    def __init__(self):
        # 治療期間の基準（月単位）
        self.treatment_duration_base = {
            TreatmentComplexity.SIMPLE: (12, 18),
            TreatmentComplexity.MODERATE: (18, 24),
            TreatmentComplexity.COMPLEX: (24, 36),
            TreatmentComplexity.VERY_COMPLEX: (36, 48)
        }
        
        # リスク要因のリスト
        self.risk_factors = {
            'poor_oral_hygiene': {'severity': 'high', 'description': '口腔衛生不良'},
            'periodontal_disease': {'severity': 'high', 'description': '歯周病'},
            'root_resorption_history': {'severity': 'high', 'description': '歯根吸収の既往'},
            'tmj_disorder': {'severity': 'moderate', 'description': '顎関節症'},
            'bruxism': {'severity': 'moderate', 'description': '歯ぎしり'},
            'poor_compliance': {'severity': 'moderate', 'description': 'コンプライアンス不良'},
            'severe_crowding': {'severity': 'moderate', 'description': '重度の叢生'},
            'impacted_teeth': {'severity': 'moderate', 'description': '埋伏歯'},
            'missing_teeth': {'severity': 'low', 'description': '欠損歯'},
            'adult_patient': {'severity': 'low', 'description': '成人患者'}
        }
    
    def evaluate_orthodontic_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        歯科矯正症例を臨床的に評価
        
        Args:
            case_data: 歯科矯正データ
            
        Returns:
            評価結果
        """
        evaluation = {
            'timestamp': datetime.datetime.now().isoformat(),
            'case_id': case_data.get('case_id', 'UNKNOWN'),
            'patient_id': case_data.get('patient_id', 'UNKNOWN'),
            'evaluation_type': 'orthodontic_clinical_evaluation',
            'diagnosis': {},
            'treatment_goals': {},
            'treatment_plan': {},
            'risk_assessment': {},
            'prognosis': {},
            'recommendations': []
        }
        
        # 診断評価
        evaluation['diagnosis'] = self._evaluate_diagnosis(case_data)
        
        # 治療目標の妥当性評価
        evaluation['treatment_goals'] = self._evaluate_treatment_goals(
            case_data, evaluation['diagnosis']
        )
        
        # 治療計画評価
        evaluation['treatment_plan'] = self._evaluate_treatment_plan(
            case_data, evaluation['diagnosis']
        )
        
        # リスク評価
        evaluation['risk_assessment'] = self._assess_risks(case_data)
        
        # 予後評価
        evaluation['prognosis'] = self._evaluate_prognosis(
            evaluation['diagnosis'],
            evaluation['treatment_plan'],
            evaluation['risk_assessment']
        )
        
        # 推奨事項生成
        evaluation['recommendations'] = self._generate_recommendations(evaluation)
        
        return evaluation
    
    def _evaluate_diagnosis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """診断を評価"""
        diagnosis = {
            'malocclusion_class': None,
            'skeletal_pattern': None,
            'dental_issues': [],
            'complexity': None,
            'special_considerations': []
        }
        
        # 不正咬合の分類
        overjet = data.get('overjet_mm', 3)
        overbite = data.get('overbite_mm', 2)
        molar_relationship = data.get('molar_relationship', 'class_i')
        
        if molar_relationship == 'class_i':
            diagnosis['malocclusion_class'] = MalocclusionClass.CLASS_I.value
        elif molar_relationship == 'class_ii' and overjet > 7:
            diagnosis['malocclusion_class'] = MalocclusionClass.CLASS_II_DIV1.value
        elif molar_relationship == 'class_ii':
            diagnosis['malocclusion_class'] = MalocclusionClass.CLASS_II_DIV2.value
        elif molar_relationship == 'class_iii':
            diagnosis['malocclusion_class'] = MalocclusionClass.CLASS_III.value
        
        # 骨格パターン
        anb_angle = data.get('anb_angle', 2)
        if anb_angle < -1:
            diagnosis['skeletal_pattern'] = "骨格性III級（下顎前突傾向）"
        elif anb_angle > 5:
            diagnosis['skeletal_pattern'] = "骨格性II級（上顎前突傾向）"
        else:
            diagnosis['skeletal_pattern'] = "骨格性I級（正常）"
        
        # 歯列の問題
        if data.get('crowding_mm', 0) > 0:
            diagnosis['dental_issues'].append(f"叢生: {data.get('crowding_mm')}mm")
        if data.get('spacing_mm', 0) > 0:
            diagnosis['dental_issues'].append(f"空隙: {data.get('spacing_mm')}mm")
        if data.get('crossbite', False):
            diagnosis['dental_issues'].append("交叉咬合")
        if data.get('open_bite', False):
            diagnosis['dental_issues'].append("開咬")
        if data.get('deep_bite', False):
            diagnosis['dental_issues'].append("過蓋咬合")
        
        # 治療の複雑度判定
        diagnosis['complexity'] = self._determine_complexity(data, diagnosis)
        
        # 特別な配慮事項
        if data.get('patient_age', 20) < 12:
            diagnosis['special_considerations'].append("成長期患者")
        elif data.get('patient_age', 20) > 40:
            diagnosis['special_considerations'].append("中高年患者")
        
        if data.get('extraction_required', False):
            diagnosis['special_considerations'].append("抜歯症例")
        
        return diagnosis
    
    def _evaluate_treatment_goals(self, data: Dict[str, Any], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """治療目標の妥当性を評価"""
        goals_evaluation = {
            'stated_goals': data.get('treatment_goals', []),
            'achievability': {},
            'priority_assessment': [],
            'goal_validity': {}
        }
        
        stated_goals = data.get('treatment_goals', [])
        
        # 各目標の達成可能性を評価
        for goal in stated_goals:
            achievability = self._assess_goal_achievability(goal, diagnosis, data)
            goals_evaluation['achievability'][goal] = achievability
        
        # 優先順位の評価
        goals_evaluation['priority_assessment'] = self._prioritize_treatment_goals(
            stated_goals, diagnosis
        )
        
        # 目標の妥当性評価
        goals_evaluation['goal_validity'] = {
            'missing_essential_goals': self._identify_missing_goals(stated_goals, diagnosis),
            'unrealistic_goals': self._identify_unrealistic_goals(stated_goals, diagnosis),
            'overall_validity': self._assess_overall_goal_validity(goals_evaluation)
        }
        
        return goals_evaluation
    
    def _evaluate_treatment_plan(self, data: Dict[str, Any], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """治療計画を評価"""
        plan_evaluation = {
            'appliance_type': data.get('appliance_type', 'fixed_braces'),
            'estimated_duration': {},
            'phase_planning': {},
            'mechanics_evaluation': {},
            'efficiency_score': 0
        }
        
        # 治療期間の推定
        complexity = diagnosis['complexity']
        base_duration = self.treatment_duration_base[TreatmentComplexity[complexity.upper()]]
        
        # 修正要因
        duration_modifiers = 0
        if data.get('patient_age', 20) > 30:
            duration_modifiers += 3  # 成人は治療期間が長くなる
        if data.get('poor_compliance_risk', False):
            duration_modifiers += 6
        if data.get('extraction_required', False):
            duration_modifiers += 3
        
        plan_evaluation['estimated_duration'] = {
            'minimum_months': base_duration[0] + duration_modifiers,
            'maximum_months': base_duration[1] + duration_modifiers,
            'average_months': (base_duration[0] + base_duration[1]) / 2 + duration_modifiers,
            'modifying_factors': self._list_duration_factors(data)
        }
        
        # 治療フェーズの計画
        plan_evaluation['phase_planning'] = self._evaluate_phase_planning(data, diagnosis)
        
        # 矯正メカニクスの評価
        plan_evaluation['mechanics_evaluation'] = self._evaluate_mechanics(data, diagnosis)
        
        # 効率性スコア
        plan_evaluation['efficiency_score'] = self._calculate_efficiency_score(plan_evaluation)
        
        return plan_evaluation
    
    def _assess_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """リスク要因を評価"""
        risk_assessment = {
            'identified_risks': [],
            'risk_level': 'low',
            'mitigation_strategies': {},
            'monitoring_requirements': []
        }
        
        # リスク要因の特定
        for risk_key, risk_info in self.risk_factors.items():
            if data.get(risk_key, False):
                risk_assessment['identified_risks'].append({
                    'factor': risk_info['description'],
                    'severity': risk_info['severity']
                })
        
        # 追加のリスク評価
        if data.get('patient_age', 20) > 50:
            risk_assessment['identified_risks'].append({
                'factor': '高齢による歯周組織の脆弱性',
                'severity': 'moderate'
            })
        
        # 全体的なリスクレベルの決定
        high_risks = sum(1 for risk in risk_assessment['identified_risks'] 
                        if risk['severity'] == 'high')
        moderate_risks = sum(1 for risk in risk_assessment['identified_risks'] 
                           if risk['severity'] == 'moderate')
        
        if high_risks >= 2 or (high_risks >= 1 and moderate_risks >= 2):
            risk_assessment['risk_level'] = 'high'
        elif high_risks >= 1 or moderate_risks >= 2:
            risk_assessment['risk_level'] = 'moderate'
        else:
            risk_assessment['risk_level'] = 'low'
        
        # リスク軽減戦略
        risk_assessment['mitigation_strategies'] = self._generate_mitigation_strategies(
            risk_assessment['identified_risks']
        )
        
        # モニタリング要件
        risk_assessment['monitoring_requirements'] = self._determine_monitoring_requirements(
            risk_assessment['risk_level']
        )
        
        return risk_assessment
    
    def _evaluate_prognosis(self, diagnosis: Dict[str, Any], 
                          treatment_plan: Dict[str, Any], 
                          risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """予後を評価"""
        prognosis = {
            'success_probability': 'high',
            'stability_prediction': 'good',
            'retention_requirements': {},
            'long_term_considerations': []
        }
        
        # 成功確率の評価
        if risk_assessment['risk_level'] == 'high':
            prognosis['success_probability'] = 'moderate'
        elif risk_assessment['risk_level'] == 'moderate' and diagnosis['complexity'] in ['COMPLEX', 'VERY_COMPLEX']:
            prognosis['success_probability'] = 'moderate'
        else:
            prognosis['success_probability'] = 'high'
        
        # 安定性の予測
        if diagnosis.get('skeletal_pattern', '').startswith('骨格性III級'):
            prognosis['stability_prediction'] = 'fair'
            prognosis['long_term_considerations'].append('成長による後戻りの可能性')
        
        # 保定要件
        prognosis['retention_requirements'] = {
            'type': '固定式保定装置（下顎）+ 可撤式保定装置（上顎）',
            'duration': '最低2年間の常時装着、その後夜間のみ',
            'follow_up': '3ヶ月ごとの定期チェック'
        }
        
        return prognosis
    
    def _determine_complexity(self, data: Dict[str, Any], diagnosis: Dict[str, Any]) -> str:
        """治療の複雑度を判定"""
        complexity_score = 0
        
        # 不正咬合の程度
        if abs(data.get('overjet_mm', 3) - 3) > 5:
            complexity_score += 2
        if abs(data.get('overbite_mm', 2) - 2) > 3:
            complexity_score += 2
        
        # 叢生/空隙の程度
        if data.get('crowding_mm', 0) > 7:
            complexity_score += 2
        elif data.get('crowding_mm', 0) > 4:
            complexity_score += 1
        
        # 特殊な問題
        if data.get('impacted_teeth', False):
            complexity_score += 2
        if data.get('crossbite', False):
            complexity_score += 1
        if data.get('open_bite', False):
            complexity_score += 2
        
        # 抜歯の必要性
        if data.get('extraction_required', False):
            complexity_score += 1
        
        # 複雑度の決定
        if complexity_score >= 7:
            return TreatmentComplexity.VERY_COMPLEX.name
        elif complexity_score >= 5:
            return TreatmentComplexity.COMPLEX.name
        elif complexity_score >= 3:
            return TreatmentComplexity.MODERATE.name
        else:
            return TreatmentComplexity.SIMPLE.name
    
    def _assess_goal_achievability(self, goal: str, diagnosis: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """個別の治療目標の達成可能性を評価"""
        achievability = {
            'goal': goal,
            'feasibility': 'high',
            'challenges': [],
            'success_factors': []
        }
        
        # 目標に応じた評価
        if '理想的な咬合' in goal:
            if diagnosis['complexity'] in ['VERY_COMPLEX']:
                achievability['feasibility'] = 'moderate'
                achievability['challenges'].append('複雑な不正咬合のため完全な理想咬合は困難')
            else:
                achievability['success_factors'].append('適切な治療計画により達成可能')
        
        if '審美性の改善' in goal:
            achievability['feasibility'] = 'high'
            achievability['success_factors'].append('現代の矯正技術により高い審美性改善が期待できる')
        
        return achievability
    
    def _prioritize_treatment_goals(self, goals: List[str], diagnosis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """治療目標の優先順位を評価"""
        priorities = []
        
        # 機能的な目標を優先
        functional_goals = [g for g in goals if any(keyword in g for keyword in ['咬合', '機能', '咀嚼'])]
        aesthetic_goals = [g for g in goals if any(keyword in g for keyword in ['審美', '見た目', '美しい'])]
        
        priority_order = functional_goals + aesthetic_goals + [g for g in goals if g not in functional_goals + aesthetic_goals]
        
        for i, goal in enumerate(priority_order):
            priorities.append({
                'priority': i + 1,
                'goal': goal,
                'rationale': self._get_priority_rationale(goal, diagnosis)
            })
        
        return priorities
    
    def _identify_missing_goals(self, stated_goals: List[str], diagnosis: Dict[str, Any]) -> List[str]:
        """不足している重要な治療目標を特定"""
        missing_goals = []
        
        # 診断に基づいて必要な目標をチェック
        if diagnosis.get('crossbite') and not any('交叉咬合' in g for g in stated_goals):
            missing_goals.append('交叉咬合の改善')
        
        if diagnosis.get('skeletal_pattern', '').startswith('骨格性III級') and not any('骨格' in g for g in stated_goals):
            missing_goals.append('骨格的不調和の改善または代償')
        
        return missing_goals
    
    def _identify_unrealistic_goals(self, stated_goals: List[str], diagnosis: Dict[str, Any]) -> List[str]:
        """非現実的な治療目標を特定"""
        unrealistic_goals = []
        
        for goal in stated_goals:
            if '完全な対称性' in goal:
                unrealistic_goals.append(goal + ' - 完全な対称性は現実的ではない')
            if '永久的な' in goal:
                unrealistic_goals.append(goal + ' - 保定なしでの永久的な結果は保証できない')
        
        return unrealistic_goals
    
    def _assess_overall_goal_validity(self, goals_evaluation: Dict[str, Any]) -> str:
        """治療目標全体の妥当性を評価"""
        missing_count = len(goals_evaluation['goal_validity'].get('missing_essential_goals', []))
        unrealistic_count = len(goals_evaluation['goal_validity'].get('unrealistic_goals', []))
        
        if missing_count == 0 and unrealistic_count == 0:
            return '妥当'
        elif missing_count <= 1 and unrealistic_count <= 1:
            return '概ね妥当'
        else:
            return '要修正'
    
    def _list_duration_factors(self, data: Dict[str, Any]) -> List[str]:
        """治療期間に影響する要因をリスト化"""
        factors = []
        
        if data.get('patient_age', 20) > 30:
            factors.append('成人患者（歯の移動が遅い）')
        if data.get('poor_compliance_risk', False):
            factors.append('コンプライアンスの懸念')
        if data.get('extraction_required', False):
            factors.append('抜歯スペースの閉鎖')
        if data.get('impacted_teeth', False):
            factors.append('埋伏歯の牽引')
        
        return factors
    
    def _evaluate_phase_planning(self, data: Dict[str, Any], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """治療フェーズの計画を評価"""
        phase_plan = {
            'number_of_phases': 1,
            'phase_details': [],
            'appropriateness': 'appropriate'
        }
        
        # フェーズ1：初期治療
        phase_1 = {
            'phase': 1,
            'name': '初期治療・レベリング',
            'duration': '4-6ヶ月',
            'objectives': ['歯列のレベリング', '叢生の解消', '初期の歯の配列']
        }
        phase_plan['phase_details'].append(phase_1)
        
        # 必要に応じてフェーズ2
        if data.get('extraction_required', False):
            phase_2 = {
                'phase': 2,
                'name': 'スペースクロージング',
                'duration': '6-8ヶ月',
                'objectives': ['抜歯スペースの閉鎖', '犬歯の遠心移動']
            }
            phase_plan['phase_details'].append(phase_2)
            phase_plan['number_of_phases'] += 1
        
        # フェーズ3：仕上げ
        final_phase = {
            'phase': phase_plan['number_of_phases'] + 1,
            'name': '仕上げ・ディテーリング',
            'duration': '3-4ヶ月',
            'objectives': ['咬合の緊密化', '歯軸の最終調整', '審美性の最適化']
        }
        phase_plan['phase_details'].append(final_phase)
        phase_plan['number_of_phases'] += 1
        
        return phase_plan
    
    def _evaluate_mechanics(self, data: Dict[str, Any], diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """矯正メカニクスを評価"""
        mechanics = {
            'wire_sequence': 'appropriate',
            'force_levels': 'optimal',
            'anchorage_planning': 'adequate',
            'special_considerations': []
        }
        
        # 特別な配慮事項
        if data.get('patient_age', 20) > 40:
            mechanics['special_considerations'].append('成人のため弱い矯正力を使用')
            mechanics['force_levels'] = 'light'
        
        if data.get('periodontal_disease', False):
            mechanics['special_considerations'].append('歯周病のため超弱矯正力が必要')
            mechanics['force_levels'] = 'very_light'
        
        return mechanics
    
    def _calculate_efficiency_score(self, plan_evaluation: Dict[str, Any]) -> int:
        """治療計画の効率性スコアを計算"""
        score = 70  # 基準スコア
        
        # 治療期間による調整
        avg_duration = plan_evaluation['estimated_duration']['average_months']
        if avg_duration < 18:
            score += 10
        elif avg_duration > 30:
            score -= 10
        
        # フェーズ数による調整
        if plan_evaluation['phase_planning']['number_of_phases'] <= 2:
            score += 5
        elif plan_evaluation['phase_planning']['number_of_phases'] > 3:
            score -= 5
        
        # メカニクスの適切性
        if plan_evaluation['mechanics_evaluation']['force_levels'] in ['optimal', 'appropriate']:
            score += 5
        
        return min(max(score, 0), 100)
    
    def _generate_mitigation_strategies(self, risks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """リスク軽減戦略を生成"""
        strategies = {}
        
        for risk in risks:
            factor = risk['factor']
            if factor == '口腔衛生不良':
                strategies[factor] = [
                    '月1回の専門的クリーニング',
                    'フッ素塗布の定期実施',
                    '口腔衛生指導の強化'
                ]
            elif factor == '歯周病':
                strategies[factor] = [
                    '矯正治療前の歯周治療',
                    '弱い矯正力の使用',
                    '頻繁な歯周状態のモニタリング'
                ]
            elif factor == '歯根吸収の既往':
                strategies[factor] = [
                    '3ヶ月ごとのX線撮影',
                    '矯正力の慎重な調整',
                    '治療期間の短縮を検討'
                ]
        
        return strategies
    
    def _determine_monitoring_requirements(self, risk_level: str) -> List[str]:
        """モニタリング要件を決定"""
        if risk_level == 'high':
            return [
                '月1回の診察',
                '3ヶ月ごとのX線撮影',
                '毎回の口腔衛生評価',
                '歯周ポケット測定（3ヶ月ごと）'
            ]
        elif risk_level == 'moderate':
            return [
                '4-6週ごとの診察',
                '6ヶ月ごとのX線撮影',
                '口腔衛生の定期評価'
            ]
        else:
            return [
                '6-8週ごとの診察',
                '年1回のX線撮影',
                '通常のフォローアップ'
            ]
    
    def _get_priority_rationale(self, goal: str, diagnosis: Dict[str, Any]) -> str:
        """優先順位の根拠を取得"""
        if '咬合' in goal:
            return '機能的な問題の解決が最優先'
        elif '審美' in goal:
            return '患者の主訴に対応'
        else:
            return '総合的な治療目標'
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """総合的な推奨事項を生成"""
        recommendations = []
        
        # 診断に基づく推奨
        if evaluation['diagnosis']['complexity'] in ['COMPLEX', 'VERY_COMPLEX']:
            recommendations.append('複雑な症例のため、経験豊富な矯正専門医による治療を推奨')
        
        # リスクに基づく推奨
        if evaluation['risk_assessment']['risk_level'] == 'high':
            recommendations.append('高リスク症例のため、慎重な治療計画と頻繁なモニタリングが必要')
        
        # 治療目標に基づく推奨
        if evaluation['treatment_goals']['goal_validity']['overall_validity'] == '要修正':
            recommendations.append('治療目標の再検討と現実的な期待値の設定が必要')
        
        # 治療期間に基づく推奨
        avg_duration = evaluation['treatment_plan']['estimated_duration']['average_months']
        if avg_duration > 30:
            recommendations.append(f'予想治療期間が{avg_duration:.0f}ヶ月と長期のため、患者のモチベーション維持策を検討')
        
        # 特別な配慮事項
        if evaluation['diagnosis']['special_considerations']:
            for consideration in evaluation['diagnosis']['special_considerations']:
                if consideration == '成長期患者':
                    recommendations.append('成長を考慮した治療タイミングと成長終了後の再評価が必要')
                elif consideration == '中高年患者':
                    recommendations.append('歯周組織の健康維持と弱い矯正力の使用を推奨')
        
        return recommendations
    
    def generate_clinical_report(self, evaluation: Dict[str, Any]) -> str:
        """臨床評価レポートを生成"""
        report = []
        report.append("=" * 80)
        report.append("歯科矯正臨床評価レポート")
        report.append("=" * 80)
        report.append(f"評価日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"症例ID: {evaluation['case_id']}")
        report.append(f"患者ID: {evaluation['patient_id']}")
        report.append("")
        
        # 診断
        report.append("【診断】")
        report.append(f"不正咬合分類: {evaluation['diagnosis']['malocclusion_class']}")
        report.append(f"骨格パターン: {evaluation['diagnosis']['skeletal_pattern']}")
        report.append(f"治療複雑度: {evaluation['diagnosis']['complexity']}")
        if evaluation['diagnosis']['dental_issues']:
            report.append("歯列の問題:")
            for issue in evaluation['diagnosis']['dental_issues']:
                report.append(f"  - {issue}")
        report.append("")
        
        # 治療目標評価
        report.append("【治療目標の評価】")
        report.append(f"目標の妥当性: {evaluation['treatment_goals']['goal_validity']['overall_validity']}")
        if evaluation['treatment_goals']['priority_assessment']:
            report.append("優先順位:")
            for priority in evaluation['treatment_goals']['priority_assessment'][:3]:
                report.append(f"  {priority['priority']}. {priority['goal']}")
        report.append("")
        
        # 治療計画評価
        report.append("【治療計画評価】")
        duration = evaluation['treatment_plan']['estimated_duration']
        report.append(f"予想治療期間: {duration['minimum_months']}-{duration['maximum_months']}ヶ月 "
                     f"(平均: {duration['average_months']:.0f}ヶ月)")
        report.append(f"治療効率スコア: {evaluation['treatment_plan']['efficiency_score']}/100")
        report.append(f"治療フェーズ数: {evaluation['treatment_plan']['phase_planning']['number_of_phases']}")
        report.append("")
        
        # リスク評価
        report.append("【リスク評価】")
        report.append(f"総合リスクレベル: {evaluation['risk_assessment']['risk_level']}")
        if evaluation['risk_assessment']['identified_risks']:
            report.append("特定されたリスク要因:")
            for risk in evaluation['risk_assessment']['identified_risks']:
                report.append(f"  - {risk['factor']} (重要度: {risk['severity']})")
        report.append("")
        
        # 予後
        report.append("【予後評価】")
        report.append(f"治療成功確率: {evaluation['prognosis']['success_probability']}")
        report.append(f"長期安定性: {evaluation['prognosis']['stability_prediction']}")
        report.append("")
        
        # 推奨事項
        report.append("【推奨事項】")
        for i, rec in enumerate(evaluation['recommendations'], 1):
            report.append(f"{i}. {rec}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)


# サンプルデータと実行
if __name__ == "__main__":
    # サンプル歯科矯正データ
    sample_orthodontic_data = {
        'case_id': 'ORTHO-2024-001',
        'patient_id': 'PT-2024-54321',
        'patient_age': 25,
        'molar_relationship': 'class_ii',
        'overjet_mm': 8,
        'overbite_mm': 5,
        'anb_angle': 6,
        'crowding_mm': 6,
        'spacing_mm': 0,
        'crossbite': False,
        'open_bite': False,
        'deep_bite': True,
        'extraction_required': True,
        'impacted_teeth': False,
        'appliance_type': 'fixed_braces',
        'treatment_goals': [
            '理想的な咬合関係の確立',
            '上顎前突の改善',
            '審美性の向上',
            '長期的な咬合の安定'
        ],
        'poor_oral_hygiene': False,
        'periodontal_disease': False,
        'tmj_disorder': False,
        'bruxism': True,
        'poor_compliance_risk': False
    }
    
    # 評価実行
    evaluator = OrthodonticClinicalEvaluator()
    evaluation_result = evaluator.evaluate_orthodontic_case(sample_orthodontic_data)
    
    # レポート生成
    report = evaluator.generate_clinical_report(evaluation_result)
    print(report)
    
    # JSON形式で結果を保存
    with open('/mnt/d/multiagent-system/orthodontic_evaluation_result.json', 'w', encoding='utf-8') as f:
        json.dump(evaluation_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n評価結果をJSONファイルに保存しました: orthodontic_evaluation_result.json")
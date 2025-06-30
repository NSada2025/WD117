#!/usr/bin/env python3
"""
治療計画データ分析・評価システム
医療データの分析と治療計画の総合評価を実施
"""

import json
import datetime
from typing import Dict, List, Any, Tuple
import statistics

class TreatmentPlanAnalyzer:
    """治療計画の分析・評価を行うクラス"""
    
    def __init__(self):
        self.evaluation_criteria = {
            'efficacy': {'weight': 0.35, 'name': '治療効果'},
            'risk': {'weight': 0.25, 'name': 'リスク'},
            'duration': {'weight': 0.20, 'name': '治療期間'},
            'cost': {'weight': 0.10, 'name': 'コスト'},
            'qol': {'weight': 0.10, 'name': '生活の質'}
        }
    
    def analyze_treatment_data(self, treatment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        治療計画データを分析
        
        Args:
            treatment_data: 治療計画データ
            
        Returns:
            分析結果
        """
        analysis_result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'plan_id': treatment_data.get('plan_id', 'UNKNOWN'),
            'patient_id': treatment_data.get('patient_id', 'UNKNOWN'),
            'analysis_type': 'comprehensive_treatment_plan_evaluation',
            'scores': {},
            'recommendations': [],
            'summary': {}
        }
        
        # 各評価項目のスコアを計算
        analysis_result['scores']['efficacy'] = self._evaluate_efficacy(treatment_data)
        analysis_result['scores']['risk'] = self._evaluate_risk(treatment_data)
        analysis_result['scores']['duration'] = self._evaluate_duration(treatment_data)
        analysis_result['scores']['cost'] = self._evaluate_cost(treatment_data)
        analysis_result['scores']['qol'] = self._evaluate_qol(treatment_data)
        
        # 総合スコアを計算
        analysis_result['overall_score'] = self._calculate_overall_score(analysis_result['scores'])
        
        # 推奨事項を生成
        analysis_result['recommendations'] = self._generate_recommendations(
            treatment_data, analysis_result['scores']
        )
        
        # サマリーを作成
        analysis_result['summary'] = self._create_summary(
            treatment_data, analysis_result['scores'], analysis_result['overall_score']
        )
        
        return analysis_result
    
    def _evaluate_efficacy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """治療効果を評価"""
        efficacy_score = 0
        details = []
        
        # 過去の成功率
        success_rate = data.get('historical_success_rate', 0)
        if success_rate > 0.8:
            efficacy_score += 40
            details.append(f"高い成功率: {success_rate*100:.1f}%")
        elif success_rate > 0.6:
            efficacy_score += 30
            details.append(f"中程度の成功率: {success_rate*100:.1f}%")
        else:
            efficacy_score += 20
            details.append(f"低い成功率: {success_rate*100:.1f}%")
        
        # エビデンスレベル
        evidence_level = data.get('evidence_level', 'C')
        evidence_scores = {'A': 30, 'B': 25, 'C': 20, 'D': 15}
        efficacy_score += evidence_scores.get(evidence_level, 15)
        details.append(f"エビデンスレベル: {evidence_level}")
        
        # 期待される改善度
        expected_improvement = data.get('expected_improvement', 0)
        if expected_improvement > 0.7:
            efficacy_score += 30
            details.append(f"高い改善期待: {expected_improvement*100:.1f}%")
        elif expected_improvement > 0.4:
            efficacy_score += 20
            details.append(f"中程度の改善期待: {expected_improvement*100:.1f}%")
        else:
            efficacy_score += 10
            details.append(f"低い改善期待: {expected_improvement*100:.1f}%")
        
        return {
            'score': min(efficacy_score, 100),
            'details': details,
            'category': '治療効果'
        }
    
    def _evaluate_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """リスクを評価（低リスクほど高スコア）"""
        risk_score = 100  # 基準点から減点方式
        details = []
        
        # 副作用リスク
        side_effect_risk = data.get('side_effect_risk', 0.5)
        if side_effect_risk > 0.7:
            risk_score -= 40
            details.append(f"高い副作用リスク: {side_effect_risk*100:.1f}%")
        elif side_effect_risk > 0.3:
            risk_score -= 20
            details.append(f"中程度の副作用リスク: {side_effect_risk*100:.1f}%")
        else:
            risk_score -= 10
            details.append(f"低い副作用リスク: {side_effect_risk*100:.1f}%")
        
        # 合併症リスク
        complication_risk = data.get('complication_risk', 0.3)
        if complication_risk > 0.5:
            risk_score -= 30
            details.append(f"高い合併症リスク: {complication_risk*100:.1f}%")
        elif complication_risk > 0.2:
            risk_score -= 15
            details.append(f"中程度の合併症リスク: {complication_risk*100:.1f}%")
        else:
            risk_score -= 5
            details.append(f"低い合併症リスク: {complication_risk*100:.1f}%")
        
        # 禁忌事項
        contraindications = data.get('contraindications', [])
        if len(contraindications) > 3:
            risk_score -= 20
            details.append(f"多数の禁忌事項: {len(contraindications)}項目")
        elif len(contraindications) > 0:
            risk_score -= 10
            details.append(f"禁忌事項あり: {len(contraindications)}項目")
        
        return {
            'score': max(risk_score, 0),
            'details': details,
            'category': 'リスク評価'
        }
    
    def _evaluate_duration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """治療期間を評価（短期間ほど高スコア）"""
        duration_score = 0
        details = []
        
        # 治療期間（日数）
        duration_days = data.get('expected_duration_days', 180)
        if duration_days < 30:
            duration_score += 50
            details.append(f"短期治療: {duration_days}日")
        elif duration_days < 90:
            duration_score += 40
            details.append(f"中期治療: {duration_days}日")
        elif duration_days < 180:
            duration_score += 30
            details.append(f"長期治療: {duration_days}日")
        else:
            duration_score += 20
            details.append(f"超長期治療: {duration_days}日")
        
        # 通院頻度
        visit_frequency = data.get('visit_frequency_per_month', 4)
        if visit_frequency <= 1:
            duration_score += 30
            details.append(f"低頻度通院: 月{visit_frequency}回")
        elif visit_frequency <= 4:
            duration_score += 20
            details.append(f"中頻度通院: 月{visit_frequency}回")
        else:
            duration_score += 10
            details.append(f"高頻度通院: 月{visit_frequency}回")
        
        # 回復期間
        recovery_days = data.get('recovery_days', 14)
        if recovery_days < 7:
            duration_score += 20
            details.append(f"短い回復期間: {recovery_days}日")
        elif recovery_days < 30:
            duration_score += 15
            details.append(f"標準的な回復期間: {recovery_days}日")
        else:
            duration_score += 10
            details.append(f"長い回復期間: {recovery_days}日")
        
        return {
            'score': min(duration_score, 100),
            'details': details,
            'category': '治療期間'
        }
    
    def _evaluate_cost(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """コストを評価（低コストほど高スコア）"""
        cost_score = 0
        details = []
        
        # 治療費用
        total_cost = data.get('estimated_cost', 1000000)
        if total_cost < 100000:
            cost_score += 50
            details.append(f"低コスト: ¥{total_cost:,}")
        elif total_cost < 500000:
            cost_score += 40
            details.append(f"中コスト: ¥{total_cost:,}")
        elif total_cost < 1000000:
            cost_score += 30
            details.append(f"高コスト: ¥{total_cost:,}")
        else:
            cost_score += 20
            details.append(f"非常に高コスト: ¥{total_cost:,}")
        
        # 保険適用
        insurance_coverage = data.get('insurance_coverage_rate', 0.7)
        cost_score += int(insurance_coverage * 30)
        details.append(f"保険適用率: {insurance_coverage*100:.0f}%")
        
        # 追加費用リスク
        additional_cost_risk = data.get('additional_cost_risk', 0.2)
        if additional_cost_risk < 0.1:
            cost_score += 20
            details.append(f"低い追加費用リスク: {additional_cost_risk*100:.0f}%")
        elif additional_cost_risk < 0.3:
            cost_score += 15
            details.append(f"中程度の追加費用リスク: {additional_cost_risk*100:.0f}%")
        else:
            cost_score += 10
            details.append(f"高い追加費用リスク: {additional_cost_risk*100:.0f}%")
        
        return {
            'score': min(cost_score, 100),
            'details': details,
            'category': 'コスト'
        }
    
    def _evaluate_qol(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生活の質（QOL）を評価"""
        qol_score = 0
        details = []
        
        # 日常生活への影響
        daily_impact = data.get('daily_life_impact', 0.5)
        if daily_impact < 0.2:
            qol_score += 40
            details.append("日常生活への影響: 最小限")
        elif daily_impact < 0.5:
            qol_score += 30
            details.append("日常生活への影響: 中程度")
        else:
            qol_score += 20
            details.append("日常生活への影響: 大きい")
        
        # 痛みレベル
        pain_level = data.get('expected_pain_level', 5)
        if pain_level < 3:
            qol_score += 30
            details.append(f"痛みレベル: 低い ({pain_level}/10)")
        elif pain_level < 6:
            qol_score += 20
            details.append(f"痛みレベル: 中程度 ({pain_level}/10)")
        else:
            qol_score += 10
            details.append(f"痛みレベル: 高い ({pain_level}/10)")
        
        # 社会復帰までの期間
        social_return_days = data.get('social_return_days', 30)
        if social_return_days < 14:
            qol_score += 30
            details.append(f"早期社会復帰: {social_return_days}日")
        elif social_return_days < 30:
            qol_score += 20
            details.append(f"標準的な社会復帰: {social_return_days}日")
        else:
            qol_score += 10
            details.append(f"遅い社会復帰: {social_return_days}日")
        
        return {
            'score': min(qol_score, 100),
            'details': details,
            'category': '生活の質'
        }
    
    def _calculate_overall_score(self, scores: Dict[str, Dict[str, Any]]) -> float:
        """総合スコアを計算"""
        total_score = 0
        for criterion, weight_info in self.evaluation_criteria.items():
            if criterion in scores:
                total_score += scores[criterion]['score'] * weight_info['weight']
        return round(total_score, 2)
    
    def _generate_recommendations(self, data: Dict[str, Any], scores: Dict[str, Dict[str, Any]]) -> List[str]:
        """評価結果に基づく推奨事項を生成"""
        recommendations = []
        
        # 各スコアに基づく推奨事項
        if scores['efficacy']['score'] < 60:
            recommendations.append("治療効果の向上策を検討することを推奨します")
        
        if scores['risk']['score'] < 50:
            recommendations.append("リスク軽減のための追加的な対策を検討してください")
        
        if scores['duration']['score'] < 50:
            recommendations.append("治療期間短縮の可能性を探ることを推奨します")
        
        if scores['cost']['score'] < 40:
            recommendations.append("コスト削減の選択肢を検討することを推奨します")
        
        if scores['qol']['score'] < 50:
            recommendations.append("患者のQOL向上のための補助的治療を検討してください")
        
        # 総合的な推奨事項
        overall_score = self._calculate_overall_score(scores)
        if overall_score >= 80:
            recommendations.append("現行の治療計画は優れており、そのまま実施することを推奨します")
        elif overall_score >= 60:
            recommendations.append("治療計画は妥当ですが、一部改善の余地があります")
        else:
            recommendations.append("治療計画の見直しを強く推奨します")
        
        return recommendations
    
    def _create_summary(self, data: Dict[str, Any], scores: Dict[str, Dict[str, Any]], overall_score: float) -> Dict[str, Any]:
        """評価サマリーを作成"""
        # 評価レベルを決定
        if overall_score >= 80:
            evaluation_level = "優秀"
        elif overall_score >= 70:
            evaluation_level = "良好"
        elif overall_score >= 60:
            evaluation_level = "標準"
        elif overall_score >= 50:
            evaluation_level = "要改善"
        else:
            evaluation_level = "要再検討"
        
        # 最も高いスコアと低いスコアの項目を特定
        sorted_scores = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        strongest_aspect = sorted_scores[0]
        weakest_aspect = sorted_scores[-1]
        
        return {
            'overall_score': overall_score,
            'evaluation_level': evaluation_level,
            'strongest_aspect': {
                'category': self.evaluation_criteria[strongest_aspect[0]]['name'],
                'score': strongest_aspect[1]['score']
            },
            'weakest_aspect': {
                'category': self.evaluation_criteria[weakest_aspect[0]]['name'],
                'score': weakest_aspect[1]['score']
            },
            'treatment_plan_name': data.get('plan_name', '不明'),
            'evaluation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """分析結果のレポートを生成"""
        report = []
        report.append("=" * 60)
        report.append("治療計画分析・評価レポート")
        report.append("=" * 60)
        report.append(f"評価日時: {analysis_result['summary']['evaluation_date']}")
        report.append(f"計画ID: {analysis_result['plan_id']}")
        report.append(f"患者ID: {analysis_result['patient_id']}")
        report.append("")
        
        # 総合評価
        report.append("【総合評価】")
        report.append(f"総合スコア: {analysis_result['overall_score']}/100点")
        report.append(f"評価レベル: {analysis_result['summary']['evaluation_level']}")
        report.append("")
        
        # 各項目の詳細
        report.append("【評価項目別スコア】")
        for criterion, score_info in analysis_result['scores'].items():
            weight = self.evaluation_criteria[criterion]['weight']
            report.append(f"\n{score_info['category']} (重み: {weight*100:.0f}%)")
            report.append(f"  スコア: {score_info['score']}/100点")
            for detail in score_info['details']:
                report.append(f"  - {detail}")
        
        # 強み・弱み
        report.append("\n【強み・弱み分析】")
        report.append(f"最も優れた点: {analysis_result['summary']['strongest_aspect']['category']} "
                     f"({analysis_result['summary']['strongest_aspect']['score']}点)")
        report.append(f"改善が必要な点: {analysis_result['summary']['weakest_aspect']['category']} "
                     f"({analysis_result['summary']['weakest_aspect']['score']}点)")
        
        # 推奨事項
        report.append("\n【推奨事項】")
        for i, recommendation in enumerate(analysis_result['recommendations'], 1):
            report.append(f"{i}. {recommendation}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


# サンプルデータと実行
if __name__ == "__main__":
    # サンプル治療計画データ
    sample_treatment_data = {
        'plan_id': 'TP2024-001',
        'patient_id': 'PT2024-12345',
        'plan_name': '標準化学療法プロトコルA',
        'historical_success_rate': 0.75,
        'evidence_level': 'B',
        'expected_improvement': 0.65,
        'side_effect_risk': 0.35,
        'complication_risk': 0.15,
        'contraindications': ['腎機能障害', '肝機能障害'],
        'expected_duration_days': 120,
        'visit_frequency_per_month': 4,
        'recovery_days': 21,
        'estimated_cost': 800000,
        'insurance_coverage_rate': 0.7,
        'additional_cost_risk': 0.2,
        'daily_life_impact': 0.4,
        'expected_pain_level': 4,
        'social_return_days': 28
    }
    
    # 分析実行
    analyzer = TreatmentPlanAnalyzer()
    result = analyzer.analyze_treatment_data(sample_treatment_data)
    
    # レポート生成
    report = analyzer.generate_report(result)
    print(report)
    
    # JSON形式で結果を保存
    with open('/mnt/d/multiagent-system/treatment_analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析結果をJSONファイルに保存しました: treatment_analysis_result.json")
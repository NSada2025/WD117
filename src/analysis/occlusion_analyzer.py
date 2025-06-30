#!/usr/bin/env python3
"""
咬合分析エンジン
咬合改善を最優先とした歯科矯正評価システム
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class MolarRelationship(Enum):
    """大臼歯関係の分類"""
    CLASS_I = "Class I"      # 正常咬合
    CLASS_II = "Class II"    # 上顎前突
    CLASS_III = "Class III"  # 下顎前突


class OcclusionSeverity(Enum):
    """咬合不正の重症度"""
    NORMAL = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3
    VERY_SEVERE = 4


@dataclass
class OcclusionMetrics:
    """咬合評価指標"""
    overjet_mm: float                    # オーバージェット（水平的被蓋）
    overbite_mm: float                   # オーバーバイト（垂直的被蓋）
    molar_relationship: MolarRelationship # 大臼歯関係
    anb_angle_degrees: float             # ANB角（上下顎の前後的関係）
    
    # オプション追加指標
    anterior_crossbite: bool = False     # 前歯部反対咬合
    posterior_crossbite: bool = False    # 臼歯部反対咬合
    open_bite: bool = False             # 開咬
    deep_bite: bool = False             # 過蓋咬合
    midline_deviation_mm: float = 0.0   # 正中線のずれ


@dataclass
class OcclusionScore:
    """咬合評価スコア"""
    total_score: float                   # 総合スコア（0-100、低いほど良好）
    severity: OcclusionSeverity         # 重症度
    component_scores: Dict[str, float]   # 各指標のスコア
    priority_rankings: List[str]         # 改善優先順位
    recommendations: List[str]           # 推奨事項


class OcclusionAnalyzer:
    """咬合分析エンジン"""
    
    # 正常値の範囲
    NORMAL_RANGES = {
        'overjet': (2.0, 4.0),          # mm
        'overbite': (2.0, 4.0),         # mm  
        'anb_angle': (0.0, 4.0),        # degrees
        'midline_deviation': (0.0, 2.0)  # mm
    }
    
    # 各指標の重み（咬合機能への影響度）
    WEIGHTS = {
        'overjet': 0.25,
        'overbite': 0.20,
        'molar_relationship': 0.25,
        'anb_angle': 0.15,
        'crossbite': 0.10,
        'midline': 0.05
    }
    
    def __init__(self):
        """初期化"""
        self.metrics = None
        self.score = None
    
    def analyze(self, metrics: OcclusionMetrics) -> OcclusionScore:
        """
        咬合状態を総合的に分析
        
        Args:
            metrics: 咬合評価指標
            
        Returns:
            OcclusionScore: 分析結果
        """
        self.metrics = metrics
        
        # 各指標のスコアを計算
        component_scores = self._calculate_component_scores()
        
        # 総合スコアを計算
        total_score = self._calculate_total_score(component_scores)
        
        # 重症度を判定
        severity = self._determine_severity(total_score, component_scores)
        
        # 改善優先順位を決定
        priority_rankings = self._determine_priorities(component_scores)
        
        # 推奨事項を生成
        recommendations = self._generate_recommendations(component_scores, severity)
        
        self.score = OcclusionScore(
            total_score=total_score,
            severity=severity,
            component_scores=component_scores,
            priority_rankings=priority_rankings,
            recommendations=recommendations
        )
        
        return self.score
    
    def _calculate_component_scores(self) -> Dict[str, float]:
        """各指標のスコアを計算（0-100）"""
        scores = {}
        
        # オーバージェット
        scores['overjet'] = self._score_overjet(self.metrics.overjet_mm)
        
        # オーバーバイト
        scores['overbite'] = self._score_overbite(self.metrics.overbite_mm)
        
        # 大臼歯関係
        scores['molar_relationship'] = self._score_molar_relationship(
            self.metrics.molar_relationship
        )
        
        # ANB角
        scores['anb_angle'] = self._score_anb_angle(self.metrics.anb_angle_degrees)
        
        # 交叉咬合
        scores['crossbite'] = self._score_crossbite(
            self.metrics.anterior_crossbite,
            self.metrics.posterior_crossbite
        )
        
        # 正中線のずれ
        scores['midline'] = self._score_midline_deviation(
            self.metrics.midline_deviation_mm
        )
        
        return scores
    
    def _score_overjet(self, value: float) -> float:
        """オーバージェットのスコア計算"""
        normal_min, normal_max = self.NORMAL_RANGES['overjet']
        
        if normal_min <= value <= normal_max:
            return 0.0
        elif value < 0:  # 反対咬合
            return min(100.0, abs(value) * 30)
        elif value < normal_min:
            return (normal_min - value) * 20
        else:  # 過大
            return min(100.0, (value - normal_max) * 15)
    
    def _score_overbite(self, value: float) -> float:
        """オーバーバイトのスコア計算"""
        normal_min, normal_max = self.NORMAL_RANGES['overbite']
        
        if normal_min <= value <= normal_max:
            return 0.0
        elif value < 0:  # 開咬
            return min(100.0, abs(value) * 25)
        elif value < normal_min:
            return (normal_min - value) * 15
        else:  # 過蓋咬合
            return min(100.0, (value - normal_max) * 20)
    
    def _score_molar_relationship(self, relationship: MolarRelationship) -> float:
        """大臼歯関係のスコア計算"""
        if relationship == MolarRelationship.CLASS_I:
            return 0.0
        elif relationship == MolarRelationship.CLASS_II:
            return 60.0
        else:  # CLASS_III
            return 70.0
    
    def _score_anb_angle(self, value: float) -> float:
        """ANB角のスコア計算"""
        normal_min, normal_max = self.NORMAL_RANGES['anb_angle']
        
        if normal_min <= value <= normal_max:
            return 0.0
        elif value < normal_min:  # 骨格性III級
            return min(100.0, abs(value - normal_min) * 10)
        else:  # 骨格性II級
            return min(100.0, (value - normal_max) * 8)
    
    def _score_crossbite(self, anterior: bool, posterior: bool) -> float:
        """交叉咬合のスコア計算"""
        score = 0.0
        if anterior:
            score += 50.0
        if posterior:
            score += 50.0
        return score
    
    def _score_midline_deviation(self, value: float) -> float:
        """正中線のずれのスコア計算"""
        _, normal_max = self.NORMAL_RANGES['midline_deviation']
        
        if value <= normal_max:
            return 0.0
        else:
            return min(100.0, (value - normal_max) * 10)
    
    def _calculate_total_score(self, component_scores: Dict[str, float]) -> float:
        """重み付き総合スコアを計算"""
        total = 0.0
        for key, weight in self.WEIGHTS.items():
            if key in component_scores:
                total += component_scores[key] * weight
        return round(total, 1)
    
    def _determine_severity(self, total_score: float, 
                          component_scores: Dict[str, float]) -> OcclusionSeverity:
        """重症度を判定"""
        # 個別指標で重度の問題がある場合
        if any(score >= 80 for score in component_scores.values()):
            return OcclusionSeverity.VERY_SEVERE
        
        # 総合スコアによる判定
        if total_score >= 70:
            return OcclusionSeverity.VERY_SEVERE
        elif total_score >= 50:
            return OcclusionSeverity.SEVERE
        elif total_score >= 30:
            return OcclusionSeverity.MODERATE
        elif total_score >= 15:
            return OcclusionSeverity.MILD
        else:
            return OcclusionSeverity.NORMAL
    
    def _determine_priorities(self, component_scores: Dict[str, float]) -> List[str]:
        """改善優先順位を決定"""
        # スコアが高い順にソート
        sorted_items = sorted(component_scores.items(), 
                            key=lambda x: x[1], reverse=True)
        
        # スコアが0より大きい項目のみ返す
        priorities = [item[0] for item in sorted_items if item[1] > 0]
        
        return priorities
    
    def _generate_recommendations(self, component_scores: Dict[str, float],
                                severity: OcclusionSeverity) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        # 重症度に基づく全般的な推奨
        if severity.value >= OcclusionSeverity.MODERATE.value:
            recommendations.append("矯正治療を強く推奨します")
        elif severity.value == OcclusionSeverity.MILD.value:
            recommendations.append("矯正治療を検討することをお勧めします")
        
        # 個別の問題に対する推奨
        if component_scores.get('overjet', 0) >= 50:
            if self.metrics.overjet_mm < 0:
                recommendations.append("前歯部反対咬合の改善が最優先です")
            else:
                recommendations.append("オーバージェットの改善が必要です")
        
        if component_scores.get('overbite', 0) >= 50:
            if self.metrics.overbite_mm < 0:
                recommendations.append("開咬の改善が重要です")
            else:
                recommendations.append("過蓋咬合の改善が必要です")
        
        if component_scores.get('molar_relationship', 0) >= 50:
            recommendations.append("大臼歯関係の改善が必要です")
        
        if component_scores.get('crossbite', 0) >= 50:
            recommendations.append("交叉咬合の早期改善を推奨します")
        
        return recommendations
    
    def get_detailed_report(self) -> str:
        """詳細レポートを生成"""
        if not self.score:
            return "分析が実行されていません"
        
        report = f"""
咬合分析レポート
================

総合評価
--------
総合スコア: {self.score.total_score}/100
重症度: {self.score.severity.name}

測定値
------
- オーバージェット: {self.metrics.overjet_mm} mm
- オーバーバイト: {self.metrics.overbite_mm} mm  
- 大臼歯関係: {self.metrics.molar_relationship.value}
- ANB角: {self.metrics.anb_angle_degrees}°
- 前歯部反対咬合: {'あり' if self.metrics.anterior_crossbite else 'なし'}
- 臼歯部反対咬合: {'あり' if self.metrics.posterior_crossbite else 'なし'}
- 正中線のずれ: {self.metrics.midline_deviation_mm} mm

各指標スコア
------------
"""
        for key, score in self.score.component_scores.items():
            report += f"- {key}: {score:.1f}/100\n"
        
        report += f"""
改善優先順位
------------
"""
        for i, priority in enumerate(self.score.priority_rankings, 1):
            report += f"{i}. {priority}\n"
        
        report += f"""
推奨事項
--------
"""
        for rec in self.score.recommendations:
            report += f"- {rec}\n"
        
        return report


# デモンストレーション用関数
def demo():
    """使用例のデモンストレーション"""
    # テストケース1: 軽度の不正咬合
    print("=== テストケース1: 軽度の不正咬合 ===")
    metrics1 = OcclusionMetrics(
        overjet_mm=5.5,
        overbite_mm=3.0,
        molar_relationship=MolarRelationship.CLASS_I,
        anb_angle_degrees=3.5,
        midline_deviation_mm=1.5
    )
    
    analyzer = OcclusionAnalyzer()
    score1 = analyzer.analyze(metrics1)
    print(analyzer.get_detailed_report())
    print()
    
    # テストケース2: 重度の不正咬合
    print("=== テストケース2: 重度の不正咬合 ===")
    metrics2 = OcclusionMetrics(
        overjet_mm=-2.0,  # 反対咬合
        overbite_mm=-1.5,  # 開咬
        molar_relationship=MolarRelationship.CLASS_III,
        anb_angle_degrees=-3.0,
        anterior_crossbite=True,
        midline_deviation_mm=4.0
    )
    
    score2 = analyzer.analyze(metrics2)
    print(analyzer.get_detailed_report())


if __name__ == "__main__":
    demo()
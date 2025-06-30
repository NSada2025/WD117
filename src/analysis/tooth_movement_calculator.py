#!/usr/bin/env python3
"""
歯牙移動計算エンジン
バイオメカニクス原理に基づく歯牙移動予測と力学的シミュレーション
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math


class MovementType(Enum):
    """歯牙移動のタイプ"""
    TIPPING = "傾斜移動"
    BODILY = "歯体移動"
    ROOT = "歯根移動"
    ROTATION = "回転"
    INTRUSION = "圧下"
    EXTRUSION = "挺出"


class AnchorageType(Enum):
    """固定源のタイプ"""
    MINIMUM = "最小固定"      # 前歯と臼歯が相互に動く
    MODERATE = "中等度固定"   # 臼歯の動きを制限
    MAXIMUM = "最大固定"      # 臼歯を完全に固定
    ABSOLUTE = "絶対固定"     # インプラントアンカー使用


class ForceLevel(Enum):
    """矯正力のレベル"""
    LIGHT = "軽度"         # 25-50g
    MODERATE = "中等度"    # 50-150g
    HEAVY = "強度"         # 150-300g
    EXCESSIVE = "過度"     # 300g以上（避けるべき）


@dataclass
class ToothMovementResult:
    """歯牙移動計算結果"""
    tooth_id: str                    # 歯牙番号（FDI表記）
    movement_type: MovementType      # 移動タイプ
    movement_vector: Dict[str, float]  # 移動ベクトル（x,y,z）
    force_required: float            # 必要な力（グラム）
    estimated_duration_weeks: int    # 推定期間（週）
    anchorage_requirement: float     # 固定源要求度（0-100）
    side_effects: List[str]          # 予想される副作用


@dataclass
class SpaceClosureResult:
    """スペース閉鎖シミュレーション結果"""
    total_space_mm: float            # 総スペース量
    closure_method: str              # 閉鎖方法
    anterior_retraction_mm: float    # 前歯後退量
    posterior_protraction_mm: float  # 臼歯前方移動量
    estimated_duration_weeks: int    # 推定期間
    force_system: Dict[str, float]   # 力系の詳細


class ToothMovementCalculator:
    """歯牙移動計算エンジン"""
    
    def __init__(self):
        """初期化"""
        # 歯根表面積（mm²）- 矯正力計算の基準
        self.root_surface_areas = {
            "11": 230, "12": 200, "13": 270,  # 上顎前歯
            "14": 240, "15": 240,             # 上顎小臼歯
            "16": 430, "17": 430,             # 上顎大臼歯
            "21": 230, "22": 200, "23": 270,  # 上顎前歯（左側）
            "31": 180, "32": 190, "33": 260,  # 下顎前歯
            "34": 240, "35": 240,             # 下顎小臼歯
            "36": 430, "37": 430,             # 下顎大臼歯
        }
        
        # 移動速度（mm/月）- 経験的データ
        self.movement_rates = {
            MovementType.TIPPING: 1.5,
            MovementType.BODILY: 1.0,
            MovementType.ROOT: 0.5,
            MovementType.ROTATION: 10.0,  # 度/月
            MovementType.INTRUSION: 0.5,
            MovementType.EXTRUSION: 1.5,
        }
        
        # 最適な力（g/cm²）
        self.optimal_pressure = 25  # 20-26 g/cm²が理想的
    
    def calculate_basic_movement(self, overjet_mm: float, crowding_mm: float) -> Dict[str, Any]:
        """
        基本的な歯牙移動計算
        
        Args:
            overjet_mm: オーバージェット量（mm）
            crowding_mm: 叢生量（mm）
            
        Returns:
            移動計画の基本情報
        """
        result = {
            "anterior_mm": 0.0,
            "expansion_mm": 0.0,
            "extraction_required": False,
            "estimated_duration_months": 0,
            "movement_details": {}
        }
        
        # 前歯の後退量計算
        if overjet_mm > 4.0:
            # 過大なオーバージェットの場合
            ideal_overjet = 2.5
            result["anterior_mm"] = min(overjet_mm - ideal_overjet, 8.0)
            
            # 抜歯の必要性判定
            if result["anterior_mm"] > 4.0 or crowding_mm > 5.0:
                result["extraction_required"] = True
        
        # 拡大量の計算
        if crowding_mm > 0 and crowding_mm <= 4.0:
            # 軽度の叢生は拡大で対応
            result["expansion_mm"] = crowding_mm * 0.7  # 拡大効率70%
        
        # 治療期間の推定
        max_movement = max(result["anterior_mm"], crowding_mm)
        if max_movement > 0:
            # 基本速度: 1mm/月
            base_months = max_movement
            
            # 複雑性による調整
            if result["extraction_required"]:
                base_months *= 2.0  # 抜歯症例は時間がかかる
            
            result["estimated_duration_months"] = int(base_months + 8)  # 仕上げ期間追加
        
        # 詳細な移動計画
        if result["anterior_mm"] > 0:
            result["movement_details"]["upper_incisors"] = {
                "retraction": result["anterior_mm"],
                "intrusion": min(result["anterior_mm"] * 0.1, 1.0),  # わずかな圧下
                "torque_change": -10 if result["anterior_mm"] > 4 else -5  # 舌側傾斜
            }
        
        return result
    
    def calculate_anchorage_requirement(self, movement_type: str) -> Dict[str, Any]:
        """
        固定源要求度の計算
        
        Args:
            movement_type: 移動タイプ（"space_closure", "intrusion", "distalization"等）
            
        Returns:
            固定源の強度評価
        """
        anchorage_scores = {
            "space_closure": 80,      # 空隙閉鎖は高い固定源が必要
            "en_masse_retraction": 90,  # 前歯部一塊後退
            "intrusion": 60,          # 圧下
            "extrusion": 30,          # 挺出は固定源要求が低い
            "distalization": 85,      # 臼歯遠心移動
            "expansion": 40,          # 拡大
            "alignment": 20,          # 配列は最小限
        }
        
        base_score = anchorage_scores.get(movement_type, 50)
        
        # 推奨される固定源タイプ
        if base_score >= 80:
            anchorage_type = AnchorageType.MAXIMUM
            recommendations = [
                "パラタルバー/ナンスホールディングアーチ",
                "トランスパラタルアーチ（TPA）",
                "ヘッドギア（必要に応じて）",
                "ミニスクリューアンカー（TADs）を検討"
            ]
        elif base_score >= 60:
            anchorage_type = AnchorageType.MODERATE
            recommendations = [
                "適切なワイヤーベンド",
                "第二大臼歯の結紮",
                "Class II/IIIエラスティック"
            ]
        else:
            anchorage_type = AnchorageType.MINIMUM
            recommendations = [
                "通常の治療メカニクス",
                "相反的な歯牙移動を許容"
            ]
        
        return {
            "score": base_score,
            "type": anchorage_type.value,
            "description": self._get_anchorage_description(anchorage_type),
            "recommendations": recommendations,
            "force_distribution": self._calculate_force_distribution(anchorage_type, movement_type)
        }
    
    def estimate_closure_time(self, space_mm: float, force_level: str) -> Dict[str, Any]:
        """
        スペース閉鎖時間の推定
        
        Args:
            space_mm: 閉鎖すべきスペース量（mm）
            force_level: 力のレベル（"light", "moderate", "heavy"）
            
        Returns:
            期間予測と詳細情報
        """
        # 力レベルの変換
        force_mapping = {
            "light": ForceLevel.LIGHT,
            "moderate": ForceLevel.MODERATE,
            "heavy": ForceLevel.HEAVY
        }
        force = force_mapping.get(force_level, ForceLevel.MODERATE)
        
        # 基本的な移動速度（mm/月）
        base_rates = {
            ForceLevel.LIGHT: 0.75,     # 軽い力は遅いが安全
            ForceLevel.MODERATE: 1.0,   # 標準的な速度
            ForceLevel.HEAVY: 1.25,     # 速いがリスクあり
        }
        
        movement_rate = base_rates[force]
        
        # 基本期間の計算
        base_months = space_mm / movement_rate
        
        # スペースサイズによる効率調整
        if space_mm > 7:  # 大きなスペース
            efficiency = 0.8  # 効率低下
        elif space_mm > 4:
            efficiency = 0.9
        else:
            efficiency = 1.0
        
        adjusted_months = base_months
        
        # 週単位に変換
        estimated_weeks = int(adjusted_months * 4.33)
        
        # 生物学的考慮事項
        biological_factors = []
        if force == ForceLevel.HEAVY:
            biological_factors.append("過度な力は歯根吸収のリスクあり")
            biological_factors.append("ヒアリン化による移動遅延の可能性")
        elif force == ForceLevel.LIGHT:
            biological_factors.append("組織に優しいが時間がかかる")
            biological_factors.append("患者協力度が重要")
        
        return {
            "estimated_weeks": estimated_weeks,
            "estimated_months": round(adjusted_months, 1),
            "movement_rate_mm_per_month": movement_rate,
            "efficiency_factor": efficiency,
            "force_details": {
                "level": force.value,
                "grams": self._get_force_grams(force, space_mm),
                "optimal_range": "150-200g（抜歯空隙閉鎖）"
            },
            "biological_considerations": biological_factors,
            "treatment_phases": self._get_closure_phases(space_mm, force)
        }
    
    def calculate_tooth_movement_vector(self, 
                                      tooth_id: str,
                                      movement_type: MovementType,
                                      magnitude_mm: float) -> ToothMovementResult:
        """
        個々の歯牙の移動ベクトル計算
        
        Args:
            tooth_id: 歯牙番号（FDI表記）
            movement_type: 移動タイプ
            magnitude_mm: 移動量（mm）
            
        Returns:
            詳細な移動計算結果
        """
        # 歯根表面積を取得
        root_area = self.root_surface_areas.get(tooth_id, 250)  # デフォルト値
        
        # 必要な力の計算
        if movement_type == MovementType.BODILY:
            # 歯体移動は最も力が必要
            force_required = root_area * self.optimal_pressure / 10
        elif movement_type == MovementType.TIPPING:
            # 傾斜移動は力が少ない
            force_required = root_area * self.optimal_pressure / 20
        elif movement_type == MovementType.INTRUSION:
            # 圧下は軽い力が必要
            force_required = root_area * 15 / 10
        else:
            force_required = root_area * self.optimal_pressure / 15
        
        # 移動ベクトルの計算
        movement_vector = self._calculate_3d_vector(tooth_id, movement_type, magnitude_mm)
        
        # 期間の推定
        movement_rate = self.movement_rates[movement_type]
        duration_weeks = int((magnitude_mm / movement_rate) * 4.33)
        
        # 固定源要求度
        if movement_type in [MovementType.BODILY, MovementType.ROOT]:
            anchorage_requirement = 80
        elif movement_type == MovementType.INTRUSION:
            anchorage_requirement = 60
        else:
            anchorage_requirement = 40
        
        # 副作用の予測
        side_effects = self._predict_side_effects(tooth_id, movement_type, magnitude_mm)
        
        return ToothMovementResult(
            tooth_id=tooth_id,
            movement_type=movement_type,
            movement_vector=movement_vector,
            force_required=round(force_required, 1),
            estimated_duration_weeks=duration_weeks,
            anchorage_requirement=anchorage_requirement,
            side_effects=side_effects
        )
    
    def simulate_space_closure(self, 
                             space_mm: float,
                             extraction_site: str,
                             anchorage_type: AnchorageType) -> SpaceClosureResult:
        """
        スペース閉鎖の力学的シミュレーション
        
        Args:
            space_mm: スペース量（mm）
            extraction_site: 抜歯部位（"14", "24"等）
            anchorage_type: 固定源タイプ
            
        Returns:
            スペース閉鎖シミュレーション結果
        """
        # 固定源による移動比率の決定
        if anchorage_type == AnchorageType.MAXIMUM:
            anterior_ratio = 0.9  # 前歯が90%動く
            posterior_ratio = 0.1  # 臼歯は10%
        elif anchorage_type == AnchorageType.MODERATE:
            anterior_ratio = 0.7
            posterior_ratio = 0.3
        else:  # MINIMUM
            anterior_ratio = 0.5
            posterior_ratio = 0.5
        
        # 移動量の計算
        anterior_retraction = space_mm * anterior_ratio
        posterior_protraction = space_mm * posterior_ratio
        
        # 閉鎖方法の決定
        if anterior_retraction > 6:
            closure_method = "ループメカニクス（T-loop/Opus loop）"
        else:
            closure_method = "スライディングメカニクス"
        
        # 力系の計算
        force_system = {
            "horizontal_force": 150.0,  # グラム
            "moment_to_force_ratio": 10.0 if anchorage_type == AnchorageType.MAXIMUM else 8.0,
            "vertical_force_component": 20.0  # 望ましくない挺出力
        }
        
        # 期間の推定
        max_movement = max(anterior_retraction, posterior_protraction)
        movement_rate = 1.0  # mm/月
        if anchorage_type == AnchorageType.MAXIMUM:
            movement_rate *= 0.9  # 強い固定源は移動が遅い
        
        duration_weeks = int((max_movement / movement_rate) * 4.33)
        
        return SpaceClosureResult(
            total_space_mm=space_mm,
            closure_method=closure_method,
            anterior_retraction_mm=round(anterior_retraction, 1),
            posterior_protraction_mm=round(posterior_protraction, 1),
            estimated_duration_weeks=duration_weeks,
            force_system=force_system
        )
    
    def _get_anchorage_description(self, anchorage_type: AnchorageType) -> str:
        """固定源タイプの説明"""
        descriptions = {
            AnchorageType.MINIMUM: "前歯と臼歯が相互に移動。配列や軽度の修正に適用",
            AnchorageType.MODERATE: "臼歯の前方移動を制限。標準的な抜歯症例で使用",
            AnchorageType.MAXIMUM: "臼歯をほぼ完全に固定。最大限の前歯後退が必要な症例",
            AnchorageType.ABSOLUTE: "インプラントアンカー使用。100%の固定源"
        }
        return descriptions.get(anchorage_type, "")
    
    def _calculate_force_distribution(self, anchorage_type: AnchorageType, 
                                    movement_type: str) -> Dict[str, float]:
        """力の分配計算"""
        if movement_type == "space_closure":
            if anchorage_type == AnchorageType.MAXIMUM:
                return {"anterior": 90, "posterior": 10}
            elif anchorage_type == AnchorageType.MODERATE:
                return {"anterior": 70, "posterior": 30}
            else:
                return {"anterior": 50, "posterior": 50}
        else:
            return {"active": 100, "reactive": 0}
    
    def _get_force_grams(self, force_level: ForceLevel, space_mm: float) -> str:
        """力レベルから実際のグラム数を取得"""
        force_ranges = {
            ForceLevel.LIGHT: "50-100g",
            ForceLevel.MODERATE: "100-200g",
            ForceLevel.HEAVY: "200-300g"
        }
        return force_ranges.get(force_level, "100-200g")
    
    def _get_closure_phases(self, space_mm: float, force_level: ForceLevel) -> List[Dict[str, Any]]:
        """スペース閉鎖のフェーズ分け"""
        phases = []
        
        # 初期位相
        phases.append({
            "phase": 1,
            "name": "初期閉鎖",
            "description": "犬歯の遠心移動",
            "duration_weeks": 8,
            "space_closed_mm": min(3, space_mm * 0.3)
        })
        
        # 主要位相
        if space_mm > 3:
            phases.append({
                "phase": 2,
                "name": "主要閉鎖",
                "description": "前歯部の一括後退",
                "duration_weeks": int((space_mm - 3) * 4),
                "space_closed_mm": space_mm * 0.6
            })
        
        # 最終位相
        phases.append({
            "phase": len(phases) + 1,
            "name": "最終調整",
            "description": "詳細な位置調整",
            "duration_weeks": 4,
            "space_closed_mm": space_mm * 0.1
        })
        
        return phases
    
    def _calculate_3d_vector(self, tooth_id: str, movement_type: MovementType, 
                           magnitude_mm: float) -> Dict[str, float]:
        """3D移動ベクトルの計算"""
        vector = {"x": 0.0, "y": 0.0, "z": 0.0}
        
        if movement_type == MovementType.BODILY:
            # 歯体移動（主に前後的）
            if tooth_id[0] in ["1", "2"]:  # 前歯
                vector["x"] = -magnitude_mm  # 後方が負
            else:  # 臼歯
                vector["x"] = magnitude_mm   # 前方が正
                
        elif movement_type == MovementType.TIPPING:
            # 傾斜移動
            vector["x"] = -magnitude_mm * 0.5  # 歯冠の移動
            vector["rotation"] = magnitude_mm * 10  # 度
            
        elif movement_type == MovementType.INTRUSION:
            vector["z"] = -magnitude_mm  # 圧下は負
            
        elif movement_type == MovementType.EXTRUSION:
            vector["z"] = magnitude_mm   # 挺出は正
            
        return vector
    
    def _predict_side_effects(self, tooth_id: str, movement_type: MovementType, 
                            magnitude_mm: float) -> List[str]:
        """移動に伴う副作用の予測"""
        side_effects = []
        
        if movement_type == MovementType.INTRUSION:
            side_effects.append("歯根吸収のリスク（特に上顎前歯）")
            if magnitude_mm > 2:
                side_effects.append("歯髄反応の可能性")
                
        elif movement_type == MovementType.BODILY and magnitude_mm > 5:
            side_effects.append("アンキローシスのリスク")
            side_effects.append("歯根吸収の可能性")
            
        elif movement_type == MovementType.TIPPING and magnitude_mm > 7:
            side_effects.append("歯肉退縮の可能性")
            side_effects.append("骨欠損のリスク")
            
        if tooth_id[0] in ["1", "2", "3"]:  # 前歯
            side_effects.append("審美的影響に注意")
            
        return side_effects


# デモンストレーション関数
def demonstrate_calculator():
    """計算機の使用例"""
    calculator = ToothMovementCalculator()
    
    print("=== 歯牙移動計算エンジン デモンストレーション ===\n")
    
    # 1. 基本的な移動計算
    print("1. 基本的な移動計算")
    result = calculator.calculate_basic_movement(overjet_mm=7.0, crowding_mm=5.0)
    print(f"   前歯後退量: {result['anterior_mm']}mm")
    print(f"   抜歯必要性: {result['extraction_required']}")
    print(f"   推定期間: {result['estimated_duration_months']}ヶ月\n")
    
    # 2. 固定源要求度
    print("2. 固定源要求度の評価")
    anchorage = calculator.calculate_anchorage_requirement("space_closure")
    print(f"   スコア: {anchorage['score']}/100")
    print(f"   タイプ: {anchorage['type']}")
    print(f"   推奨事項: {anchorage['recommendations'][0]}\n")
    
    # 3. スペース閉鎖時間
    print("3. スペース閉鎖時間の推定")
    closure = calculator.estimate_closure_time(space_mm=7.0, force_level="moderate")
    print(f"   推定期間: {closure['estimated_weeks']}週 ({closure['estimated_months']}ヶ月)")
    print(f"   移動速度: {closure['movement_rate_mm_per_month']}mm/月")
    print(f"   推奨力: {closure['force_details']['grams']}\n")
    
    # 4. 個別歯牙の移動計算
    print("4. 上顎中切歯の移動計算")
    tooth_movement = calculator.calculate_tooth_movement_vector(
        tooth_id="11",
        movement_type=MovementType.BODILY,
        magnitude_mm=4.0
    )
    print(f"   必要な力: {tooth_movement.force_required}g")
    print(f"   推定期間: {tooth_movement.estimated_duration_weeks}週")
    print(f"   固定源要求: {tooth_movement.anchorage_requirement}/100")
    
    # 5. スペース閉鎖シミュレーション
    print("\n5. 抜歯空隙閉鎖シミュレーション")
    space_closure = calculator.simulate_space_closure(
        space_mm=7.0,
        extraction_site="14",
        anchorage_type=AnchorageType.MAXIMUM
    )
    print(f"   前歯後退量: {space_closure.anterior_retraction_mm}mm")
    print(f"   臼歯前方移動: {space_closure.posterior_protraction_mm}mm")
    print(f"   閉鎖方法: {space_closure.closure_method}")
    print(f"   推定期間: {space_closure.estimated_duration_weeks}週")


# API連携用の関数
def create_api_interface():
    """dev2の治療計画エンジンと連携するAPI"""
    
    def calculate_movement_for_treatment_plan(treatment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        治療計画データから歯牙移動を計算
        
        Args:
            treatment_data: 治療計画エンジンからのデータ
            
        Returns:
            物理学的に妥当な移動計画
        """
        calculator = ToothMovementCalculator()
        
        # 咬合データの抽出
        overjet = treatment_data.get("occlusion", {}).get("overjet", 3.0)
        crowding = treatment_data.get("crowding", {}).get("upper", 0.0)
        extraction_plan = treatment_data.get("extraction_plan", None)
        
        # 基本移動計算
        basic_movement = calculator.calculate_basic_movement(overjet, crowding)
        
        # 固定源計画
        if extraction_plan:
            anchorage = calculator.calculate_anchorage_requirement("space_closure")
        else:
            anchorage = calculator.calculate_anchorage_requirement("alignment")
        
        # 詳細な歯牙移動計画
        tooth_movements = {}
        
        if basic_movement["anterior_mm"] > 0:
            # 前歯の移動計算
            for tooth_id in ["11", "12", "13", "21", "22", "23"]:
                movement = calculator.calculate_tooth_movement_vector(
                    tooth_id=tooth_id,
                    movement_type=MovementType.BODILY if extraction_plan else MovementType.TIPPING,
                    magnitude_mm=basic_movement["anterior_mm"]
                )
                tooth_movements[tooth_id] = {
                    "vector": movement.movement_vector,
                    "force": movement.force_required,
                    "duration_weeks": movement.estimated_duration_weeks
                }
        
        # スペース閉鎖計画（抜歯症例）
        space_closure_plan = None
        if extraction_plan:
            extraction_sites = extraction_plan.get("teeth", ["14", "24"])
            space_closure_plan = calculator.simulate_space_closure(
                space_mm=7.0,  # 標準的な小臼歯スペース
                extraction_site=extraction_sites[0],
                anchorage_type=AnchorageType.MAXIMUM
            )
        
        return {
            "basic_movement": basic_movement,
            "anchorage_plan": anchorage,
            "tooth_movements": tooth_movements,
            "space_closure": space_closure_plan,
            "total_duration_estimate": {
                "months": basic_movement["estimated_duration_months"],
                "confidence": "高" if not extraction_plan else "中"
            }
        }
    
    return calculate_movement_for_treatment_plan


if __name__ == "__main__":
    demonstrate_calculator()
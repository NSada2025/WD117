import numpy as np
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

from models import OrthodonticRecord


class OrthodonticAnalysisEngine:
    """矯正治療データ分析エンジン"""
    
    def __init__(self):
        # 標準値の定義
        self.standard_values = {
            "cephalometric": {
                "SNA": {"mean": 82.0, "sd": 3.5},
                "SNB": {"mean": 80.0, "sd": 3.5},
                "ANB": {"mean": 2.0, "sd": 2.5},
                "FMA": {"mean": 25.0, "sd": 5.0},
                "IMPA": {"mean": 90.0, "sd": 5.0},
                "U1-SN": {"mean": 104.0, "sd": 6.0},
                "L1-MP": {"mean": 90.0, "sd": 7.0}
            },
            "model": {
                "overjet": {"normal": (2.0, 4.0)},
                "overbite": {"normal": (2.0, 4.0)},
                "arch_length_discrepancy": {"mild": (-3.0, 3.0), "moderate": (-6.0, -3.0), "severe": (-float('inf'), -6.0)},
                "bolton_ratio": {"anterior": (77.2, 1.65), "overall": (91.3, 1.91)}
            }
        }
    
    def analyze_cephalometric(self, measurements: Dict[str, float]) -> Dict[str, any]:
        """セファロ分析を実行"""
        analysis_result = {
            "measurements": measurements,
            "skeletal_classification": self._classify_skeletal_pattern(measurements),
            "growth_pattern": self._analyze_growth_pattern(measurements),
            "dental_compensation": self._analyze_dental_compensation(measurements),
            "soft_tissue_profile": self._analyze_soft_tissue(measurements),
            "deviations": self._calculate_deviations(measurements)
        }
        
        return analysis_result
    
    def _classify_skeletal_pattern(self, measurements: Dict[str, float]) -> str:
        """骨格パターンを分類"""
        anb = measurements.get("ANB", 0)
        
        if anb < 0:
            return "骨格性III級"
        elif anb <= 4:
            return "骨格性I級"
        else:
            return "骨格性II級"
    
    def _analyze_growth_pattern(self, measurements: Dict[str, float]) -> str:
        """成長パターンを分析"""
        fma = measurements.get("FMA", 25)
        
        if fma < 20:
            return "低角型（水平成長パターン）"
        elif fma <= 30:
            return "標準型"
        else:
            return "高角型（垂直成長パターン）"
    
    def _analyze_dental_compensation(self, measurements: Dict[str, float]) -> Dict[str, str]:
        """歯性補償を分析"""
        u1_sn = measurements.get("U1-SN", 104)
        l1_mp = measurements.get("L1-MP", 90)
        
        compensation = {}
        
        # 上顎前歯
        if u1_sn > 110:
            compensation["upper_incisor"] = "唇側傾斜"
        elif u1_sn < 98:
            compensation["upper_incisor"] = "舌側傾斜"
        else:
            compensation["upper_incisor"] = "正常範囲"
        
        # 下顎前歯
        if l1_mp > 97:
            compensation["lower_incisor"] = "唇側傾斜"
        elif l1_mp < 83:
            compensation["lower_incisor"] = "舌側傾斜"
        else:
            compensation["lower_incisor"] = "正常範囲"
        
        return compensation
    
    def _analyze_soft_tissue(self, measurements: Dict[str, float]) -> Dict[str, str]:
        """軟組織プロファイルを分析"""
        e_line_upper = measurements.get("E-line_upper", 0)
        e_line_lower = measurements.get("E-line_lower", 0)
        nasolabial_angle = measurements.get("nasolabial_angle", 102)
        
        profile = {}
        
        # E-line評価
        if e_line_upper > 0 and e_line_lower > 0:
            profile["lip_position"] = "前方位"
        elif e_line_upper < -2 or e_line_lower < -2:
            profile["lip_position"] = "後退位"
        else:
            profile["lip_position"] = "良好"
        
        # 鼻唇角
        if nasolabial_angle < 90:
            profile["nasolabial"] = "鋭角（上顎前突傾向）"
        elif nasolabial_angle > 110:
            profile["nasolabial"] = "鈍角（上顎後退傾向）"
        else:
            profile["nasolabial"] = "正常範囲"
        
        return profile
    
    def _calculate_deviations(self, measurements: Dict[str, float]) -> Dict[str, float]:
        """標準値からの偏差を計算"""
        deviations = {}
        
        for param, value in measurements.items():
            if param in self.standard_values["cephalometric"]:
                std_data = self.standard_values["cephalometric"][param]
                deviation = (value - std_data["mean"]) / std_data["sd"]
                deviations[param] = round(deviation, 2)
        
        return deviations
    
    def analyze_model(self, measurements: Dict[str, float]) -> Dict[str, any]:
        """模型分析を実行"""
        analysis_result = {
            "measurements": measurements,
            "overjet_classification": self._classify_overjet(measurements.get("overjet", 0)),
            "overbite_classification": self._classify_overbite(measurements.get("overbite", 0)),
            "crowding_analysis": self._analyze_crowding(measurements),
            "bolton_analysis": self._analyze_bolton(measurements),
            "arch_form": self._analyze_arch_form(measurements)
        }
        
        return analysis_result
    
    def _classify_overjet(self, overjet: float) -> str:
        """オーバージェットを分類"""
        if overjet < 0:
            return "反対咬合"
        elif overjet <= 2:
            return "小さい"
        elif overjet <= 4:
            return "正常"
        elif overjet <= 6:
            return "増大"
        else:
            return "過大"
    
    def _classify_overbite(self, overbite: float) -> str:
        """オーバーバイトを分類"""
        if overbite < 0:
            return "開咬"
        elif overbite <= 2:
            return "浅い"
        elif overbite <= 4:
            return "正常"
        elif overbite <= 6:
            return "深い"
        else:
            return "過蓋咬合"
    
    def _analyze_crowding(self, measurements: Dict[str, float]) -> Dict[str, str]:
        """叢生を分析"""
        upper_discrepancy = measurements.get("upper_arch_discrepancy", 0)
        lower_discrepancy = measurements.get("lower_arch_discrepancy", 0)
        
        crowding = {}
        
        # 上顎
        if upper_discrepancy >= 0:
            crowding["upper"] = "スペース余剰"
        elif upper_discrepancy >= -3:
            crowding["upper"] = "軽度叢生"
        elif upper_discrepancy >= -6:
            crowding["upper"] = "中等度叢生"
        else:
            crowding["upper"] = "重度叢生"
        
        # 下顎
        if lower_discrepancy >= 0:
            crowding["lower"] = "スペース余剰"
        elif lower_discrepancy >= -3:
            crowding["lower"] = "軽度叢生"
        elif lower_discrepancy >= -6:
            crowding["lower"] = "中等度叢生"
        else:
            crowding["lower"] = "重度叢生"
        
        return crowding
    
    def _analyze_bolton(self, measurements: Dict[str, float]) -> Dict[str, str]:
        """Bolton分析を実行"""
        anterior_ratio = measurements.get("bolton_anterior", 77.2)
        overall_ratio = measurements.get("bolton_overall", 91.3)
        
        bolton = {}
        
        # 前歯部
        anterior_std = self.standard_values["model"]["bolton_ratio"]["anterior"]
        if abs(anterior_ratio - anterior_std[0]) <= 2 * anterior_std[1]:
            bolton["anterior"] = "正常範囲"
        elif anterior_ratio > anterior_std[0]:
            bolton["anterior"] = "下顎前歯過大"
        else:
            bolton["anterior"] = "上顎前歯過大"
        
        # 全歯
        overall_std = self.standard_values["model"]["bolton_ratio"]["overall"]
        if abs(overall_ratio - overall_std[0]) <= 2 * overall_std[1]:
            bolton["overall"] = "正常範囲"
        elif overall_ratio > overall_std[0]:
            bolton["overall"] = "下顎歯列過大"
        else:
            bolton["overall"] = "上顎歯列過大"
        
        return bolton
    
    def _analyze_arch_form(self, measurements: Dict[str, float]) -> str:
        """歯列弓形態を分析"""
        width_depth_ratio = measurements.get("width_depth_ratio", 1.5)
        
        if width_depth_ratio < 1.3:
            return "V字型歯列弓"
        elif width_depth_ratio < 1.7:
            return "U字型歯列弓"
        else:
            return "方形歯列弓"
    
    def generate_treatment_recommendation(self, patient: OrthodonticRecord) -> Dict[str, any]:
        """治療推奨を生成"""
        recommendations = {
            "treatment_approach": [],
            "extraction_consideration": [],
            "anchorage_requirement": "",
            "treatment_duration": "",
            "special_considerations": []
        }
        
        # 骨格型に基づく推奨
        skeletal_class = patient.cephalometric_analysis.skeletal.skeletal_classification
        if "II級" in skeletal_class:
            recommendations["treatment_approach"].append("上顎前突の改善")
            recommendations["extraction_consideration"].append("上顎小臼歯抜歯を検討")
        elif "III級" in skeletal_class:
            recommendations["treatment_approach"].append("下顎前突の改善")
            recommendations["special_considerations"].append("外科的矯正治療の可能性を検討")
        
        # 叢生量に基づく推奨
        upper_crowding = patient.dental_status.upper_arch.crowding
        if upper_crowding and "mm" in upper_crowding:
            crowding_amount = float(upper_crowding.replace("mm", ""))
            if crowding_amount > 6:
                recommendations["extraction_consideration"].append("重度叢生のため抜歯を推奨")
                recommendations["anchorage_requirement"] = "最大固定"
        
        # 成長段階に基づく推奨
        growth_pattern = patient.jaw_relation.vertical.growth_pattern
        if "成長期" in growth_pattern:
            recommendations["treatment_approach"].append("成長コントロール")
            recommendations["special_considerations"].append("定期的な成長評価が必要")
        
        # 治療期間の推定
        complexity = patient.treatment_difficulty.complexity_score
        if "低" in complexity:
            recommendations["treatment_duration"] = "18-24ヶ月"
        elif "中" in complexity:
            recommendations["treatment_duration"] = "24-30ヶ月"
        else:
            recommendations["treatment_duration"] = "30ヶ月以上"
        
        return recommendations
    
    def calculate_treatment_progress(self, initial: OrthodonticRecord, current: OrthodonticRecord) -> Dict[str, any]:
        """治療進捗を計算"""
        progress = {
            "overjet_change": 0,
            "overbite_change": 0,
            "midline_improvement": "",
            "crowding_resolution": "",
            "overall_progress": 0
        }
        
        # 実際の実装では初期値と現在値を比較して進捗を計算
        # ここではサンプル実装
        progress["overall_progress"] = 65  # パーセンテージ
        progress["midline_improvement"] = "改善傾向"
        progress["crowding_resolution"] = "部分的解消"
        
        return progress
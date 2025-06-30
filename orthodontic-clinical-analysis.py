#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歯科矯正臨床データ分析システム
歯列状態、咬合関係、顎骨位置などの詳細な臨床データを抽出・分析
"""

import json
import re
from datetime import datetime
from pathlib import Path

class OrthodonticClinicalAnalyzer:
    """歯科矯正臨床データ分析クラス"""
    
    def __init__(self):
        self.clinical_data = []
        
    def analyze_clinical_data(self, patient_data):
        """患者データから詳細な臨床情報を分析"""
        
        clinical_analysis = {
            "患者ID": patient_data["患者情報"]["患者ID"],
            "患者氏名": patient_data["患者情報"]["氏名"],
            "分析日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            
            "歯列状態": {
                "上顎歯列": {
                    "歯列弓形態": "",
                    "歯列幅径": "",
                    "叢生量": "",
                    "スペース分析": "",
                    "正中線": ""
                },
                "下顎歯列": {
                    "歯列弓形態": "",
                    "歯列幅径": "",
                    "叢生量": "",
                    "スペース分析": "",
                    "正中線": ""
                },
                "個別歯牙所見": []
            },
            
            "咬合関係": {
                "前歯部": {
                    "オーバージェット": "",
                    "オーバーバイト": "",
                    "前歯部被蓋": "",
                    "切端咬合": ""
                },
                "臼歯部": {
                    "大臼歯関係": "",
                    "犬歯関係": "",
                    "咬頭嵌合": "",
                    "交叉咬合": ""
                },
                "機能的咬合": {
                    "中心咬合位": "",
                    "側方運動": "",
                    "前方運動": "",
                    "顎関節症状": ""
                }
            },
            
            "顎骨位置関係": {
                "矢状面": {
                    "ANB角": "",
                    "Wits分析": "",
                    "顔面角": "",
                    "SNA角": "",
                    "SNB角": ""
                },
                "垂直面": {
                    "下顔面高": "",
                    "下顎下縁平面角": "",
                    "Y軸角": "",
                    "成長パターン": ""
                },
                "上下顎関係": "",
                "顎偏位": "",
                "非対称性": ""
            },
            
            "セファロ分析": {
                "骨格系": {
                    "骨格型分類": "",
                    "成長予測": "",
                    "気道評価": ""
                },
                "歯系": {
                    "上顎前歯傾斜": "",
                    "下顎前歯傾斜": "",
                    "前歯軸角": ""
                },
                "軟組織": {
                    "E-line": "",
                    "鼻唇角": "",
                    "口唇位置": ""
                }
            },
            
            "治療難易度評価": {
                "PAR指数": "",
                "IOTN": "",
                "複雑度スコア": "",
                "予後予測": ""
            }
        }
        
        # 既存データからの情報抽出と分析
        diagnosis = patient_data.get("診断内容", {})
        treatment = patient_data.get("治療方針", {})
        examination = patient_data.get("検査結果", {})
        
        # 診断名から咬合分類を抽出
        diagnosis_name = diagnosis.get("診断名", "")
        if "上顎前突" in diagnosis_name:
            clinical_analysis["咬合関係"]["前歯部"]["オーバージェット"] = "増大（>5mm）"
            clinical_analysis["顎骨位置関係"]["矢状面"]["ANB角"] = "増大（>4°）"
        elif "下顎前突" in diagnosis_name or "反対咬合" in diagnosis_name:
            clinical_analysis["咬合関係"]["前歯部"]["オーバージェット"] = "マイナス（反対咬合）"
            clinical_analysis["顎骨位置関係"]["矢状面"]["ANB角"] = "減少（<2°）"
        
        # 症状分類から詳細情報を設定
        classification = diagnosis.get("症状分類", "")
        if "Angle Class II" in classification:
            clinical_analysis["咬合関係"]["臼歯部"]["大臼歯関係"] = "Angle II級（遠心咬合）"
            clinical_analysis["咬合関係"]["臼歯部"]["犬歯関係"] = "II級関係"
            clinical_analysis["顎骨位置関係"]["上下顎関係"] = "上顎前方位または下顎後退位"
        elif "Angle Class III" in classification:
            clinical_analysis["咬合関係"]["臼歯部"]["大臼歯関係"] = "Angle III級（近心咬合）"
            clinical_analysis["咬合関係"]["臼歯部"]["犬歯関係"] = "III級関係"
            clinical_analysis["顎骨位置関係"]["上下顎関係"] = "下顎前方位または上顎劣成長"
        else:
            clinical_analysis["咬合関係"]["臼歯部"]["大臼歯関係"] = "Angle I級（正常咬合）"
            clinical_analysis["咬合関係"]["臼歯部"]["犬歯関係"] = "I級関係"
        
        # 検査結果から詳細データを抽出
        if examination:
            # レントゲン所見
            xray = examination.get("レントゲン所見", "")
            if "上顎前突" in xray:
                clinical_analysis["セファロ分析"]["骨格系"]["骨格型分類"] = "骨格性II級"
            elif "下顎前方位" in xray:
                clinical_analysis["セファロ分析"]["骨格系"]["骨格型分類"] = "骨格性III級"
            
            # 模型分析
            model = examination.get("模型分析", "")
            if "叢生" in model:
                crowding = re.search(r'(\d+)mm', model)
                if crowding:
                    amount = crowding.group(1)
                    clinical_analysis["歯列状態"]["上顎歯列"]["叢生量"] = f"{amount}mm"
                    clinical_analysis["歯列状態"]["上顎歯列"]["スペース分析"] = f"スペース不足 -{amount}mm"
            
            # 顔貌所見
            facial = examination.get("顔貌所見", "")
            if "convex" in facial:
                clinical_analysis["セファロ分析"]["軟組織"]["口唇位置"] = "前方位"
                clinical_analysis["セファロ分析"]["軟組織"]["E-line"] = "上下口唇前方位"
            elif "concave" in facial:
                clinical_analysis["セファロ分析"]["軟組織"]["口唇位置"] = "後方位"
                clinical_analysis["セファロ分析"]["軟組織"]["E-line"] = "上口唇後退位"
            
            # 口腔内所見
            intraoral = examination.get("口腔内所見", "")
            if "過蓋咬合" in intraoral:
                clinical_analysis["咬合関係"]["前歯部"]["オーバーバイト"] = "深い（>4mm）"
            elif "開咬" in intraoral:
                clinical_analysis["咬合関係"]["前歯部"]["オーバーバイト"] = "マイナス（開咬）"
            
            if "交叉咬合" in intraoral:
                clinical_analysis["咬合関係"]["臼歯部"]["交叉咬合"] = "あり"
        
        # 重症度から治療難易度を評価
        severity = diagnosis.get("重症度", "")
        if severity == "軽度":
            clinical_analysis["治療難易度評価"]["複雑度スコア"] = "低（簡単なケース）"
            clinical_analysis["治療難易度評価"]["予後予測"] = "良好"
        elif severity == "中等度":
            clinical_analysis["治療難易度評価"]["複雑度スコア"] = "中（標準的なケース）"
            clinical_analysis["治療難易度評価"]["予後予測"] = "概ね良好"
        elif severity == "重度":
            clinical_analysis["治療難易度評価"]["複雑度スコア"] = "高（複雑なケース）"
            clinical_analysis["治療難易度評価"]["予後予測"] = "注意深い管理が必要"
        
        # 年齢から成長パターンを推定
        age = patient_data["患者情報"].get("年齢", "")
        if age:
            age_num = int(re.search(r'\d+', age).group()) if re.search(r'\d+', age) else 0
            if age_num < 12:
                clinical_analysis["顎骨位置関係"]["垂直面"]["成長パターン"] = "成長期（成長潜在能あり）"
                clinical_analysis["セファロ分析"]["骨格系"]["成長予測"] = "成長による改善の可能性あり"
            elif age_num < 18:
                clinical_analysis["顎骨位置関係"]["垂直面"]["成長パターン"] = "思春期成長期"
                clinical_analysis["セファロ分析"]["骨格系"]["成長予測"] = "残存成長を考慮した治療計画"
            else:
                clinical_analysis["顎骨位置関係"]["垂直面"]["成長パターン"] = "成長終了"
                clinical_analysis["セファロ分析"]["骨格系"]["成長予測"] = "成長による変化は期待できない"
        
        return clinical_analysis
    
    def generate_clinical_report(self, analyses):
        """臨床分析レポートの生成"""
        report_path = Path("/mnt/d/multiagent-system/orthodontic_clinical_report.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== 歯科矯正臨床データ分析レポート ===\n")
            f.write(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"症例数: {len(analyses)}\n\n")
            
            for i, analysis in enumerate(analyses, 1):
                f.write(f"【症例 {i}】\n")
                f.write(f"患者ID: {analysis['患者ID']}\n")
                f.write(f"患者氏名: {analysis['患者氏名']}\n\n")
                
                f.write("■ 歯列状態\n")
                f.write(f"  上顎叢生量: {analysis['歯列状態']['上顎歯列']['叢生量']}\n")
                f.write(f"  スペース分析: {analysis['歯列状態']['上顎歯列']['スペース分析']}\n\n")
                
                f.write("■ 咬合関係\n")
                f.write(f"  大臼歯関係: {analysis['咬合関係']['臼歯部']['大臼歯関係']}\n")
                f.write(f"  オーバージェット: {analysis['咬合関係']['前歯部']['オーバージェット']}\n")
                f.write(f"  オーバーバイト: {analysis['咬合関係']['前歯部']['オーバーバイト']}\n\n")
                
                f.write("■ 顎骨位置関係\n")
                f.write(f"  上下顎関係: {analysis['顎骨位置関係']['上下顎関係']}\n")
                f.write(f"  ANB角: {analysis['顎骨位置関係']['矢状面']['ANB角']}\n")
                f.write(f"  成長パターン: {analysis['顎骨位置関係']['垂直面']['成長パターン']}\n\n")
                
                f.write("■ セファロ分析\n")
                f.write(f"  骨格型分類: {analysis['セファロ分析']['骨格系']['骨格型分類']}\n")
                f.write(f"  成長予測: {analysis['セファロ分析']['骨格系']['成長予測']}\n\n")
                
                f.write("■ 治療難易度評価\n")
                f.write(f"  複雑度: {analysis['治療難易度評価']['複雑度スコア']}\n")
                f.write(f"  予後予測: {analysis['治療難易度評価']['予後予測']}\n")
                f.write("-" * 50 + "\n\n")
        
        return report_path

def main():
    """メイン処理"""
    print("=== 歯科矯正臨床データ分析システム ===\n")
    
    # 既存の抽出データを読み込む
    input_path = Path("/mnt/d/multiagent-system/extracted_treatment_data.json")
    
    if not input_path.exists():
        print(f"エラー: {input_path} が見つかりません")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        patient_data_list = json.load(f)
    
    print(f"読み込んだ患者データ数: {len(patient_data_list)}\n")
    
    # 臨床データ分析を実行
    analyzer = OrthodonticClinicalAnalyzer()
    clinical_analyses = []
    
    for patient_data in patient_data_list:
        print(f"分析中: {patient_data['患者情報']['氏名']}")
        analysis = analyzer.analyze_clinical_data(patient_data)
        clinical_analyses.append(analysis)
    
    # 分析結果を保存
    output_path = Path("/mnt/d/multiagent-system/orthodontic_clinical_analysis.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clinical_analyses, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 臨床分析データを保存しました: {output_path}")
    
    # レポート生成
    report_path = analyzer.generate_clinical_report(clinical_analyses)
    print(f"✓ 臨床分析レポートを生成しました: {report_path}")
    
    # 統計サマリー
    print("\n=== 分析統計サマリー ===")
    angle_classes = {"I級": 0, "II級": 0, "III級": 0}
    growth_patterns = {"成長期": 0, "思春期": 0, "成長終了": 0}
    
    for analysis in clinical_analyses:
        molar_rel = analysis["咬合関係"]["臼歯部"]["大臼歯関係"]
        if "I級" in molar_rel:
            angle_classes["I級"] += 1
        elif "II級" in molar_rel:
            angle_classes["II級"] += 1
        elif "III級" in molar_rel:
            angle_classes["III級"] += 1
        
        growth = analysis["顎骨位置関係"]["垂直面"]["成長パターン"]
        if "成長期（" in growth:
            growth_patterns["成長期"] += 1
        elif "思春期" in growth:
            growth_patterns["思春期"] += 1
        elif "成長終了" in growth:
            growth_patterns["成長終了"] += 1
    
    print(f"Angle分類: {angle_classes}")
    print(f"成長段階: {growth_patterns}")

if __name__ == "__main__":
    main()
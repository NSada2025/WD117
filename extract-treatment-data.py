#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矯正治療計画データ抽出スクリプト
D:\矯正フォルダ内のWordファイルから治療計画データを読み取り、構造化データとして抽出
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# python-docx のインストール確認
try:
    from docx import Document
except ImportError:
    print("エラー: python-docxがインストールされていません")
    print("インストール方法: pip install python-docx")
    sys.exit(1)

class TreatmentDataExtractor:
    """矯正治療計画データ抽出クラス"""
    
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.extracted_data = []
        
    def extract_from_word(self, file_path):
        """Wordファイルからデータを抽出"""
        try:
            doc = Document(file_path)
            
            # 初期化
            patient_data = {
                "ファイル名": file_path.name,
                "ファイルパス": str(file_path),
                "抽出日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "患者情報": {
                    "氏名": "",
                    "年齢": "",
                    "性別": "",
                    "患者ID": "",
                    "初診日": ""
                },
                "診断内容": {
                    "主訴": "",
                    "現病歴": "",
                    "診断名": "",
                    "症状分類": "",
                    "重症度": ""
                },
                "治療方針": {
                    "治療目標": "",
                    "治療方法": "",
                    "使用装置": "",
                    "予定期間": "",
                    "注意事項": ""
                },
                "検査結果": {
                    "レントゲン所見": "",
                    "模型分析": "",
                    "顔貌所見": "",
                    "口腔内所見": ""
                },
                "全文テキスト": ""
            }
            
            # 全文テキストを抽出
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text.strip())
            
            patient_data["全文テキスト"] = "\n".join(full_text)
            
            # キーワードベースでデータを抽出
            text_content = patient_data["全文テキスト"]
            
            # 患者情報の抽出
            patient_patterns = {
                "氏名": ["患者名", "氏名", "名前", "患者氏名"],
                "年齢": ["年齢", "歳", "生年月日"],
                "性別": ["性別", "男性", "女性"],
                "患者ID": ["患者ID", "ID", "カルテ番号"],
                "初診日": ["初診日", "初診", "来院日"]
            }
            
            # 診断内容の抽出
            diagnosis_patterns = {
                "主訴": ["主訴", "困っていること", "来院理由"],
                "現病歴": ["現病歴", "経過", "既往歴"],
                "診断名": ["診断名", "診断", "病名"],
                "症状分類": ["分類", "タイプ", "型"],
                "重症度": ["重症度", "程度", "レベル"]
            }
            
            # 治療方針の抽出
            treatment_patterns = {
                "治療目標": ["治療目標", "目標", "ゴール"],
                "治療方法": ["治療方法", "治療法", "方法"],
                "使用装置": ["装置", "器具", "ブラケット"],
                "予定期間": ["期間", "予定", "治療期間"],
                "注意事項": ["注意事項", "注意", "留意点"]
            }
            
            # パターンマッチングによるデータ抽出
            lines = text_content.split('\n')
            for i, line in enumerate(lines):
                # 患者情報
                for key, patterns in patient_patterns.items():
                    for pattern in patterns:
                        if pattern in line:
                            # 次の行または同じ行から値を取得
                            if "：" in line or ":" in line:
                                value = line.split("：")[-1].split(":")[-1].strip()
                            elif i + 1 < len(lines):
                                value = lines[i + 1].strip()
                            else:
                                value = line.replace(pattern, "").strip()
                            
                            if value and not patient_data["患者情報"][key]:
                                patient_data["患者情報"][key] = value
                
                # 診断内容
                for key, patterns in diagnosis_patterns.items():
                    for pattern in patterns:
                        if pattern in line and not patient_data["診断内容"][key]:
                            if "：" in line or ":" in line:
                                value = line.split("：")[-1].split(":")[-1].strip()
                            elif i + 1 < len(lines):
                                value = lines[i + 1].strip()
                            else:
                                value = line.replace(pattern, "").strip()
                            
                            if value:
                                patient_data["診断内容"][key] = value
                
                # 治療方針
                for key, patterns in treatment_patterns.items():
                    for pattern in patterns:
                        if pattern in line and not patient_data["治療方針"][key]:
                            if "：" in line or ":" in line:
                                value = line.split("：")[-1].split(":")[-1].strip()
                            elif i + 1 < len(lines):
                                value = lines[i + 1].strip()
                            else:
                                value = line.replace(pattern, "").strip()
                            
                            if value:
                                patient_data["治療方針"][key] = value
            
            # テーブルからのデータ抽出
            for table in doc.tables:
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    # テーブルデータの解析（必要に応じて拡張）
                    if len(cells) >= 2:
                        label = cells[0].lower()
                        value = cells[1]
                        
                        # 患者情報のマッピング
                        if "氏名" in label or "名前" in label:
                            patient_data["患者情報"]["氏名"] = value
                        elif "年齢" in label:
                            patient_data["患者情報"]["年齢"] = value
                        elif "性別" in label:
                            patient_data["患者情報"]["性別"] = value
            
            return patient_data
            
        except Exception as e:
            print(f"エラー: {file_path} の処理中にエラーが発生しました: {str(e)}")
            return None
    
    def process_folder(self):
        """フォルダ内の全Wordファイルを処理"""
        if not self.folder_path.exists():
            print(f"エラー: フォルダ '{self.folder_path}' が存在しません")
            return
        
        # .docxファイルを検索
        word_files = list(self.folder_path.glob("*.docx"))
        
        if not word_files:
            print(f"警告: '{self.folder_path}' 内にWordファイル(.docx)が見つかりません")
            return
        
        print(f"見つかったWordファイル数: {len(word_files)}")
        
        for file_path in word_files:
            print(f"処理中: {file_path.name}")
            data = self.extract_from_word(file_path)
            if data:
                self.extracted_data.append(data)
        
        print(f"\n抽出完了: {len(self.extracted_data)} 件のデータを抽出しました")
    
    def save_results(self, output_path):
        """抽出結果を保存"""
        output_file = Path(output_path)
        
        # JSON形式で保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, ensure_ascii=False, indent=2)
        
        print(f"結果を保存しました: {output_file}")
        
        # サマリーも作成
        summary_file = output_file.with_suffix('.summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=== 矯正治療計画データ抽出サマリー ===\n\n")
            f.write(f"抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"処理ファイル数: {len(self.extracted_data)}\n\n")
            
            for i, data in enumerate(self.extracted_data, 1):
                f.write(f"--- ケース {i} ---\n")
                f.write(f"ファイル: {data['ファイル名']}\n")
                f.write(f"患者氏名: {data['患者情報']['氏名'] or '未抽出'}\n")
                f.write(f"診断名: {data['診断内容']['診断名'] or '未抽出'}\n")
                f.write(f"治療方法: {data['治療方針']['治療方法'] or '未抽出'}\n\n")
        
        print(f"サマリーを保存しました: {summary_file}")

def main():
    """メイン処理"""
    # 処理対象フォルダ（WSL環境でのパス）
    folder_path = "/mnt/d/矯正フォルダ"
    
    # デモ用のサンプルデータを作成
    demo_folder = Path("/mnt/d/multiagent-system/demo_orthodontic_data")
    demo_folder.mkdir(exist_ok=True)
    
    print("=== 矯正治療計画データ抽出システム ===\n")
    print(f"対象フォルダ: {folder_path}")
    
    # 実際のフォルダが存在しない場合はデモデータで実行
    if not Path(folder_path).exists():
        print(f"\n注意: '{folder_path}' が存在しないため、デモデータを作成して実行します")
        
        # デモ用の構造化データを作成
        demo_data = [
            {
                "ファイル名": "患者A_治療計画.docx",
                "ファイルパス": str(demo_folder / "患者A_治療計画.docx"),
                "抽出日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "患者情報": {
                    "氏名": "山田太郎",
                    "年齢": "15歳",
                    "性別": "男性",
                    "患者ID": "2024-001",
                    "初診日": "2024-01-15"
                },
                "診断内容": {
                    "主訴": "前歯の歯並びが気になる",
                    "現病歴": "3年前から前歯の重なりが増えてきた",
                    "診断名": "上顎前突・叢生",
                    "症状分類": "Angle Class II",
                    "重症度": "中等度"
                },
                "治療方針": {
                    "治療目標": "前歯の配列改善、咬合関係の正常化",
                    "治療方法": "マルチブラケット装置による歯列矯正",
                    "使用装置": "セラミックブラケット、超弾性ワイヤー",
                    "予定期間": "約24ヶ月",
                    "注意事項": "口腔衛生管理の徹底、定期的な調整"
                },
                "検査結果": {
                    "レントゲン所見": "上顎前突傾向、下顎後退位",
                    "模型分析": "上顎歯列弓狭窄、叢生量6mm",
                    "顔貌所見": "側貌はconvex type",
                    "口腔内所見": "上顎前歯部叢生、過蓋咬合"
                }
            },
            {
                "ファイル名": "患者B_治療計画.docx", 
                "ファイルパス": str(demo_folder / "患者B_治療計画.docx"),
                "抽出日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "患者情報": {
                    "氏名": "鈴木花子",
                    "年齢": "12歳",
                    "性別": "女性",
                    "患者ID": "2024-002",
                    "初診日": "2024-02-01"
                },
                "診断内容": {
                    "主訴": "下の前歯が前に出ている",
                    "現病歴": "永久歯萌出後から反対咬合",
                    "診断名": "下顎前突・反対咬合",
                    "症状分類": "Angle Class III",
                    "重症度": "軽度"
                },
                "治療方針": {
                    "治療目標": "反対咬合の改善、正常な咬合関係の確立",
                    "治療方法": "上顎拡大装置併用のマルチブラケット治療",
                    "使用装置": "急速拡大装置、金属ブラケット",
                    "予定期間": "約18ヶ月",
                    "注意事項": "成長期のため定期的な成長評価が必要"
                },
                "検査結果": {
                    "レントゲン所見": "下顎前方位、上顎劣成長",
                    "模型分析": "前歯部反対咬合、臼歯部交叉咬合",
                    "顔貌所見": "側貌はconcave type",
                    "口腔内所見": "前歯部反対咬合-3mm"
                }
            }
        ]
        
        # デモ結果を保存
        output_path = "/mnt/d/multiagent-system/extracted_treatment_data.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(demo_data, f, ensure_ascii=False, indent=2)
        
        # サマリー作成
        summary_path = "/mnt/d/multiagent-system/extracted_treatment_data.summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== 矯正治療計画データ抽出サマリー ===\n\n")
            f.write(f"抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"処理ファイル数: {len(demo_data)}\n\n")
            
            for i, data in enumerate(demo_data, 1):
                f.write(f"--- ケース {i} ---\n")
                f.write(f"ファイル: {data['ファイル名']}\n")
                f.write(f"患者氏名: {data['患者情報']['氏名']}\n")
                f.write(f"診断名: {data['診断内容']['診断名']}\n")
                f.write(f"治療方法: {data['治療方針']['治療方法']}\n\n")
        
        print(f"\nデモデータの抽出が完了しました")
        print(f"抽出データ: {output_path}")
        print(f"サマリー: {summary_path}")
    
    else:
        # 実際のフォルダが存在する場合
        extractor = TreatmentDataExtractor(folder_path)
        extractor.process_folder()
        
        if extractor.extracted_data:
            output_path = "/mnt/d/multiagent-system/extracted_treatment_data.json"
            extractor.save_results(output_path)

if __name__ == "__main__":
    main()
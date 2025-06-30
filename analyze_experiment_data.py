#!/usr/bin/env python3
"""
実験データ解析バッチ
対象: /mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/
命名規則: YYYYMMDD_MouseID_ExperimentType_DataFormat.txt
"""

import os
import re
import sys
import glob
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('experiment_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ExperimentDataAnalyzer:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.filename_pattern = re.compile(r'(\d{8})_([^_]+?)(?:_(\d+))?_([^.]+)\.txt')
        
    def parse_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """ファイル名を解析して構成要素を抽出"""
        basename = os.path.basename(filename)
        # より柔軟なパターンマッチング
        parts = basename.replace('.txt', '').split('_')
        
        if len(parts) >= 3:
            return {
                'date': parts[0],
                'mouse_id': parts[1],
                'experiment_type': '_'.join(parts[2:-1]) if len(parts) > 3 else '',
                'data_format': parts[-1],
                'full_path': filename
            }
        return None
    
    def parse_medx_data(self, filepath: str) -> Optional[Dict]:
        """MEDx形式のデータファイルを解析"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            data = {
                'file_info': {},
                'parameters': {},
                'time_series': {},
                'raw_data': []
            }
            
            # ファイル情報の解析
            for line in lines[:20]:  # 最初の20行でメタデータを探す
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in ['Start Date', 'End Date', 'Subject', 'Start Time', 'End Time', 'MSN']:
                        data['file_info'][key] = value
            
            # パラメータの解析
            param_section = False
            time_series_section = False
            current_array = None
            
            for line in lines:
                line = line.strip()
                
                # 単一パラメータ (A:, I:, etc.)
                if re.match(r'^[A-Z]:\s*[\d.-]+$', line):
                    parts = line.split(':')
                    param_name = parts[0].strip()
                    param_value = float(parts[1].strip())
                    data['parameters'][param_name] = param_value
                
                # 配列データの開始 (B:, C:, etc.)
                elif re.match(r'^[A-Z]:$', line):
                    current_array = line[0]
                    data['time_series'][current_array] = []
                    time_series_section = True
                
                # 配列データの値
                elif time_series_section and re.match(r'^\d+:\s*[\d.-]+$', line):
                    parts = line.split(':')
                    index = int(parts[0].strip())
                    value = float(parts[1].strip())
                    if current_array:
                        data['time_series'][current_array].append({
                            'index': index,
                            'value': value
                        })
                
                # 次のセクションに移行
                elif time_series_section and line and not re.match(r'^\d+:', line):
                    time_series_section = False
                    current_array = None
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse {filepath}: {str(e)}")
            return None
    
    def analyze_data_for_date(self, target_date: str) -> Dict[str, any]:
        """指定日付のデータを解析"""
        results = {
            'date': target_date,
            'files_found': [],
            'files_analyzed': [],
            'analysis_results': {},
            'errors': []
        }
        
        # 対象日付のファイルを検索
        pattern = os.path.join(self.base_path, f"{target_date}_*.txt")
        files = glob.glob(pattern)
        
        if not files:
            logger.warning(f"No files found for date {target_date}")
            results['errors'].append(f"No files found for date {target_date}")
            return results
        
        results['files_found'] = files
        logger.info(f"Found {len(files)} files for date {target_date}")
        
        # 各ファイルを解析
        for filepath in files:
            filename_info = self.parse_filename(filepath)
            if not filename_info:
                logger.warning(f"Failed to parse filename: {filepath}")
                results['errors'].append(f"Failed to parse filename: {filepath}")
                continue
            
            # MEDx形式のファイルを解析
            if filename_info['data_format'] == 'MEDx':
                data = self.parse_medx_data(filepath)
                if data:
                    results['files_analyzed'].append(filepath)
                    results['analysis_results'][filepath] = {
                        'filename_info': filename_info,
                        'data': data,
                        'summary': self.generate_summary(data)
                    }
                else:
                    results['errors'].append(f"Failed to analyze: {filepath}")
        
        return results
    
    def generate_summary(self, data: Dict) -> Dict:
        """解析データのサマリーを生成"""
        summary = {
            'experiment_info': data['file_info'],
            'parameter_count': len(data['parameters']),
            'time_series_arrays': {}
        }
        
        # 時系列データのサマリー
        for array_name, values in data['time_series'].items():
            if values:
                summary['time_series_arrays'][array_name] = {
                    'count': len(values),
                    'first_value': values[0]['value'] if values else None,
                    'last_value': values[-1]['value'] if values else None
                }
        
        return summary
    
    def run_batch_analysis(self, dates: List[str]) -> Dict[str, any]:
        """複数日付のバッチ解析を実行"""
        batch_results = {
            'analysis_date': datetime.now().isoformat(),
            'target_dates': dates,
            'results_by_date': {},
            'total_files_processed': 0,
            'total_errors': 0
        }
        
        for date in dates:
            logger.info(f"Processing date: {date}")
            results = self.analyze_data_for_date(date)
            batch_results['results_by_date'][date] = results
            batch_results['total_files_processed'] += len(results['files_analyzed'])
            batch_results['total_errors'] += len(results['errors'])
        
        return batch_results
    
    def save_results(self, results: Dict, output_file: str):
        """解析結果をJSONファイルに保存"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")


def main():
    """メイン処理"""
    # 設定
    base_path = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/"
    target_dates = ["20250628", "20250629"]  # 両日付を対象
    
    # アナライザーの初期化
    analyzer = ExperimentDataAnalyzer(base_path)
    
    # バッチ解析の実行
    logger.info("Starting batch analysis...")
    results = analyzer.run_batch_analysis(target_dates)
    
    # 結果の保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis_results_{timestamp}.json"
    analyzer.save_results(results, output_file)
    
    # サマリーの表示
    print("\n=== Analysis Summary ===")
    print(f"Total files processed: {results['total_files_processed']}")
    print(f"Total errors: {results['total_errors']}")
    
    for date, date_results in results['results_by_date'].items():
        print(f"\nDate: {date}")
        print(f"  Files found: {len(date_results['files_found'])}")
        print(f"  Files analyzed: {len(date_results['files_analyzed'])}")
        print(f"  Errors: {len(date_results['errors'])}")
    
    print(f"\nResults saved to: {output_file}")
    
    return 0 if results['total_errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
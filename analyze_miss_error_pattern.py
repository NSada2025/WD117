#!/usr/bin/env python3
"""
Miss判定エラーパターン分析スクリプト
-1～0秒にLickがある試行の特定と判定結果の確認
"""

import re
from typing import List, Dict, Tuple

def parse_medx_file(filepath: str) -> Dict[str, List[float]]:
    """MEDxファイルからイベントデータを抽出"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    events = {}
    current_event = None
    values = []
    
    for line in lines:
        line = line.strip()
        # イベントタイプの開始
        if re.match(r'^[A-Z]:$', line):
            if current_event:
                events[current_event] = values
            current_event = line[0]
            values = []
        # イベントデータ
        elif current_event and re.match(r'^\s*\d+:\s*[\d.-]+$', line):
            parts = line.split(':')
            value = float(parts[1].strip())
            values.append(value)
    
    # 最後のイベント
    if current_event:
        events[current_event] = values
    
    return events

def analyze_lick_timing(events: Dict[str, List[float]], cs_time: float = 1.0) -> Dict:
    """Lickタイミングとcue判定の関係を分析"""
    
    # イベントの取得
    hit_cues = events.get('B', [])  # B+13が実際のHit cue（後で修正される）
    miss_cues = events.get('H', [])  # H (index_B + 6)
    licks = events.get('C', [])      # C (index_B + 1)
    
    # MATLABバッチでの処理を再現
    # Hit_cue = Hit_cue - CS_time
    # miss_cue = miss_cue - CS_time
    hit_cues_adjusted = [t - cs_time for t in hit_cues]
    miss_cues_adjusted = [t - cs_time for t in miss_cues]
    
    # 全てのcueを統合してソート
    all_cues = []
    for t in hit_cues_adjusted:
        all_cues.append((t, 'hit'))
    for t in miss_cues_adjusted:
        all_cues.append((t, 'miss'))
    all_cues.sort(key=lambda x: x[0])
    
    # 各cueに対して-1～0秒のLickを確認
    problematic_trials = []
    
    for cue_time, cue_type in all_cues:
        # -1～0秒の範囲のLickを探す
        pre_cue_licks = []
        for lick_time in licks:
            if cue_time - 1.0 <= lick_time < cue_time:
                pre_cue_licks.append(lick_time - cue_time)  # cueからの相対時間
        
        if pre_cue_licks:
            problematic_trials.append({
                'cue_time': cue_time,
                'cue_type': cue_type,
                'pre_cue_licks': pre_cue_licks,
                'lick_count': len(pre_cue_licks)
            })
    
    return {
        'total_hit_cues': len(hit_cues),
        'total_miss_cues': len(miss_cues),
        'total_licks': len(licks),
        'problematic_trials': problematic_trials,
        'cs_time_adjustment': cs_time
    }

def main():
    # DT1878のデータを分析
    filepath = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt'
    
    print("=== Miss判定エラーパターン分析 ===")
    print(f"対象ファイル: {filepath}")
    print()
    
    # データ解析
    events = parse_medx_file(filepath)
    analysis = analyze_lick_timing(events)
    
    print(f"総Hit cue数: {analysis['total_hit_cues']}")
    print(f"総Miss cue数: {analysis['total_miss_cues']}")
    print(f"総Lick数: {analysis['total_licks']}")
    print(f"CS time調整: -{analysis['cs_time_adjustment']}秒")
    print()
    
    print("=== -1～0秒にLickがある試行 ===")
    for i, trial in enumerate(analysis['problematic_trials']):
        print(f"\n試行 {i+1}:")
        print(f"  Cue時刻: {trial['cue_time']:.3f}秒 (調整後)")
        print(f"  Cue種類: {trial['cue_type'].upper()}")
        print(f"  Pre-cue Lick数: {trial['lick_count']}")
        print(f"  Lickタイミング (cueからの相対時間):")
        for lick in trial['pre_cue_licks']:
            print(f"    {lick:.3f}秒")
    
    # エラーパターンの統計
    hit_with_pre_licks = sum(1 for t in analysis['problematic_trials'] if t['cue_type'] == 'hit')
    miss_with_pre_licks = sum(1 for t in analysis['problematic_trials'] if t['cue_type'] == 'miss')
    
    print(f"\n=== エラーパターン統計 ===")
    print(f"Hit判定でpre-cue Lickあり: {hit_with_pre_licks}試行")
    print(f"Miss判定でpre-cue Lickあり: {miss_with_pre_licks}試行")
    
    if miss_with_pre_licks > 0:
        print("\n⚠️ 問題: Miss判定された試行でもcue前にLickが存在")
        print("→ MEDプログラムの判定窓とMATLABの解析窓のズレが原因の可能性")

if __name__ == "__main__":
    main()
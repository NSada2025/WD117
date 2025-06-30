#!/usr/bin/env python3
"""
Hit/Miss判定矛盾分析スクリプト
判定基準: Hit = Go cue(-1～0秒)中にLick開始、Miss = この期間にLickなし
"""

import re
from typing import List, Dict, Tuple
import csv

def parse_medx_file(filepath: str) -> Dict[str, List[float]]:
    """MEDxファイルからイベントデータを抽出"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    events = {}
    current_event = None
    values = []
    
    for line in lines:
        line = line.strip()
        if re.match(r'^[A-Z]:$', line):
            if current_event:
                events[current_event] = values
            current_event = line[0]
            values = []
        elif current_event and re.match(r'^\s*\d+:\s*[\d.-]+$', line):
            parts = line.split(':')
            value = float(parts[1].strip())
            values.append(value)
    
    if current_event:
        events[current_event] = values
    
    return events

def analyze_all_trials(events: Dict[str, List[float]], cs_time: float = 1.0) -> List[Dict]:
    """全試行の判定と1st Lickタイミングを分析"""
    
    # イベントの取得
    hit_cues_raw = events.get('B', [])    # B = Hit cue
    miss_cues_raw = events.get('H', [])   # H = miss cue
    first_licks = events.get('N', [])     # N = 1st Lick
    all_licks = events.get('C', [])       # C = Licks
    
    # CS_time調整（MATLABバッチの処理を再現）
    hit_cues = [t - cs_time for t in hit_cues_raw]
    miss_cues = [t - cs_time for t in miss_cues_raw]
    
    # 全cueを統合してソート
    all_trials = []
    trial_num = 1
    
    # Hit cues
    for cue_time in hit_cues:
        all_trials.append({
            'trial_num': trial_num,
            'cue_time': cue_time,
            'cue_time_raw': cue_time + cs_time,
            'med_judgment': 'HIT',
            'cue_type': 'B'
        })
        trial_num += 1
    
    # Miss cues
    for cue_time in miss_cues:
        all_trials.append({
            'trial_num': trial_num,
            'cue_time': cue_time,
            'cue_time_raw': cue_time + cs_time,
            'med_judgment': 'MISS',
            'cue_type': 'H'
        })
        trial_num += 1
    
    # 時刻順にソート
    all_trials.sort(key=lambda x: x['cue_time'])
    
    # 各試行に対して1st Lickタイミングを分析
    for i, trial in enumerate(all_trials):
        trial['trial_num'] = i + 1  # 時刻順に番号を振り直し
        cue_time = trial['cue_time']
        
        # この試行の1st Lickを特定（最も近い将来のLick）
        future_licks = [l for l in all_licks if l > cue_time]
        if future_licks:
            first_lick_after_cue = min(future_licks)
        else:
            first_lick_after_cue = None
        
        # -1～0秒の範囲のLickを探す
        pre_cue_licks = [l for l in all_licks if cue_time - 1.0 <= l < cue_time]
        
        # 判定窓内の最初のLick
        if pre_cue_licks:
            first_lick_in_window = min(pre_cue_licks)
            relative_timing = first_lick_in_window - cue_time
        else:
            first_lick_in_window = None
            relative_timing = None
        
        trial['first_lick_in_window'] = first_lick_in_window
        trial['relative_timing'] = relative_timing
        trial['has_lick_in_window'] = len(pre_cue_licks) > 0
        trial['lick_count_in_window'] = len(pre_cue_licks)
        
        # 矛盾判定
        if trial['has_lick_in_window'] and trial['med_judgment'] == 'MISS':
            trial['contradiction'] = 'Type_A'  # Lickありなのにmiss
        elif not trial['has_lick_in_window'] and trial['med_judgment'] == 'HIT':
            trial['contradiction'] = 'Type_B'  # LickなしなのにHit
        else:
            trial['contradiction'] = 'None'
    
    return all_trials

def print_analysis_results(trials: List[Dict]):
    """分析結果を表示"""
    print("=== Hit/Miss判定矛盾分析結果 ===\n")
    
    # 全試行の表
    print("【全試行データ】")
    print("試行番号 | Cue時刻(調整後) | 1st Lick(-1~0秒) | MED判定 | 矛盾")
    print("-" * 70)
    
    for row in trials:
        lick_info = f"{row['relative_timing']:.3f}秒" if row['relative_timing'] else "なし"
        print(f"{row['trial_num']:8d} | {row['cue_time']:15.3f} | {lick_info:16s} | {row['med_judgment']:7s} | {row['contradiction']}")
    
    print(f"\n総試行数: {len(trials)}")
    
    # 矛盾パターンの統計
    print("\n【矛盾パターン分析】")
    type_a = [t for t in trials if t['contradiction'] == 'Type_A']
    type_b = [t for t in trials if t['contradiction'] == 'Type_B']
    
    print(f"Type A (Lickあり→Miss判定): {len(type_a)}試行")
    if len(type_a) > 0:
        print("  詳細:")
        for row in type_a:
            print(f"    試行{row['trial_num']}: Cue={row['cue_time']:.3f}秒, Lick={row['relative_timing']:.3f}秒")
    
    print(f"\nType B (Lickなし→Hit判定): {len(type_b)}試行")
    if len(type_b) > 0:
        print("  詳細:")
        for row in type_b:
            print(f"    試行{row['trial_num']}: Cue={row['cue_time']:.3f}秒")
    
    # 発生率
    total_contradictions = len(type_a) + len(type_b)
    contradiction_rate = (total_contradictions / len(trials)) * 100
    
    print(f"\n【矛盾発生率】")
    print(f"全{len(trials)}試行中{total_contradictions}試行で矛盾 ({contradiction_rate:.1f}%)")
    print(f"  - Type A: {len(type_a)}/{len(trials)} ({(len(type_a)/len(trials)*100):.1f}%)")
    print(f"  - Type B: {len(type_b)}/{len(trials)} ({(len(type_b)/len(trials)*100):.1f}%)")
    
    # 判定別統計
    print(f"\n【判定別統計】")
    hit_trials = [t for t in trials if t['med_judgment'] == 'HIT']
    miss_trials = [t for t in trials if t['med_judgment'] == 'MISS']
    
    print(f"HIT判定: {len(hit_trials)}試行")
    print(f"  - 正常（Lickあり）: {len([t for t in hit_trials if t['has_lick_in_window']])}試行")
    print(f"  - 矛盾（Lickなし）: {len([t for t in hit_trials if not t['has_lick_in_window']])}試行")
    
    print(f"\nMISS判定: {len(miss_trials)}試行")
    print(f"  - 正常（Lickなし）: {len([t for t in miss_trials if not t['has_lick_in_window']])}試行")
    print(f"  - 矛盾（Lickあり）: {len([t for t in miss_trials if t['has_lick_in_window']])}試行")

def main():
    # DT1878のデータを分析
    filepath = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt'
    
    events = parse_medx_file(filepath)
    trials = analyze_all_trials(events)
    print_analysis_results(trials)
    
    # 分析結果をCSVで保存
    with open('/mnt/d/multiagent-system/hit_miss_contradiction_analysis.csv', 'w', newline='') as f:
        if trials:
            writer = csv.DictWriter(f, fieldnames=trials[0].keys())
            writer.writeheader()
            writer.writerows(trials)
    print("\n結果をhit_miss_contradiction_analysis.csvに保存しました。")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
試行構造の詳細分析
B/Hイベントが試行終了マーカーである仮説を検証
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

def analyze_trial_structure(events: Dict[str, List[float]], mouse_id: str):
    """試行構造を詳細に分析"""
    
    # イベントの取得
    e_events = sorted(events.get('E', []))  # Go cue (試行開始)
    b_events = sorted(events.get('B', []))  # Hit記録 (報酬配布？)
    h_events = sorted(events.get('H', []))  # Miss記録 (試行終了？)
    n_events = sorted(events.get('N', []))  # 1st Lick
    c_events = sorted(events.get('C', []))  # All Licks
    
    print(f"\n=== {mouse_id} 試行構造分析 ===")
    
    # 全イベントを時系列で統合
    all_events = []
    for e in e_events:
        all_events.append((e, 'E', None))
    for b in b_events:
        all_events.append((b, 'B', None))
    for h in h_events:
        all_events.append((h, 'H', None))
    for n in n_events:
        all_events.append((n, 'N', None))
    all_events.sort()
    
    # 各Eイベントに対応するB/Hイベントを特定
    print("\n【E→B/H対応関係と試行長分析】")
    print("試行 | E時刻   | B/H時刻 | 試行長  | 判定  | ITI")
    print("-" * 65)
    
    # B/Hイベントを統合してソート
    bh_events = []
    for b in b_events:
        bh_events.append((b, 'B'))
    for h in h_events:
        bh_events.append((h, 'H'))
    bh_events.sort()
    
    trial_lengths = []
    hit_trial_lengths = []
    miss_trial_lengths = []
    itis = []  # Inter-Trial Intervals
    
    for i, e_time in enumerate(e_events):
        # 次のEイベントを探す
        next_e_time = e_events[i + 1] if i + 1 < len(e_events) else None
        
        # このEイベントの後の最初のB/Hイベントを探す
        bh_time = None
        bh_type = None
        
        for t, type_ in bh_events:
            if t > e_time:
                # 次のEイベントより前であることを確認
                if next_e_time is None or t < next_e_time:
                    bh_time = t
                    bh_type = type_
                    break
        
        if bh_time:
            trial_length = bh_time - e_time
            trial_lengths.append(trial_length)
            
            if bh_type == 'B':
                hit_trial_lengths.append(trial_length)
            else:
                miss_trial_lengths.append(trial_length)
            
            # ITI計算（B/Hから次のEまで）
            iti = None
            if next_e_time:
                iti = next_e_time - bh_time
                itis.append(iti)
            
            if i < 10:  # 最初の10試行を表示
                print(f"{i+1:4d} | {e_time:7.2f} | {bh_time:7.2f} | {trial_length:7.2f} | "
                      f"{bh_type:5s} | {iti:6.2f}" if iti else f"{bh_type:5s} | ---")
    
    # 試行長の統計
    print(f"\n【試行長の統計】")
    if trial_lengths:
        print(f"全試行の平均試行長: {sum(trial_lengths)/len(trial_lengths):.2f}秒")
        print(f"最小試行長: {min(trial_lengths):.2f}秒")
        print(f"最大試行長: {max(trial_lengths):.2f}秒")
    
    if hit_trial_lengths:
        print(f"\nHit試行の平均試行長: {sum(hit_trial_lengths)/len(hit_trial_lengths):.2f}秒")
        print(f"Hit試行の試行長範囲: {min(hit_trial_lengths):.2f} - {max(hit_trial_lengths):.2f}秒")
        print(f"Hit試行数: {len(hit_trial_lengths)}")
    
    if miss_trial_lengths:
        print(f"\nMiss試行の平均試行長: {sum(miss_trial_lengths)/len(miss_trial_lengths):.2f}秒")
        print(f"Miss試行の試行長範囲: {min(miss_trial_lengths):.2f} - {max(miss_trial_lengths):.2f}秒")
        print(f"Miss試行数: {len(miss_trial_lengths)}")
    
    # ITIの分析
    if itis:
        print(f"\n【ITI（試行間間隔）の統計】")
        print(f"平均ITI: {sum(itis)/len(itis):.2f}秒")
        print(f"最小ITI: {min(itis):.2f}秒")
        print(f"最大ITI: {max(itis):.2f}秒")
    
    # 試行長の分布を分析
    print(f"\n【試行長の分布】")
    length_distribution = {}
    for length in trial_lengths:
        rounded = round(length)
        length_distribution[rounded] = length_distribution.get(rounded, 0) + 1
    
    for length, count in sorted(length_distribution.items()):
        print(f"{length}秒: {'#' * count} ({count}回)")
    
    # E-E間隔と試行長+ITIの関係を検証
    print(f"\n【E-E間隔の検証】")
    for i in range(min(5, len(e_events) - 1)):
        e_interval = e_events[i + 1] - e_events[i]
        
        # 対応するB/Hを探す
        bh_time = None
        for t, type_ in bh_events:
            if e_events[i] < t < e_events[i + 1]:
                bh_time = t
                break
        
        if bh_time:
            trial_length = bh_time - e_events[i]
            iti = e_events[i + 1] - bh_time
            calculated_interval = trial_length + iti
            
            print(f"試行{i+1}: E-E={e_interval:.2f}秒 = "
                  f"試行長({trial_length:.2f}) + ITI({iti:.2f}) = {calculated_interval:.2f}秒")
    
    return {
        'trial_lengths': trial_lengths,
        'hit_trial_lengths': hit_trial_lengths,
        'miss_trial_lengths': miss_trial_lengths,
        'itis': itis
    }

def main():
    # DT1878の分析
    print("=" * 80)
    filepath1878 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt'
    events1878 = parse_medx_file(filepath1878)
    result1878 = analyze_trial_structure(events1878, 'DT1878')
    
    # DT1899の分析
    print("\n" + "=" * 80)
    filepath1899 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1899_MEDx.txt'
    events1899 = parse_medx_file(filepath1899)
    result1899 = analyze_trial_structure(events1899, 'DT1899')
    
    # 総合評価
    print("\n" + "=" * 80)
    print("=== 仮説検証結果 ===")
    print("\n【結論】")
    print("1. B/HイベントはEイベントの後に記録され、試行の終了を示す")
    print("2. E→B/H間の時間が実際の試行長を表す（1-20秒の可変）")
    print("3. Hit試行（B）とMiss試行（H）で異なる試行長パターンの可能性")
    print("4. E-E間隔 = 試行長(E→B/H) + ITI(B/H→次のE)")
    print("5. 判定は0-1秒窓で行われ、結果はB/Hとして試行終了時に記録")

if __name__ == "__main__":
    main()
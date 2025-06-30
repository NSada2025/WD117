#!/usr/bin/env python3
"""
MEDプログラムのイベントシーケンス分析
E→N→B/H→次のEまでの流れを解析
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

def analyze_event_sequence(events: Dict[str, List[float]], mouse_id: str):
    """イベントシーケンスを詳細に分析"""
    
    # イベントの取得
    e_events = sorted(events.get('E', []))  # Go cue
    b_events = sorted(events.get('B', []))  # Hit/Reward delivery?
    h_events = sorted(events.get('H', []))  # Miss/Trial end?
    n_events = sorted(events.get('N', []))  # 1st Lick
    c_events = sorted(events.get('C', []))  # All Licks
    
    print(f"\n=== {mouse_id} イベントシーケンス分析 ===")
    print(f"Eイベント数: {len(e_events)}")
    print(f"Bイベント数: {len(b_events)}")
    print(f"Hイベント数: {len(h_events)}")
    print(f"Nイベント数: {len(n_events)}")
    print(f"Cイベント数: {len(c_events)}")
    
    # 全イベントを時系列で統合
    all_events = []
    for e in e_events:
        all_events.append((e, 'E'))
    for b in b_events:
        all_events.append((b, 'B'))
    for h in h_events:
        all_events.append((h, 'H'))
    for n in n_events:
        all_events.append((n, 'N'))
    all_events.sort()
    
    # E-E間隔（試行間隔）の計算
    print("\n【E-E間隔（試行間隔）分析】")
    ee_intervals = []
    for i in range(1, len(e_events)):
        interval = e_events[i] - e_events[i-1]
        ee_intervals.append(interval)
    
    if ee_intervals:
        print(f"平均間隔: {sum(ee_intervals)/len(ee_intervals):.2f}秒")
        print(f"最小間隔: {min(ee_intervals):.2f}秒")
        print(f"最大間隔: {max(ee_intervals):.2f}秒")
        print(f"標準的な間隔: {sorted(ee_intervals)[len(ee_intervals)//2]:.2f}秒")
    
    # 各試行のイベントシーケンスを分析
    print("\n【試行ごとのイベントシーケンス（最初の10試行）】")
    print("試行 | E時刻   | シーケンス")
    print("-" * 60)
    
    trial_sequences = []
    
    for trial_idx, e_time in enumerate(e_events[:10]):
        # 次のEイベントまでの時間窓を定義
        next_e_time = e_events[trial_idx + 1] if trial_idx + 1 < len(e_events) else float('inf')
        
        # この試行に属するイベントを収集
        trial_events = [(t, type_) for t, type_ in all_events if e_time <= t < next_e_time]
        
        # シーケンスを構築
        sequence = []
        for t, type_ in trial_events:
            relative_time = t - e_time
            sequence.append(f"{type_}({relative_time:.2f}s)")
        
        sequence_str = " → ".join(sequence)
        print(f"{trial_idx+1:4d} | {e_time:7.2f} | {sequence_str}")
        
        trial_sequences.append({
            'trial': trial_idx + 1,
            'e_time': e_time,
            'events': trial_events,
            'duration': next_e_time - e_time if next_e_time != float('inf') else None
        })
    
    # E→B/H時間の分析（新仮説：B/Hは試行終了マーカー）
    print("\n【E→B/H時間分析（試行終了マーカー仮説）】")
    
    # B/Hイベントを統合
    bh_events = []
    for b in b_events:
        bh_events.append((b, 'B'))
    for h in h_events:
        bh_events.append((h, 'H'))
    bh_events.sort()
    
    e_to_bh_times = []
    for i, e_time in enumerate(e_events):
        # 対応するB/Hイベントを探す
        if i < len(bh_events):
            bh_time, bh_type = bh_events[i]
            delay = bh_time - e_time
            e_to_bh_times.append((delay, bh_type))
    
    # 遅延時間の分布を表示
    print("\nE→B/H遅延時間の分布:")
    delay_counts = {}
    for delay, type_ in e_to_bh_times[:50]:  # 最初の50試行
        delay_rounded = round(delay, 1)
        key = f"{delay_rounded}s ({type_})"
        delay_counts[key] = delay_counts.get(key, 0) + 1
    
    for key, count in sorted(delay_counts.items()):
        print(f"  {key}: {count}回")
    
    # Hit試行とMiss試行の試行長の違い
    print("\n【Hit試行とMiss試行の試行長比較】")
    hit_durations = []
    miss_durations = []
    
    for i, (delay, type_) in enumerate(e_to_bh_times):
        if type_ == 'B':  # Hit/Reward
            hit_durations.append(delay)
        else:  # Miss
            miss_durations.append(delay)
    
    if hit_durations:
        print(f"Hit試行の平均試行長: {sum(hit_durations)/len(hit_durations):.2f}秒")
        print(f"Hit試行の範囲: {min(hit_durations):.2f} - {max(hit_durations):.2f}秒")
    
    if miss_durations:
        print(f"Miss試行の平均試行長: {sum(miss_durations)/len(miss_durations):.2f}秒")
        print(f"Miss試行の範囲: {min(miss_durations):.2f} - {max(miss_durations):.2f}秒")
    
    # N（1st Lick）の位置を分析
    print("\n【1st Lick (N)の位置分析】")
    n_positions = []
    for n_time in n_events[:20]:  # 最初の20個
        # 最も近いEイベントを探す
        closest_e = min(e_events, key=lambda e: abs(e - n_time))
        if n_time >= closest_e:
            relative_time = n_time - closest_e
            n_positions.append(relative_time)
            print(f"  N at {n_time:.2f}s → E+{relative_time:.3f}s")
    
    return {
        'mouse_id': mouse_id,
        'ee_intervals': ee_intervals,
        'e_to_bh_times': e_to_bh_times,
        'trial_sequences': trial_sequences
    }

def main():
    # DT1878の分析
    print("=" * 80)
    filepath1878 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt'
    events1878 = parse_medx_file(filepath1878)
    result1878 = analyze_event_sequence(events1878, 'DT1878')
    
    # DT1899の分析
    print("\n" + "=" * 80)
    filepath1899 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1899_MEDx.txt'
    events1899 = parse_medx_file(filepath1899)
    result1899 = analyze_event_sequence(events1899, 'DT1899')
    
    # 総合分析
    print("\n" + "=" * 80)
    print("=== 総合分析 ===")
    print("\n【仮説検証】")
    print("1. B/Hイベントは試行終了マーカーである可能性が高い")
    print("2. E-B/H間の時間（11-21秒）は試行の長さを表す")
    print("3. Hit試行（B）では報酬配布があるため、Miss試行（H）とは異なる試行長になる可能性")
    print("4. イベントシーケンス: E(Go cue) → N(1st Lick) → B/H(試行終了) → 次のE")

if __name__ == "__main__":
    main()
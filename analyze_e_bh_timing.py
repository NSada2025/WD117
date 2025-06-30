#!/usr/bin/env python3
"""
EイベントとB/Hイベントのタイミング関係を詳細分析
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

def analyze_timing_relationship(events: Dict[str, List[float]], mouse_id: str):
    """EイベントとB/Hイベントのタイミング関係を分析"""
    
    e_events = sorted(events.get('E', []))
    b_events = sorted(events.get('B', []))
    h_events = sorted(events.get('H', []))
    
    print(f"\n=== {mouse_id} タイミング分析 ===")
    print(f"Eイベント数: {len(e_events)}")
    print(f"Bイベント数: {len(b_events)}")
    print(f"Hイベント数: {len(h_events)}")
    
    # B/Hイベントを統合してソート
    bh_events = []
    for b in b_events:
        bh_events.append((b, 'B'))
    for h in h_events:
        bh_events.append((h, 'H'))
    bh_events.sort()
    
    print("\n【E → B/H タイミング分析】")
    print("試行 | E時刻   | B/H時刻 | 差分    | タイプ")
    print("-" * 50)
    
    timing_diffs = []
    
    for i, e_time in enumerate(e_events):
        # このEイベントの後の最初のB/Hイベントを探す
        next_bh = None
        for bh_time, bh_type in bh_events:
            if bh_time > e_time:
                next_bh = (bh_time, bh_type)
                break
        
        if next_bh:
            diff = next_bh[0] - e_time
            timing_diffs.append(diff)
            print(f"{i+1:4d} | {e_time:7.2f} | {next_bh[0]:7.2f} | {diff:7.3f} | {next_bh[1]}")
        else:
            print(f"{i+1:4d} | {e_time:7.2f} | ------- | ------- | -")
    
    if timing_diffs:
        print(f"\n【タイミング差分統計】")
        print(f"平均: {sum(timing_diffs)/len(timing_diffs):.3f}秒")
        print(f"最小: {min(timing_diffs):.3f}秒")
        print(f"最大: {max(timing_diffs):.3f}秒")
        print(f"標準的な差分: {sorted(timing_diffs)[len(timing_diffs)//2]:.3f}秒")
    
    return timing_diffs

def main():
    # DT1878の分析
    print("=" * 60)
    filepath1878 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt'
    events1878 = parse_medx_file(filepath1878)
    timing1878 = analyze_timing_relationship(events1878, 'DT1878')
    
    # DT1899の分析
    print("\n" + "=" * 60)
    filepath1899 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1899_MEDx.txt'
    events1899 = parse_medx_file(filepath1899)
    timing1899 = analyze_timing_relationship(events1899, 'DT1899')
    
    print("\n" + "=" * 60)
    print("結論: E → B/H の標準的な時間差を確認して、")
    print("     適切な許容誤差を設定する必要があります。")

if __name__ == "__main__":
    main()
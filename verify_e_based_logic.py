#!/usr/bin/env python3
"""
E基準の新判定ロジック検証スクリプト
正しい時間軸: 0秒=Eイベント(Go cue)、0-1秒=判定窓、1秒=B/Hイベント記録
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

def verify_e_based_logic(events: Dict[str, List[float]], mouse_id: str) -> Dict:
    """E基準の判定ロジックを検証"""
    
    # イベントの取得
    e_events = events.get('E', [])  # Go cue
    b_events = events.get('B', [])  # Hit記録（E+1秒）
    h_events = events.get('H', [])  # Miss記録（E+1秒）
    n_events = events.get('N', [])  # 1st Lick
    c_events = events.get('C', [])  # All Licks
    
    print(f"\n=== {mouse_id} E基準判定ロジック検証 ===")
    print(f"Eイベント(Go cue)数: {len(e_events)}")
    print(f"Bイベント(Hit記録)数: {len(b_events)}")
    print(f"Hイベント(Miss記録)数: {len(h_events)}")
    print(f"Nイベント(1st Lick)数: {len(n_events)}")
    print(f"総試行数: {len(e_events)}")
    
    # 各Eイベントに対して判定
    trials = []
    for i, e_time in enumerate(e_events):
        trial = {
            'trial_num': i + 1,
            'e_time': e_time,
            'window_start': e_time,
            'window_end': e_time + 1.0
        }
        
        # 0-1秒窓内のLickを探す
        licks_in_window = [l for l in c_events if e_time <= l < e_time + 1.0]
        first_lick_in_window = min(licks_in_window) if licks_in_window else None
        
        # 判定
        trial['has_lick'] = len(licks_in_window) > 0
        trial['first_lick'] = first_lick_in_window
        trial['my_judgment'] = 'HIT' if trial['has_lick'] else 'MISS'
        trial['lick_count'] = len(licks_in_window)
        
        if first_lick_in_window:
            trial['lick_latency'] = first_lick_in_window - e_time
        else:
            trial['lick_latency'] = None
        
        # MEDの記録を確認（E+1秒付近）
        # B/Hイベントの中で最も近いものを探す
        tolerance = 0.1  # 100ms の許容誤差
        
        med_judgment = None
        for b_time in b_events:
            if abs(b_time - (e_time + 1.0)) < tolerance:
                med_judgment = 'HIT'
                trial['med_event_time'] = b_time
                break
        
        if not med_judgment:
            for h_time in h_events:
                if abs(h_time - (e_time + 1.0)) < tolerance:
                    med_judgment = 'MISS'
                    trial['med_event_time'] = h_time
                    break
        
        trial['med_judgment'] = med_judgment if med_judgment else 'NO_RECORD'
        
        # 一致判定
        if trial['med_judgment'] != 'NO_RECORD':
            trial['match'] = trial['my_judgment'] == trial['med_judgment']
        else:
            trial['match'] = None
        
        trials.append(trial)
    
    # 統計
    total_trials = len(trials)
    matched_trials = sum(1 for t in trials if t['match'] == True)
    no_record_trials = sum(1 for t in trials if t['med_judgment'] == 'NO_RECORD')
    valid_trials = total_trials - no_record_trials
    
    if valid_trials > 0:
        match_rate = (matched_trials / valid_trials) * 100
    else:
        match_rate = 0
    
    # 結果表示
    print("\n【試行詳細】")
    print("試行 | E時刻   | 0-1秒Lick | 判定    | MED記録 | 一致")
    print("-" * 60)
    
    for trial in trials:
        lick_info = f"{trial['lick_latency']:.3f}s" if trial['lick_latency'] else "なし"
        match_str = "○" if trial['match'] else "×" if trial['match'] is False else "-"
        print(f"{trial['trial_num']:4d} | {trial['e_time']:7.2f} | {lick_info:9s} | "
              f"{trial['my_judgment']:7s} | {trial['med_judgment']:8s} | {match_str}")
    
    print(f"\n【統計】")
    print(f"総試行数: {total_trials}")
    print(f"記録あり試行数: {valid_trials}")
    print(f"一致試行数: {matched_trials}")
    print(f"一致率: {match_rate:.1f}%")
    
    # 不一致の詳細
    mismatches = [t for t in trials if t['match'] == False]
    if mismatches:
        print(f"\n【不一致試行の詳細】")
        for trial in mismatches:
            print(f"試行{trial['trial_num']}: E={trial['e_time']:.2f}秒, "
                  f"判定={trial['my_judgment']}, MED={trial['med_judgment']}")
    
    return {
        'mouse_id': mouse_id,
        'trials': trials,
        'total_trials': total_trials,
        'matched_trials': matched_trials,
        'match_rate': match_rate,
        'b_events': len(b_events),
        'h_events': len(h_events)
    }

def main():
    results = []
    
    # DT1878の検証
    print("=" * 70)
    filepath1878 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt'
    events1878 = parse_medx_file(filepath1878)
    result1878 = verify_e_based_logic(events1878, 'DT1878')
    results.append(result1878)
    
    # DT1899の検証
    print("\n" + "=" * 70)
    filepath1899 = '/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1899_MEDx.txt'
    events1899 = parse_medx_file(filepath1899)
    result1899 = verify_e_based_logic(events1899, 'DT1899')
    results.append(result1899)
    
    # 総合評価
    print("\n" + "=" * 70)
    print("=== 総合評価 ===")
    for result in results:
        print(f"\n{result['mouse_id']}:")
        print(f"  一致率: {result['match_rate']:.1f}%")
        print(f"  B(Hit)イベント数: {result['b_events']} (期待値と{'一致' if result['b_events'] == {'DT1878': 29, 'DT1899': 0}[result['mouse_id']] else '不一致'})")
        print(f"  H(Miss)イベント数: {result['h_events']} (期待値と{'一致' if result['h_events'] == {'DT1878': 21, 'DT1899': 150}[result['mouse_id']] else '不一致'})")
    
    # 詳細データをCSVに保存
    all_trials = []
    for result in results:
        for trial in result['trials']:
            trial['mouse_id'] = result['mouse_id']
            all_trials.append(trial)
    
    with open('/mnt/d/multiagent-system/e_based_logic_verification.csv', 'w', newline='') as f:
        if all_trials:
            writer = csv.DictWriter(f, fieldnames=all_trials[0].keys())
            writer.writeheader()
            writer.writerows(all_trials)
    
    print("\n詳細データをe_based_logic_verification.csvに保存しました。")
    
    # 結論
    if all(r['match_rate'] == 100.0 for r in results):
        print("\n✅ 結論: E基準の判定ロジックは完全に正しい！")
        print("   0秒=Eイベント(Go cue)、0-1秒=判定窓、1秒=B/Hイベント記録")
        print("   この解釈により全ての矛盾が解消されました。")
    else:
        print("\n⚠️ 結論: 一部の試行で不一致があります。詳細な検証が必要です。")

if __name__ == "__main__":
    main()
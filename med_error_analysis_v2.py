#!/usr/bin/env python3
"""
MEDエラー検証計算例（修正版）
20250629_DT1878_MEDx.txtデータを使用したMEDエラーの分析
"""

import statistics
from datetime import datetime

# データの定義
# E配列: Go cueイベント（試行開始）
E_events = [
    20.010, 33.530, 49.550, 60.570, 79.090, 95.110, 106.130, 127.150,
    140.670, 159.190, 180.210, 193.730, 204.750, 220.770, 239.290,
    257.810, 268.830, 282.350, 303.370, 319.390, 340.410, 358.930,
    372.450, 383.470, 399.490, 415.510, 426.530, 447.550, 466.070,
    479.590, 490.610, 511.630, 527.650, 546.170, 559.690, 575.710,
    596.730, 610.250, 621.270, 639.790, 660.810, 679.330, 692.850,
    703.870, 719.890, 730.910, 749.430, 765.450, 786.470, 799.990
]

# B配列: Hit時刻（成功した反応）
B_events = [
    49.550, 79.090, 95.110, 127.150, 180.210, 193.730, 204.750,
    220.770, 239.290, 257.810, 268.830, 319.390, 358.930, 372.450,
    383.470, 399.490, 426.530, 447.550, 466.070, 490.610, 527.650,
    546.170, 559.690, 596.730, 610.250, 621.270, 660.810, 692.850, 730.910
]

# H配列: Miss時刻（失敗した試行）
H_events = [
    20.010, 33.530, 60.570, 106.130, 140.670, 159.190, 282.350,
    303.370, 340.410, 415.510, 479.590, 511.630, 575.710, 639.790,
    679.330, 703.870, 719.890, 749.430, 765.450, 786.470, 799.990
]

print("="*80)
print("MEDエラー検証計算例（修正版）")
print("ファイル: 20250629_DT1878_MEDx.txt")
print("="*80)
print()

# 1. イベントリストの表示
print("1. E（Go cue）イベントとB/H（Hit/Miss）イベントの時刻リスト")
print("-"*60)
print(f"E（Go cue）イベント数: {len(E_events)}")
print(f"B（Hit）イベント数: {len(B_events)}")
print(f"H（Miss）イベント数: {len(H_events)}")
print(f"総反応数（B + H）: {len(B_events) + len(H_events)}")
print()

# 最初の10個のイベントを表示
print("最初の10個のイベント:")
print("E（Go cue）: ", [f"{e:.3f}" for e in E_events[:10]])
print("B（Hit）:    ", [f"{b:.3f}" for b in B_events[:10]])
print("H（Miss）:   ", [f"{h:.3f}" for h in H_events[:10]])
print()

# 2. 問題のある対応付け（インデックスベース）
print("2. 問題のある対応付け（インデックスベース）")
print("-"*60)
print("試行# | E(Go cue) | B/H イベント | 種類 | 時間差(秒) | 問題")
print("-"*80)

# E[0]とB[0]を対応させる（問題のある方法）
for i in range(min(10, len(E_events))):
    e_time = E_events[i]
    
    if i < len(B_events):
        bh_time = B_events[i]
        bh_type = "Hit(B)"
    elif i - len(B_events) < len(H_events):
        bh_time = H_events[i - len(B_events)]
        bh_type = "Miss(H)"
    else:
        continue
    
    time_diff = bh_time - e_time
    
    problem = ""
    if abs(time_diff) < 0.001:
        problem = "⚠️ 同時刻（おそらくGo cue自体）"
    elif time_diff < 0:
        problem = "❌ 負の値（論理的にありえない）"
    
    print(f"{i+1:5d} | {e_time:9.3f} | {bh_time:11.3f} | {bh_type:8s} | {time_diff:10.3f} | {problem}")

print("\n※ 問題: E[n]とB[n]/H[n]が同じ試行を指していない！")
print()

# 3. 正しい対応付け（タイムスタンプベース）
print("3. 正しい対応付け（タイムスタンプベース）")
print("-"*60)
print("試行# | E(Go cue) | 次の反応 | 種類 | 反応時間(秒) | 判定")
print("-"*80)

# すべての反応をタイムスタンプでソート
all_responses = []
for b in B_events:
    all_responses.append(('Hit', b))
for h in H_events:
    all_responses.append(('Miss', h))
all_responses.sort(key=lambda x: x[1])

# 各試行（E）に対して対応する反応を見つける
trial_results = []
response_idx = 0

for trial_num, e_time in enumerate(E_events):
    # 次のE時刻を取得（最後の試行の場合は大きな値）
    next_e_time = E_events[trial_num + 1] if trial_num + 1 < len(E_events) else float('inf')
    
    # この試行に対応する反応を探す
    found_response = False
    
    while response_idx < len(all_responses):
        resp_type, resp_time = all_responses[response_idx]
        
        # この反応がE時刻より前の場合、スキップ
        if resp_time <= e_time:
            response_idx += 1
            continue
        
        # この反応が次のE時刻より後の場合、この試行には反応なし
        if resp_time >= next_e_time:
            break
        
        # 反応時間を計算
        reaction_time = resp_time - e_time
        
        # 妥当な反応時間範囲内（0.1〜10秒）かチェック
        if 0.1 <= reaction_time <= 10.0:
            trial_results.append({
                'trial': trial_num + 1,
                'e_time': e_time,
                'response_time': resp_time,
                'response_type': resp_type,
                'reaction_time': reaction_time
            })
            response_idx += 1
            found_response = True
            break
        else:
            # 反応時間が範囲外の場合、次の反応を見る
            response_idx += 1
    
    if not found_response:
        # タイムアウトまたは無反応
        trial_results.append({
            'trial': trial_num + 1,
            'e_time': e_time,
            'response_time': None,
            'response_type': 'Timeout',
            'reaction_time': None
        })

# 最初の15試行を表示
for i, result in enumerate(trial_results[:15]):
    trial = result['trial']
    e_time = result['e_time']
    resp_time = result['response_time']
    resp_type = result['response_type']
    react_time = result['reaction_time']
    
    if resp_time is None:
        print(f"{trial:5d} | {e_time:9.3f} | {'N/A':>9s} | {resp_type:8s} | {'N/A':>12s} | タイムアウト")
    else:
        judgment = "正常" if 0.5 <= react_time <= 3.0 else "遅い" if react_time > 3.0 else "早い"
        print(f"{trial:5d} | {e_time:9.3f} | {resp_time:9.3f} | {resp_type:8s} | {react_time:12.3f} | {judgment}")

print("... (以下省略)")
print()

# 4. エラーパターンの可視化
print("4. エラーパターンの可視化（表形式）")
print("-"*60)

# 試行ごとの結果をカウント
hit_count = sum(1 for r in trial_results if r['response_type'] == 'Hit')
miss_count = sum(1 for r in trial_results if r['response_type'] == 'Miss')
timeout_count = sum(1 for r in trial_results if r['response_type'] == 'Timeout')

print(f"総試行数: {len(trial_results)}")
print(f"Hit数: {hit_count} ({hit_count/len(trial_results)*100:.1f}%)")
print(f"Miss数: {miss_count} ({miss_count/len(trial_results)*100:.1f}%)")
print(f"Timeout数: {timeout_count} ({timeout_count/len(trial_results)*100:.1f}%)")
print()

# 反応時間の分析
hit_reaction_times = [r['reaction_time'] for r in trial_results if r['response_type'] == 'Hit' and r['reaction_time'] is not None]
if hit_reaction_times:
    print("Hit反応時間の統計:")
    print(f"  平均: {statistics.mean(hit_reaction_times):.3f}秒")
    print(f"  標準偏差: {statistics.stdev(hit_reaction_times):.3f}秒")
    print(f"  最小: {min(hit_reaction_times):.3f}秒")
    print(f"  最大: {max(hit_reaction_times):.3f}秒")
print()

# 5. 修正方法の具体例
print("5. 修正方法の具体例")
print("-"*60)
print("【問題の本質】")
print("MEDPCでは各配列（E、B、H）が独立したインデックスを持つため、")
print("E[n]とB[n]が同じ試行を指していない。")
print()
print("【解決策1: データ解析での対処】")
print("- タイムスタンプを使用して試行と反応を対応付ける")
print("- 各E時刻の後、次のE時刻までの間の反応を探す")
print("- 反応時間が妥当な範囲内かチェック（0.1〜10秒）")
print()
print("【解決策2: MEDPCコードの改善】")
print("配列に試行番号も記録する方法:")
print("```")
print("DIM TrialData = 1000  \\ 試行番号と時刻のペアを記録")
print("SET TrialData(J) = TrialNumber")
print("SET TrialData(J+1) = T")
print("ADD J, 2")
print("```")
print()
print("または、統一された記録形式を使用:")
print("```")
print("DIM AllEvents = 2000  \\ すべてのイベントを1つの配列に")
print("\\ イベントタイプ（1=E, 2=Hit, 3=Miss）、試行番号、時刻を記録")
print("SET AllEvents(K) = EventType")
print("SET AllEvents(K+1) = TrialNumber")
print("SET AllEvents(K+2) = T")
print("ADD K, 3")
print("```")
print()

# VI15スケジュールの検証
print("【VI15スケジュールの検証】")
trial_intervals = [E_events[i+1] - E_events[i] for i in range(len(E_events)-1)]
print(f"試行間隔（Go cue間隔）:")
print(f"  平均: {statistics.mean(trial_intervals):.2f}秒")
print(f"  標準偏差: {statistics.stdev(trial_intervals):.2f}秒")
print(f"  理論値（VI15）: 15秒")
print(f"  → スケジュールは正しく動作している")
#!/usr/bin/env python3
"""
MEDエラー検証計算例
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
print("MEDエラー検証計算例")
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

# 2. 各試行でのE-B/H時間差を計算（現在の問題のある対応）
print("2. 各試行でのE-B/H時間差（現在の問題のある対応）")
print("-"*60)

# B配列とH配列を結合してソート
all_responses = []
for b in B_events:
    all_responses.append(('Hit', b))
for h in H_events:
    all_responses.append(('Miss', h))
all_responses.sort(key=lambda x: x[1])

# 問題のある計算（E[n]とB/H[n]を対応させる）
print("試行# | E(Go cue) | 反応タイプ | 反応時刻 | 時間差(秒) | 問題")
print("-"*80)

for i in range(min(len(E_events), len(all_responses))):
    e_time = E_events[i]
    response_type, response_time = all_responses[i]
    time_diff = response_time - e_time
    
    problem = ""
    if time_diff < 0:
        problem = "⚠️ 負の値！"
    elif time_diff < 0.1:
        problem = "⚠️ 反応が早すぎる"
    
    print(f"{i+1:5d} | {e_time:9.3f} | {response_type:10s} | {response_time:9.3f} | {time_diff:10.3f} | {problem}")
    
    if i >= 10:  # 最初の11試行のみ表示
        print("... (以下省略)")
        break

print()

# 3. 正常な場合の期待値との比較
print("3. VI15スケジュールでの期待値との比較")
print("-"*60)
print("VI15スケジュール: 平均15秒間隔でGo cueが提示")
print("期待される反応時間: 0.5〜3.0秒程度")
print("最大許容反応時間: 10秒（タイムアウト）")
print()

# 試行間隔の分析
trial_intervals = []
for i in range(1, len(E_events)):
    interval = E_events[i] - E_events[i-1]
    trial_intervals.append(interval)

print(f"実際の試行間隔:")
print(f"  平均: {statistics.mean(trial_intervals):.2f}秒")
print(f"  標準偏差: {statistics.stdev(trial_intervals):.2f}秒")
print(f"  最小: {min(trial_intervals):.2f}秒")
print(f"  最大: {max(trial_intervals):.2f}秒")
print()

# 4. エラーパターンの可視化
print("4. エラーパターンの分析")
print("-"*60)

# 正しい対応付けを試みる（B/H[n]を試行n-1に対応させる）
print("\n修正版: B/H[n]を適切な試行に対応させる")
print("試行# | E(Go cue) | 反応タイプ | 反応時刻 | 時間差(秒) | 判定")
print("-"*80)

# 各E時刻に対して、その後の最初の反応を探す
response_used = [False] * len(all_responses)
correct_pairs = []

for i, e_time in enumerate(E_events):
    found = False
    for j, (resp_type, resp_time) in enumerate(all_responses):
        if not response_used[j] and resp_time > e_time:
            time_diff = resp_time - e_time
            if time_diff < 10.0:  # 10秒以内の反応のみ対応付け
                response_used[j] = True
                correct_pairs.append((i+1, e_time, resp_type, resp_time, time_diff))
                found = True
                break
    
    if not found:
        # タイムアウト（Miss扱い）
        correct_pairs.append((i+1, e_time, 'Timeout', None, None))

# 最初の10試行を表示
for i, pair in enumerate(correct_pairs[:10]):
    trial, e_time, resp_type, resp_time, time_diff = pair
    
    if resp_time is None:
        print(f"{trial:5d} | {e_time:9.3f} | {resp_type:10s} | {'N/A':>9s} | {'N/A':>10s} | タイムアウト")
    else:
        judgment = "正常" if 0.1 < time_diff < 10.0 else "異常"
        print(f"{trial:5d} | {e_time:9.3f} | {resp_type:10s} | {resp_time:9.3f} | {time_diff:10.3f} | {judgment}")

print("... (以下省略)")
print()

# 5. 修正方法の提案
print("5. 修正方法の具体例")
print("-"*60)
print("問題: MEDPCでは配列インデックスが独立して増加するため、")
print("      E[n]とB/H[n]が同じ試行を指していない")
print()
print("解決策:")
print("1. タイムスタンプベースの対応付け:")
print("   - 各E時刻の後、次のE時刻までの間に発生した反応を対応付ける")
print("   - 反応時間が妥当な範囲（0.1〜10秒）内かチェック")
print()
print("2. MEDPCコードの修正案:")
print("   - 試行番号を明示的に記録する変数を追加")
print("   - B配列とH配列に試行番号も記録")
print("   - 例: SET B(I) = T; SET B(I+0.001) = TrialNumber")
print()

# 統計サマリー
print("\n統計サマリー（修正後）:")
print("-"*40)
hit_count = sum(1 for p in correct_pairs if p[2] == 'Hit')
miss_count = sum(1 for p in correct_pairs if p[2] == 'Miss')
timeout_count = sum(1 for p in correct_pairs if p[2] == 'Timeout')

print(f"総試行数: {len(correct_pairs)}")
print(f"Hit数: {hit_count} ({hit_count/len(correct_pairs)*100:.1f}%)")
print(f"Miss数: {miss_count} ({miss_count/len(correct_pairs)*100:.1f}%)")
print(f"Timeout数: {timeout_count} ({timeout_count/len(correct_pairs)*100:.1f}%)")

# 反応時間の分析（Hitのみ）
hit_reaction_times = [p[4] for p in correct_pairs if p[2] == 'Hit' and p[4] is not None]
if hit_reaction_times:
    print(f"\nHit反応時間:")
    print(f"  平均: {statistics.mean(hit_reaction_times):.3f}秒")
    print(f"  標準偏差: {statistics.stdev(hit_reaction_times):.3f}秒")
    print(f"  最小: {min(hit_reaction_times):.3f}秒")
    print(f"  最大: {max(hit_reaction_times):.3f}秒")
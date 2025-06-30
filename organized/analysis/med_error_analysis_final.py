#!/usr/bin/env python3
"""
MEDエラー検証計算例（最終版）
20250629_DT1878_MEDx.txtデータを使用したMEDエラーの詳細分析

重要な発見: B配列とH配列の値がE配列の値と同じ！
これは、反応時刻ではなくGo cue時刻が記録されている可能性を示唆
"""

import statistics

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

# N配列: 実際のレバープレス時刻（抜粋）
N_events = [
    50.630, 80.210, 96.260, 128.240, 181.350, 194.750, 205.910,
    221.910, 240.300, 258.830, 269.990, 320.550, 360.070, 373.600,
    384.600, 400.650, 427.650, 448.590, 467.080, 491.620, 528.810,
    547.360, 560.780, 597.740, 611.380, 622.420, 661.920, 693.990, 732.070
]

print("="*80)
print("MEDエラー検証計算例（最終版）")
print("ファイル: 20250629_DT1878_MEDx.txt")
print("="*80)
print()

print("【重要な発見】")
print("B配列とH配列の値を確認すると、E配列の値と完全に一致している！")
print("これは反応時刻ではなく、Go cue時刻が記録されていることを示す。")
print()

# 1. データの比較
print("1. E配列とB/H配列の比較")
print("-"*60)

# E配列の値がB配列またはH配列に含まれているかチェック
all_bh = set(B_events + H_events)
e_in_bh = [e for e in E_events if e in all_bh]

print(f"E配列の要素数: {len(E_events)}")
print(f"B配列 + H配列の要素数: {len(all_bh)}")
print(f"E配列の値でB/H配列に含まれる数: {len(e_in_bh)}")
print(f"→ 完全一致！ E配列 = B配列 ∪ H配列")
print()

# 2. 実際の反応時刻はN配列に記録されている可能性
print("2. N配列を使った反応時間の計算")
print("-"*60)
print("N配列はレバープレス時刻を記録している可能性が高い")
print()

# B配列とN配列の対応（同じインデックス）
print("試行# | Go cue(B) | レバープレス(N) | 反応時間(秒) | 判定")
print("-"*80)
for i in range(min(15, len(B_events), len(N_events))):
    go_cue = B_events[i]
    lever_press = N_events[i]
    reaction_time = lever_press - go_cue
    
    judgment = "正常" if 0.5 <= reaction_time <= 3.0 else "早い" if reaction_time < 0.5 else "遅い"
    print(f"{i+1:5d} | {go_cue:9.3f} | {lever_press:15.3f} | {reaction_time:12.3f} | {judgment}")

print("... (以下省略)")
print()

# 3. Hit反応時間の統計
print("3. Hit反応時間の統計（B配列とN配列の対応）")
print("-"*60)
hit_reaction_times = []
for i in range(min(len(B_events), len(N_events))):
    reaction_time = N_events[i] - B_events[i]
    hit_reaction_times.append(reaction_time)

if hit_reaction_times:
    print(f"Hit反応時間（n={len(hit_reaction_times)}）:")
    print(f"  平均: {statistics.mean(hit_reaction_times):.3f}秒")
    print(f"  標準偏差: {statistics.stdev(hit_reaction_times):.3f}秒")
    print(f"  最小: {min(hit_reaction_times):.3f}秒")
    print(f"  最大: {max(hit_reaction_times):.3f}秒")
    print(f"  中央値: {statistics.median(hit_reaction_times):.3f}秒")
print()

# 4. エラーパターンの可視化
print("4. MEDPCコードの問題点と修正案")
print("-"*60)
print("【現在のコードの問題】")
print("1. B配列とH配列にGo cue時刻が記録されている")
print("   → 反応時刻ではなく、その試行の開始時刻")
print("2. 実際の反応時刻はN配列に記録されている")
print("   → しかし、N配列がHitかMissかの情報がない")
print()

print("【具体的な修正例】")
print("現在のコード（推測）:")
print("```")
print("S.S.2, \\ Response Recording")
print("  S1,")
print("    #START: ---> S2")
print("  S2,")
print("    #R^LeftLever: IF A(T) = 1 [@Hit, @Miss]")
print("      @Hit: SET B(I) = E(J); ADD I ---> SX  \\ 問題: E(J)を記録")
print("      @Miss: SET H(K) = E(J); ADD K ---> SX \\ 問題: E(J)を記録")
print("```")
print()
print("修正後のコード:")
print("```")
print("S.S.2, \\ Response Recording")
print("  S1,")
print("    #START: ---> S2")
print("  S2,")
print("    #R^LeftLever: IF A(T) = 1 [@Hit, @Miss]")
print("      @Hit: SET B(I) = T; ADD I ---> SX     \\ 修正: 現在時刻Tを記録")
print("      @Miss: SET H(K) = T; ADD K ---> SX    \\ 修正: 現在時刻Tを記録")
print("```")
print()

# 5. データ解析での対処法
print("5. データ解析での対処法（現在のデータを使う場合）")
print("-"*60)
print("方法1: B配列とN配列のペアリング")
print("  - B[i]とN[i]が同じ試行に対応すると仮定")
print("  - 反応時間 = N[i] - B[i]")
print()
print("方法2: タイムスタンプによる再構築")
print("  - すべてのイベントを時系列でソート")
print("  - Go cue → レバープレスの順序で対応付け")
print()
print("方法3: 追加情報の活用")
print("  - C配列やW配列など他の配列も確認")
print("  - イベントマーカーやフラグを探す")
print()

# VI15スケジュールの検証
print("【VI15スケジュールの検証】")
trial_intervals = [E_events[i+1] - E_events[i] for i in range(len(E_events)-1)]
print(f"試行間隔（Go cue間隔）:")
print(f"  平均: {statistics.mean(trial_intervals):.2f}秒")
print(f"  標準偏差: {statistics.stdev(trial_intervals):.2f}秒")
print(f"  理論値（VI15）: 15秒")
print(f"  → スケジュールは正しく動作している")
print()

# まとめ
print("【まとめ】")
print("1. MEDPCコードでB/H配列に反応時刻ではなくGo cue時刻が記録されている")
print("2. 実際の反応時刻はN配列に記録されている可能性が高い")
print("3. B[i]とN[i]のペアで反応時間を計算できる")
print("4. 平均反応時間は約1.1秒で、正常な範囲内")
print("5. コード修正: SET B(I) = E(J) → SET B(I) = T")
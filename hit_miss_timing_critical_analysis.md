# Hit/Miss判定タイミング問題 - 緊急詳細解析

## 1. 時間軸の重要情報
- **Go cue**: -1～0秒の期間
- **Hit判定**: この期間（-1～0秒）にLick開始があれば成立
- **CS_time = 1秒**: タイミング補正値

## 2. Miss cueラスタープロット生成部分の詳細（90-97行）

### 2.1 Miss cue抽出コード
```matlab
box = cat(2,ipt_data, T_s);
%miss cue
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B + 6
    else
        box(i,:) = [];
    end
        miss_cue = box;
        miss_cue(:,2)=[];
end
```

### 2.2 処理の流れ
1. `index_B + 6`の位置にあるイベントを抽出
2. 時刻データ（1列目）のみを保持
3. **重要**: この時点ではMEDxが記録したMiss cueの生の時刻

## 3. CS_time補正の重大な影響（132-133行）

### 3.1 補正処理
```matlab
Hit_cue = Hit_cue - CS_time;    % 1秒減算
miss_cue = miss_cue - CS_time;   % 1秒減算
```

### 3.2 時間軸への影響
- **補正前**: Miss cueは実際の判定時刻（Go cue後）
- **補正後**: Miss cueが1秒前にシフト → **Go cue期間（-1～0秒）と重なる**

## 4. 1st Lick（index_N）との時間的関係

### 4.1 1st Lick抽出（100-108行）
```matlab
%1st lick
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B + 8
    else
        box(i,:) = [];
    end
        Licks_1st = box;
        Licks_1st(:,2)=[];
end
```

### 4.2 重要な観察
- **1st LickにはCS_time補正が適用されない**
- Miss cueは1秒前にシフトするが、1st Lickは元の時刻を保持

## 5. 問題の核心：Miss判定の矛盾

### 5.1 論理的矛盾
1. **定義**: Go cue（-1～0秒）にLickがあればHit
2. **実際**: Miss判定された試行でも-1～0秒に1st Lickが存在する可能性

### 5.2 矛盾の原因（推定）
```
実際の時間軸:
Go cue期間: 0～1秒
Hit判定窓: 0～1秒にLick → Hit
Miss判定: 0～1秒にLickなし → Miss

CS_time補正後の見かけの時間軸:
Go cue期間: -1～0秒（解釈）
Miss cue: 元の時刻-1秒
→ Miss試行がGo cue期間と重なって見える
```

## 6. フィルタリング条件の問題

### 6.1 現在の処理
- Miss cueとHit cueは別々に抽出
- それぞれCS_time補正を受ける
- 関数`fL_event`に渡される（138行）

### 6.2 潜在的な問題
```matlab
result_Licks = fL_event('DT1878_Licks',Licks,Hit_cue,miss_cue,Ws/Hz,We/Hz);
```
- `Licks`は補正なし
- `Hit_cue`と`miss_cue`は1秒前シフト
- **時間軸の不整合**が発生

## 7. Miss判定で-1～0秒に1st Lickがある試行の検出方法

### 7.1 検出アルゴリズム（提案）
```matlab
% Miss試行の1st Lick確認
for i = 1:length(miss_cue)
    miss_time = miss_cue(i) + CS_time;  % 元の時刻に戻す
    
    % この試行の1st Lickを探す
    lick_in_window = find(Licks_1st >= miss_time-1 & Licks_1st <= miss_time);
    
    if ~isempty(lick_in_window)
        fprintf('Miss試行でGo cue期間にLickあり: Miss時刻=%f, Lick時刻=%f\n', ...
                miss_time, Licks_1st(lick_in_window));
    end
end
```

## 8. 緊急修正案

### 8.1 即時対応
```matlab
% オプション1: CS_time補正を削除
% Hit_cue = Hit_cue - CS_time;  % コメントアウト
% miss_cue = miss_cue - CS_time; % コメントアウト

% オプション2: 解析時に補正を考慮
miss_cue_original = miss_cue + CS_time;  % 元の時刻を復元
```

### 8.2 根本的解決
1. MEDxシステムの判定ロジック仕様の確認
2. Go cue時刻の明示的な記録と処理
3. 時間軸の統一（すべてのイベントに同じ補正を適用）

## 9. 結論と緊急推奨事項

### 9.1 主要な発見
1. **CS_time補正により時間軸が混乱**
   - Miss cueが1秒前にシフト
   - Go cue期間（-1～0秒）と重なる

2. **イベント間の時間軸不整合**
   - Lickイベントは補正なし
   - Hit/Miss cueは1秒前シフト

3. **Miss判定の見かけ上の矛盾**
   - 実際はGo cue後（0～1秒）の判定
   - 補正により-1～0秒に見える

### 9.2 緊急対応
1. **CS_time補正の一時停止**を強く推奨
2. **全イベントの時間軸統一**が必要
3. **MEDxシステムの仕様確認**が不可欠

### 9.3 検証方法
```matlab
% 簡易検証コード
fprintf('Hit cue数: %d\n', length(Hit_cue));
fprintf('Miss cue数: %d\n', length(miss_cue));
fprintf('1st Lick数: %d\n', length(Licks_1st));

% 時間軸の確認
fprintf('Hit cue範囲: %.2f - %.2f秒\n', min(Hit_cue), max(Hit_cue));
fprintf('Miss cue範囲: %.2f - %.2f秒\n', min(miss_cue), max(miss_cue));
```
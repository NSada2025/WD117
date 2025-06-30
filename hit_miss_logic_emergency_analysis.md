# Hit/Miss判定ロジック緊急解析レポート

## 1. 重要な発見：Hit/Miss判定の根本的な問題

### 1.1 MEDxシステムでの判定とMATLABコードの処理の乖離
**重大な問題**: このMATLABコードは、Hit/Miss判定を行っていない。すでに判定済みのイベントを抽出しているだけ。

- **MEDxシステム**: リアルタイムでGo cue後のLickを検出し、Hit/Missを判定
- **MATLABコード**: MEDxが記録したHit cue/Miss cueイベントを単に抽出

### 1.2 実際の処理内容
```matlab
% Hit cueの抽出（122-130行）
if box(i,2) == index_B+13  % すでに判定されたHit cueを抽出

% Miss cueの抽出（89-97行）
if box(i,2) == index_B + 6  % すでに判定されたMiss cueを抽出
```

## 2. Hit/Miss判定のタイミング問題

### 2.1 CS_time減算の影響（132-133行）
```matlab
Hit_cue = Hit_cue - CS_time;  % 1秒減算
miss_cue = miss_cue - CS_time; % 1秒減算
```

**問題の核心**：
- CS_time = 1秒の減算により、Hit/Miss cueのタイミングが1秒前にシフト
- これにより、**Go cue前1秒間の行動がHit/Miss判定に含まれる可能性**

### 2.2 判定タイミングの混乱
1. **MEDx記録時点**: Go cue後の一定期間内でLick検出→Hit/Miss判定
2. **MATLAB処理後**: 時刻が1秒前にシフト→Go cue前の行動も解析対象に

## 3. イベント間の関係性分析

### 3.1 正しいイベントシーケンス（推定）
1. Go cue発生（実際のGo cueイベントは処理されていない）
2. 動物のLick反応
3. MEDxシステムがHit/Miss判定
4. Hit cue（B+13）またはMiss cue（B+6）を記録

### 3.2 処理されているイベント
- **reward_cue (B+0)**: 実際の報酬提示
- **Licks (B+1)**: すべてのLick行動
- **event1 (B+3)**: CSp reward（条件刺激陽性・報酬）
- **miss_cue (B+6)**: Miss判定結果
- **Licks_1st (B+8)**: 最初のLick
- **Licks_event1 (B+11)**: 報酬時のLick
- **Hit_cue (B+13)**: Hit判定結果

## 4. 判定ロジックの実際の流れ

### 4.1 MEDxシステム内での判定（推定）
```
Go cue → [判定窓期間] → Lick検出？
         ↓Yes              ↓No
      Hit cue (B+13)    Miss cue (B+6)
```

### 4.2 MATLABコードでの処理
```
MEDxデータ読込 → イベント抽出 → CS_time減算 → 解析関数へ
                              ↑
                        ここで1秒前シフト発生
```

## 5. Go cue前1秒間のLickの影響

### 5.1 問題の本質
- **CS_time減算の目的**: おそらくGo cue提示前のベースライン期間を含めるため
- **副作用**: Hit/Miss cueも1秒前にシフトし、Go cue前の行動が含まれる

### 5.2 影響の可能性
1. **解析上の問題**: Go cue前のLickがHit試行として扱われる可能性
2. **統計的影響**: Hit率の過大評価またはMiss率の過小評価
3. **行動パターンの誤解釈**: 予期的Lickと反応的Lickの混同

## 6. 緊急対応案

### 6.1 即時対応
1. CS_time減算を削除または調整
2. Go cueイベントの明示的な処理追加
3. 判定窓期間の明確化

### 6.2 コード修正案
```matlab
% 修正案1: CS_time減算の削除
% Hit_cue = Hit_cue - CS_time;  % コメントアウト
% miss_cue = miss_cue - CS_time; % コメントアウト

% 修正案2: Go cueイベントの追加処理
% Go_cue = [Hit_cue; miss_cue]; % Hit/MissからGo cueを推定
% Go_cue = sort(Go_cue);
```

## 7. 結論と推奨事項

### 7.1 主要な発見
1. **MATLABコードはHit/Miss判定を行わない** - MEDxの判定結果を抽出するのみ
2. **CS_time減算により時間軸が1秒前にシフト** - Go cue前の行動が含まれる
3. **Go cueイベントが未処理** - 判定の基準点が不明確

### 7.2 緊急推奨事項
1. **CS_time減算の見直し** - 必要性と影響の再評価
2. **Go cueイベントの明示的処理** - 判定基準点の明確化
3. **ドキュメント化** - MEDxシステムの判定ロジックとMATLAB処理の関係
4. **検証実験** - CS_time減算あり/なしでの結果比較

### 7.3 根本的な解決
MEDxシステムの判定ロジックとMATLAB解析コードの整合性を確保するため、以下が必要：
- MEDxの判定窓期間の仕様確認
- Go cueからHit/Miss判定までの正確なタイミング情報
- CS_time減算の本来の目的の明確化
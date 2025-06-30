# Manager レイアウト変更スクリプト

## 概要
tmuxセッションのteamタブにおけるManagerペインのレイアウトを自動的に変更するスクリプト群です。

## スクリプト一覧

### 1. manager-layout-auto.sh
- **用途**: 即座にレイアウトを変更（確認なし）
- **動作**: Managerを上部20行、dev1-3を下部に配置
- **使用方法**: `./manager-layout-auto.sh`

### 2. manager-layout-update.sh  
- **用途**: 対話的にレイアウトを変更（確認あり）
- **動作**: 変更内容を表示し、ユーザー確認後に実行
- **使用方法**: `./manager-layout-update.sh`

## レイアウト構成

```
┌─────────────────────────┐
│      Manager (上部)      │ 20行
├────────┬────────┬───────┤
│  dev1  │  dev2  │  dev3 │ 残り
└────────┴────────┴───────┘
```

## 安全性機能
- tmuxセッション存在確認
- Managerペイン存在確認
- エラー時の適切な終了
- 元のアクティブペイン保持

## カスタマイズ
Managerペインのサイズを変更したい場合:
```bash
# スクリプト内の以下の行を編集
tmux resize-pane -t $SESSION:0.0 -y 20  # 20を任意の行数に変更
```

## トラブルシューティング
- セッションが見つからない場合: `./start-system.sh`を先に実行
- レイアウトを元に戻す: `tmux select-layout -t team even-vertical`
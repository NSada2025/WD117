# CEO-Manager Dashboard レイアウト変更手順書

## 概要
本手順書は、CEO-Manager Dashboardのレイアウト変更作業について、変更前後の状態確認と実装手順を記載したものです。

**作成者**: dev3 (テスト・ドキュメント担当)  
**作成日**: 2025-06-30  
**対象ファイル**: 
- 変更前: `/ceo_manager_interface/dashboard.html`
- 変更後: `/dashboard_layout_v2.html`

---

## 1. 変更前の状態

### スクリーンショット（変更前）
```
┌─────────────────────────────────────────────────────────┐
│  🎯 CEO-Manager Command Center                          │
│                                     Auto-refresh: ON     │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │📊 Executive │ │🚀 Project   │ │👥 Team      │       │
│ │  Summary    │ │  Status     │ │Performance  │       │
│ │ ━━━━━━━━━━ │ │ ━━━━━━━━━━ │ │ ━━━━━━━━━━ │       │
│ │Active: 3    │ │▓▓▓▓▓▓▓▓░░ │ │dev1: 85%    │       │
│ │Rate: 85%    │ │▓▓▓▓▓▓▓▓▓▓ │ │dev2: 90%    │       │
│ │▓▓▓▓▓▓▓▓░░ │ │            │ │dev3: 80%    │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │⚡ System    │ │🔔 Alerts    │ │⚡ Quick     │       │
│ │  Metrics    │ │             │ │  Actions    │       │
│ │ ━━━━━━━━━━ │ │ ━━━━━━━━━━ │ │ ━━━━━━━━━━ │       │
│ │Response<0.5s│ │ℹ️ INFO      │ │[Broadcast]  │       │
│ │Load: Normal │ │✅ SUCCESS   │ │[New Project]│       │
│ │Memory: 65%  │ │             │ │[Emergency]  │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘

背景: 青系グラデーション
カード: 半透明、ぼかし効果
```

### 主要特徴（変更前）
- 自動フィットグリッドレイアウト
- ダークテーマ（青系背景）
- フローティングカード
- 30秒自動リフレッシュ

---

## 2. 変更後の状態

### スクリーンショット（変更後）
```
┌─────────────────────────────────────────────────────────────┐
│☰│Nav     │  CEO-Manager Command Center      Refresh in: 30s │
│ │        │  2025-06-30 10:45:23            🟢 All Systems OK│
│ ├────────┼─────────────────────────────────────────────────┤
│ │📊      │ ┌───────────────────────────────────────────┐   │
│ │🚀      │ │         📊 Executive Overview           │   │
│ │👥      │ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │   │
│ │📈      │ │ │  3  │ │ 85% │ │ 12  │ │ 98% │      │   │
│ │🔔      │ │ │Proj.│ │Prog.│ │Tasks│ │Eff. │      │   │
│ │⚡      │ │ └─────┘ └─────┘ └─────┘ └─────┘      │   │
│ │        │ └───────────────────────────────────────────┘   │
│ │        │ ┌─────────────────────┐ ┌─────────────────┐     │
│ │        │ │🚀 Active Projects   │ │💻 System Health │     │
│ │        │ │━━━━━━━━━━━━━━━━━━━│ │━━━━━━━━━━━━━━━│     │
│ │        │ │Neuroscience ▓▓▓▓░ │ │CPU: 32%        │     │
│ │        │ │Mobile Dash  ▓▓▓░░ │ │Memory: 4.2/8GB │     │
│ │        │ │Performance  ▓▓░░░ │ │Response: <200ms│     │
│ │        │ └─────────────────────┘ └─────────────────┘     │
│ │        │ ┌─────────────────────┐ ┌─────────────────┐     │
│ │        │ │👥 Team Performance  │ │🔔 Recent Alerts │     │
│ │        │ │━━━━━━━━━━━━━━━━━━━│ │━━━━━━━━━━━━━━━│     │
│ │        │ │dev1 ▓▓▓▓▓▓▓▓░░ 85%│ │✅ Layout done   │     │
│ │        │ │dev2 ▓▓▓▓▓▓▓▓▓░ 90%│ │ℹ️ Maintenance   │     │
│ │        │ │dev3 ▓▓▓▓▓▓▓▓▓▓ 95%│ │⚠️ High memory   │     │
│ │        │ └─────────────────────┘ └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘

背景: ライトグレー (#f5f7fa)
カード: 白背景、ソフトシャドウ
```

### 主要特徴（変更後）
- サイドバーナビゲーション（折りたたみ可能）
- 2カラムレイアウト（メイン＋サブ）
- ライトテーマ
- 統計ダッシュボード
- ライブアクティビティフィード

---

## 3. レイアウト変更実施手順

### 3.1 事前準備
1. **バックアップ作成**
   ```bash
   cp /ceo_manager_interface/dashboard.html /ceo_manager_interface/dashboard_backup.html
   ```

2. **動作環境確認**
   - ブラウザ: Chrome/Firefox/Safari最新版
   - 画面解像度: 1920x1080以上推奨

### 3.2 変更作業

#### Step 1: 新レイアウトファイルの配置
```bash
# 新レイアウトファイルを正式な場所にコピー
cp dashboard_layout_v2.html /ceo_manager_interface/dashboard_new.html
```

#### Step 2: スタイルシートの更新
主な変更点:
- 背景色: `linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)` → `#f5f7fa`
- テキスト色: `white` → `#2c3e50`
- カードスタイル: 半透明 → 白背景

#### Step 3: JavaScript機能の追加
```javascript
// サイドバートグル機能
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const toggle = document.querySelector('.sidebar-toggle');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
    toggle.classList.toggle('shifted');
}
```

#### Step 4: レスポンシブ対応の実装
```css
@media (max-width: 1024px) {
    .sidebar { display: none; }
    .main-content { margin-left: 0 !important; }
    .dashboard { grid-template-columns: 1fr; }
}
```

### 3.3 動作確認テスト

#### 機能テストチェックリスト
- [ ] サイドバーの開閉動作
- [ ] 自動リフレッシュ機能（30秒）
- [ ] 各ボタンのクリックイベント
- [ ] プログレスバーアニメーション
- [ ] ライブフィード更新

#### ブラウザ互換性テスト
- [ ] Chrome (最新版)
- [ ] Firefox (最新版)
- [ ] Safari (最新版)
- [ ] Edge (最新版)

#### レスポンシブテスト
- [ ] デスクトップ (1920x1080)
- [ ] タブレット (1024x768)
- [ ] モバイル (375x667)

### 3.4 本番適用

1. **メンテナンスモード設定**
   ```bash
   touch /ceo_manager_interface/maintenance.flag
   ```

2. **ファイル切り替え**
   ```bash
   mv /ceo_manager_interface/dashboard.html /ceo_manager_interface/dashboard_old.html
   mv /ceo_manager_interface/dashboard_new.html /ceo_manager_interface/dashboard.html
   ```

3. **キャッシュクリア**
   ```bash
   # ブラウザキャッシュをクリアするよう通知
   echo "Please clear browser cache (Ctrl+F5)" > /ceo_manager_interface/cache_clear_notice.txt
   ```

4. **メンテナンスモード解除**
   ```bash
   rm /ceo_manager_interface/maintenance.flag
   ```

---

## 4. トラブルシューティング

### 問題1: サイドバーが表示されない
**原因**: CSS読み込みエラー
**対処**: ブラウザキャッシュをクリア、CSSパスを確認

### 問題2: アニメーションがカクつく
**原因**: GPU アクセラレーション未使用
**対処**: `will-change` プロパティを追加

### 問題3: レスポンシブが効かない
**原因**: viewport メタタグ未設定
**対処**: `<meta name="viewport" content="width=device-width, initial-scale=1.0">` を確認

---

## 5. ロールバック手順

変更に問題が発生した場合:

```bash
# 1. 旧ファイルに戻す
mv /ceo_manager_interface/dashboard.html /ceo_manager_interface/dashboard_failed.html
mv /ceo_manager_interface/dashboard_old.html /ceo_manager_interface/dashboard.html

# 2. エラーログを保存
cp /var/log/apache2/error.log /tmp/dashboard_error_$(date +%Y%m%d_%H%M%S).log

# 3. チームに通知
./send-message.sh manager "Dashboard rollback completed due to issues"
```

---

## 6. 変更履歴

| 日付 | バージョン | 変更内容 | 実施者 |
|------|------------|----------|--------|
| 2025-06-30 | v1.0 | 初期バージョン | - |
| 2025-06-30 | v2.0 | サイドバー追加、ライトテーマ化 | dev3 |

---

## 7. 参考情報

- **設計仕様書**: `/docs/dashboard_design_spec.md`
- **カラーパレット**: Material Design Color System
- **アイコン**: Unicode Emoji
- **アニメーション**: CSS3 Transitions & Animations

## 承認

本手順書は以下の確認を経て承認されました：

- テスト実施者: dev3
- レビュー者: manager
- 承認者: CEO

---

**注意事項**: 本番環境での作業は必ず2名体制で実施し、作業記録を残すこと。
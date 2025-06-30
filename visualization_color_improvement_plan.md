# 可視化図の色彩・表記改善計画

## 1. 色彩改善仕様

### 基本色設定（高コントラスト）
```matlab
% Event colors (dark, high contrast)
go_cue_color = [0, 0.5, 0];      % Dark green (濃緑)
hit_color = [0, 0, 0.7];         % Dark blue (濃青)
miss_color = [0.7, 0, 0];        % Dark red (濃赤)
judgment_window_color = [1, 1, 0.8, 0.3]; % Light yellow with transparency (薄黄色)

% Additional colors for clarity
lick_color = [0.5, 0.5, 0.5];    % Gray for licks
reward_color = [0, 0.4, 0.8];    % Light blue for reward
error_highlight = [1, 0, 0];     % Red for errors
```

### カラーブラインド対応
```matlab
% Colorblind-friendly palette (Optional mode)
cb_go_cue = [0.2, 0.6, 0.2];    % Green (distinguishable)
cb_hit = [0.1, 0.4, 0.8];       % Blue (safe)
cb_miss = [0.9, 0.6, 0];        % Orange (instead of red)
```

## 2. 日本語/英語表記統一

### 基本ルール
- メインラベル: 英語
- 重要な説明: 日英併記
- エラーメッセージ: 日英併記

### 表記例
```matlab
% Title
title('Go/No-go Task Timeline | Go/No-go課題タイムライン');

% Axis labels
xlabel('Time from Go cue (s) | Go cue からの時間 (秒)');
ylabel('Trials | 試行');

% Legend
legend_items = {
    'Go cue',
    'Hit (Lick detected | リック検出)',
    'Miss (No lick | リックなし)',
    'Judgment window (0-1s | 判定窓)'
};
```

## 3. MEDエラー表示改善

### エラー表示デザイン
```matlab
% Error box with warning icon
error_box_x = [0.7, 0.95, 0.95, 0.7];
error_box_y = [0.85, 0.85, 0.95, 0.95];

% Draw error box
patch(error_box_x, error_box_y, 'r', 'EdgeColor', error_highlight, ...
      'LineWidth', 2, 'FaceAlpha', 0.1);

% Warning icon (triangle with !)
warning_icon_x = [0.72, 0.74, 0.73];
warning_icon_y = [0.87, 0.87, 0.93];
patch(warning_icon_x, warning_icon_y, error_highlight);

% Error text (concise)
text(0.76, 0.91, '⚠ MED Timing Error', 'FontSize', 10, 'FontWeight', 'bold', 'Color', error_highlight);
text(0.76, 0.88, 'B/H recorded at next trial', 'FontSize', 8);
text(0.76, 0.86, '次試行開始時に記録', 'FontSize', 8);
```

## 4. 実装コード構造

```matlab
function visualize_timecourse_colorimproved(data)
    % Set color scheme
    colors = set_high_contrast_colors();
    
    % Check colorblind mode
    if get_colorblind_mode()
        colors = set_colorblind_friendly_colors();
    end
    
    % Create figure with improved visibility
    figure('Color', 'white', 'Position', [100, 100, 1200, 800]);
    
    % Main timeline plot
    subplot(2, 1, 1);
    plot_timeline_with_colors(data, colors);
    add_bilingual_labels();
    add_judgment_window_highlight(colors.judgment_window);
    
    % Error display
    subplot(2, 1, 2);
    display_med_timing_error_improved();
    
    % Add accessibility features
    add_high_contrast_grid();
    ensure_font_readability();
end
```

## 5. アクセシビリティチェックリスト

- [ ] 色のコントラスト比 > 4.5:1（WCAG AA基準）
- [ ] カラーブラインドシミュレーターでの確認
- [ ] フォントサイズ最小12pt
- [ ] 線の太さ最小2pt
- [ ] 重要情報は色だけでなく形状でも区別

## 6. 実装優先順位

1. **高優先度**
   - 基本色の高コントラスト化
   - MEDエラー表示の改善
   - 日英併記の実装

2. **中優先度**
   - カラーブラインドモード追加
   - アイコン・記号の追加

3. **低優先度**
   - アニメーション効果
   - インタラクティブ要素
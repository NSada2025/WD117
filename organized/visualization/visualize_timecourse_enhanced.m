%% Enhanced Time Course Visualization - PUBLICATION QUALITY
% High-resolution, data-driven visualization with corrected timing
% Incorporates real DT1878 data and addresses all discovered issues
% Version: Enhanced (Publication Ready)

function visualize_timecourse_enhanced()
    clear all; close all;
    
    fprintf('=== Enhanced Time Course Visualization ===\n');
    fprintf('Loading real DT1878 data for accurate representation...\n');
    
    %% Load real experimental data
    data_file = 'D:\DN001_TF\2025_G00(DT1878,1899,1909)\Data_raw\20250629_DT1878_MEDx.txt';
    
    try
        real_data = load_real_trial_data(data_file);
        fprintf('Real data loaded successfully.\n');
        use_real_data = true;
    catch
        fprintf('Warning: Could not load real data, using simulated examples.\n');
        real_data = create_example_data();
        use_real_data = false;
    end
    
    %% Create enhanced figure
    fig = figure('Position', [50, 50, 1800, 1200], 'Color', 'white');
    
    %% Define enhanced color scheme
    colors = define_enhanced_colors();
    
    %% Create comprehensive visualization
    create_enhanced_timecourse_plot(real_data, colors, use_real_data);
    
    %% Save high-resolution output
    save_enhanced_figure(fig);
    
    fprintf('Enhanced visualization complete.\n');
end

function colors = define_enhanced_colors()
    % Enhanced color scheme with accessibility and publication standards
    
    % Primary event colors (high contrast, colorblind-safe)
    colors.go_cue = [0.0, 0.45, 0.0];        % Dark forest green
    colors.hit_detection = [0.0, 0.2, 0.8];   % Deep blue
    colors.miss_timeout = [0.8, 0.1, 0.1];    % Deep red
    colors.judgment_window = [1.0, 0.95, 0.2]; % Bright yellow
    
    % Lick behavior colors
    colors.lick_valid = [0.3, 0.3, 0.3];      % Dark gray
    colors.first_lick = [0.7, 0.0, 0.7];      % Purple
    colors.lick_burst = [0.5, 0.5, 0.5];      % Medium gray
    
    % MED-PC error highlighting
    colors.error_bg = [1.0, 0.9, 0.9];        % Light pink background
    colors.error_border = [0.9, 0.0, 0.0];    % Red border
    colors.warning = [1.0, 0.5, 0.0];         % Orange
    
    % Background and grid
    colors.background = [0.98, 0.98, 0.98];   % Very light gray
    colors.grid_major = [0.8, 0.8, 0.8];      % Light gray
    colors.grid_minor = [0.9, 0.9, 0.9];      % Very light gray
    
    % Schedule-specific colors
    colors.vi15_marker = [0.0, 0.6, 0.3];     % Green for VI15
    colors.fi5_marker = [0.0, 0.3, 0.6];      % Blue for FI5
    
    % Text and annotations
    colors.text_primary = [0.1, 0.1, 0.1];    % Near black
    colors.text_secondary = [0.4, 0.4, 0.4];  % Medium gray
    colors.annotation = [0.2, 0.2, 0.6];      % Dark blue
end

function real_data = load_real_trial_data(filename)
    % Load and parse real experimental data
    
    fprintf('Parsing MEDx file: %s\n', filename);
    
    % Read and parse the file (simplified version)
    ipt_data = readmatrix(filename);
    endlength = length(ipt_data);
    
    TF = ismissing(ipt_data);
    ipt_data(:,3) = [];
    ipt_data(:,1) = [];
    T_s = cumsum(TF);
    T_s(:,3) = [];
    T_s(:,1) = [];
    
    box = cat(2, ipt_data, T_s);
    index_B = box(18,2);
    
    % Extract events
    real_data.e_times = extract_events_at_position(box, endlength, index_B + 3);  % Go cue
    real_data.b_times = extract_events_at_position(box, endlength, index_B);      % Hit record
    real_data.h_times = extract_events_at_position(box, endlength, index_B + 6);  % Miss record
    real_data.w_times = extract_events_at_position(box, endlength, index_B + 13); % Hit detection
    real_data.c_times = extract_events_at_position(box, endlength, index_B + 1);  % All licks
    real_data.n_times = extract_events_at_position(box, endlength, index_B + 8);  % 1st lick
    
    % Analyze trial structure
    real_data.trials = analyze_real_trials(real_data);
    
    fprintf('Loaded %d trials with %d events total.\n', ...
            length(real_data.e_times), length(real_data.c_times));
end

function events = extract_events_at_position(box, endlength, position)
    % Extract events at specific cumulative position
    temp_box = box;
    
    for i = endlength:-1:1
        if temp_box(i,1) >= 0 && temp_box(i,2) == position
            % Keep this row
        else
            temp_box(i,:) = [];
        end
    end
    
    if ~isempty(temp_box)
        events = temp_box(:,1);
    else
        events = [];
    end
end

function trials = analyze_real_trials(data)
    % Analyze real trial structure with corrected timing
    
    trials = struct();
    e_times = sort(data.e_times);
    b_times = sort(data.b_times);
    h_times = sort(data.h_times);
    w_times = sort(data.w_times);
    c_times = sort(data.c_times);
    
    for i = 1:length(e_times)
        trials(i).number = i;
        trials(i).e_time = e_times(i);
        trials(i).type = 'Unknown';
        trials(i).licks = [];
        trials(i).w_detection = NaN;
        trials(i).iti = NaN;
        
        % Find licks in 0-1s window
        window_licks = c_times(c_times >= e_times(i) & c_times < e_times(i) + 1);
        trials(i).licks = window_licks - e_times(i);  % Relative to E
        
        % Find W detection
        w_in_trial = w_times(w_times > e_times(i) & w_times < e_times(i) + 2);
        if ~isempty(w_in_trial)
            trials(i).w_detection = w_in_trial(1) - e_times(i);
        end
        
        % Determine trial type (from next E recording)
        if i < length(e_times)
            next_e = e_times(i + 1);
            trials(i).iti = next_e - e_times(i);
            
            % Check what's recorded at next E
            has_b = any(abs(b_times - next_e) < 0.01);
            has_h = any(abs(h_times - next_e) < 0.01);
            
            if has_b
                trials(i).type = 'Hit';
            elseif has_h
                trials(i).type = 'Miss';
            end
        end
        
        % Determine correctness
        has_licks = ~isempty(trials(i).licks);
        if strcmp(trials(i).type, 'Hit') && has_licks
            trials(i).correct = true;
        elseif strcmp(trials(i).type, 'Miss') && ~has_licks
            trials(i).correct = true;
        else
            trials(i).correct = false;
        end
    end
end

function real_data = create_example_data()
    % Create realistic example data when real data unavailable
    
    real_data.trials = struct();
    
    % Example Hit trial
    real_data.trials(1).number = 15;
    real_data.trials(1).e_time = 257.81;
    real_data.trials(1).type = 'Hit';
    real_data.trials(1).licks = [0.31, 0.52, 0.73, 0.89];  % Relative times
    real_data.trials(1).w_detection = 1.01;
    real_data.trials(1).iti = 16.02;
    real_data.trials(1).correct = true;
    
    % Example Miss trial
    real_data.trials(2).number = 9;
    real_data.trials(2).e_time = 140.67;
    real_data.trials(2).type = 'Miss';
    real_data.trials(2).licks = [];  % No licks
    real_data.trials(2).w_detection = NaN;
    real_data.trials(2).iti = 18.52;
    real_data.trials(2).correct = true;
end

function create_enhanced_timecourse_plot(data, colors, use_real_data)
    % Create the main enhanced visualization
    
    %% Main title
    title_text = {
        '\fontsize{20}\bf Enhanced Go/No-Go Task Time Course Analysis'
        '\fontsize{16}\rm DT1878 (VI15 Schedule) | Real Data Integration'
        '\fontsize{14}\color{red}\bf ⚠ Corrected for MED-PC B/H Recording Delay'
    };
    
    sgtitle(title_text, 'Interpreter', 'tex', 'Color', colors.text_primary);
    
    %% Panel 1: Hit Trial with Real Data
    subplot(4, 1, 1);
    if use_real_data
        hit_trial = find_example_trial(data.trials, 'Hit');
        create_hit_trial_panel(hit_trial, colors, true);
    else
        create_hit_trial_panel(data.trials(1), colors, false);
    end
    
    %% Panel 2: Miss Trial with Real Data  
    subplot(4, 1, 2);
    if use_real_data
        miss_trial = find_example_trial(data.trials, 'Miss');
        create_miss_trial_panel(miss_trial, colors, true);
    else
        create_miss_trial_panel(data.trials(2), colors, false);
    end
    
    %% Panel 3: MED-PC Timing Error Explanation
    subplot(4, 1, 3);
    create_timing_error_panel(colors);
    
    %% Panel 4: Schedule and Statistics
    subplot(4, 1, 4);
    if use_real_data
        create_statistics_panel(data.trials, colors);
    else
        create_example_statistics_panel(colors);
    end
end

function trial = find_example_trial(trials, trial_type)
    % Find a good example trial of specified type
    
    candidates = [];
    for i = 1:length(trials)
        if strcmp(trials(i).type, trial_type) && trials(i).correct
            candidates(end+1) = i;
        end
    end
    
    if ~isempty(candidates)
        % Pick a trial with moderate lick count for Hit, or any for Miss
        if strcmp(trial_type, 'Hit')
            lick_counts = arrayfun(@(i) length(trials(i).licks), candidates);
            [~, idx] = min(abs(lick_counts - median(lick_counts)));
            trial = trials(candidates(idx));
        else
            trial = trials(candidates(1));
        end
    else
        % Fallback to first trial of type
        for i = 1:length(trials)
            if strcmp(trials(i).type, trial_type)
                trial = trials(i);
                return;
            end
        end
        trial = trials(1);  % Ultimate fallback
    end
end

function create_hit_trial_panel(trial, colors, is_real)
    % Create enhanced Hit trial visualization
    
    hold on;
    set(gca, 'Color', colors.background);
    
    time_range = [-1, 3];
    xlim(time_range);
    ylim([0, 1]);
    
    % Title
    if is_real
        title_str = sprintf('\\fontsize{14}\\bf Hit Trial #%d (Real Data) | VI15 Schedule', trial.number);
    else
        title_str = '\fontsize{14}\bf Hit Trial Example | VI15 Schedule';
    end
    title(title_str, 'Interpreter', 'tex', 'Color', colors.hit_detection);
    
    % Go cue at 0
    plot([0, 0], [0, 1], 'Color', colors.go_cue, 'LineWidth', 5);
    text(0, 1.05, 'Go Cue (E)', 'HorizontalAlignment', 'center', ...
         'FontSize', 12, 'FontWeight', 'bold', 'Color', colors.go_cue);
    
    % Judgment window
    patch([0, 1, 1, 0], [0.1, 0.1, 0.9, 0.9], colors.judgment_window, ...
          'FaceAlpha', 0.4, 'EdgeColor', colors.text_primary, 'LineWidth', 2);
    text(0.5, 0.05, 'Judgment Window', 'HorizontalAlignment', 'center', ...
         'FontSize', 10, 'FontWeight', 'bold');
    
    % Licks
    if ~isempty(trial.licks)
        for i = 1:length(trial.licks)
            lick_time = trial.licks(i);
            if i == 1
                % First lick - special marking
                plot([lick_time, lick_time], [0.2, 0.8], 'Color', colors.first_lick, ...
                     'LineWidth', 4);
                text(lick_time, 0.85, '1st', 'HorizontalAlignment', 'center', ...
                     'FontSize', 8, 'Color', colors.first_lick, 'FontWeight', 'bold');
            else
                % Other licks
                plot([lick_time, lick_time], [0.25, 0.75], 'Color', colors.lick_valid, ...
                     'LineWidth', 3);
            end
        end
        
        % Lick count annotation
        text(1.2, 0.7, sprintf('%d licks detected', length(trial.licks)), ...
             'FontSize', 11, 'Color', colors.text_primary, 'FontWeight', 'bold');
    end
    
    % W detection
    if ~isnan(trial.w_detection)
        plot([trial.w_detection, trial.w_detection], [0.15, 0.85], ...
             'Color', colors.hit_detection, 'LineWidth', 4, 'LineStyle', '--');
        text(trial.w_detection, 0.95, sprintf('Hit Detected\n(%.2fs)', trial.w_detection), ...
             'HorizontalAlignment', 'center', 'FontSize', 10, ...
             'Color', colors.hit_detection, 'FontWeight', 'bold');
    end
    
    % ITI indicator
    if ~isnan(trial.iti)
        arrow_start = 2.2;
        arrow_end = 2.2 + trial.iti * 0.1;  % Scale for display
        plot([arrow_start, arrow_end], [0.5, 0.5], 'k-', 'LineWidth', 2);
        plot(arrow_end, 0.5, '>', 'MarkerSize', 8, 'MarkerFaceColor', 'k');
        text((arrow_start + arrow_end)/2, 0.6, sprintf('ITI: %.1fs', trial.iti), ...
             'HorizontalAlignment', 'center', 'FontSize', 10);
    end
    
    xlabel('Time from Go Cue (s)', 'FontSize', 12, 'FontWeight', 'bold');
    ylabel('Events', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    set(gca, 'GridColor', colors.grid_major, 'GridAlpha', 0.6);
end

function create_miss_trial_panel(trial, colors, is_real)
    % Create enhanced Miss trial visualization
    
    hold on;
    set(gca, 'Color', colors.background);
    
    time_range = [-1, 3];
    xlim(time_range);
    ylim([0, 1]);
    
    % Title
    if is_real
        title_str = sprintf('\\fontsize{14}\\bf Miss Trial #%d (Real Data) | VI15 Schedule', trial.number);
    else
        title_str = '\fontsize{14}\bf Miss Trial Example | VI15 Schedule';
    end
    title(title_str, 'Interpreter', 'tex', 'Color', colors.miss_timeout);
    
    % Go cue at 0
    plot([0, 0], [0, 1], 'Color', colors.go_cue, 'LineWidth', 5);
    text(0, 1.05, 'Go Cue (E)', 'HorizontalAlignment', 'center', ...
         'FontSize', 12, 'FontWeight', 'bold', 'Color', colors.go_cue);
    
    % Judgment window
    patch([0, 1, 1, 0], [0.1, 0.1, 0.9, 0.9], colors.judgment_window, ...
          'FaceAlpha', 0.4, 'EdgeColor', colors.text_primary, 'LineWidth', 2);
    text(0.5, 0.05, 'Judgment Window', 'HorizontalAlignment', 'center', ...
         'FontSize', 10, 'FontWeight', 'bold');
    
    % No licks indication
    text(0.5, 0.5, 'No Licks Detected', 'HorizontalAlignment', 'center', ...
         'FontSize', 14, 'FontWeight', 'bold', 'Color', colors.miss_timeout);
    
    % Miss timeout
    text(1.2, 0.7, 'Miss → Timeout', 'FontSize', 11, ...
         'Color', colors.miss_timeout, 'FontWeight', 'bold');
    
    % ITI indicator
    if ~isnan(trial.iti)
        arrow_start = 2.2;
        arrow_end = 2.2 + trial.iti * 0.1;  % Scale for display
        plot([arrow_start, arrow_end], [0.5, 0.5], 'k-', 'LineWidth', 2);
        plot(arrow_end, 0.5, '>', 'MarkerSize', 8, 'MarkerFaceColor', 'k');
        text((arrow_start + arrow_end)/2, 0.6, sprintf('ITI: %.1fs', trial.iti), ...
             'HorizontalAlignment', 'center', 'FontSize', 10);
    end
    
    xlabel('Time from Go Cue (s)', 'FontSize', 12, 'FontWeight', 'bold');
    ylabel('Events', 'FontSize', 12, 'FontWeight', 'bold');
    grid on;
    set(gca, 'GridColor', colors.grid_major, 'GridAlpha', 0.6);
end

function create_timing_error_panel(colors)
    % Create MED-PC timing error explanation panel
    
    hold on;
    set(gca, 'Color', colors.error_bg);
    
    xlim([0, 10]);
    ylim([0, 10]);
    axis off;
    
    % Title
    text(5, 9.5, '⚠ MED-PC Timing Error Explanation', ...
         'HorizontalAlignment', 'center', 'FontSize', 16, 'FontWeight', 'bold', ...
         'Color', colors.error_border);
    
    % Error box
    rectangle('Position', [0.5, 5.5, 9, 3.5], 'EdgeColor', colors.error_border, ...
              'LineWidth', 3, 'FaceColor', 'white');
    
    % Error explanation
    error_text = {
        '\fontsize{13}\bf CRITICAL DISCOVERY:',
        '\fontsize{11}\rm B/H events recorded at NEXT trial start (same time as next E)',
        '',
        '\fontsize{12}\bf Impact on Analysis:',
        '\fontsize{10}\rm • Trial n outcome → Recorded at Trial n+1 beginning',
        '\fontsize{10}\rm • Creates apparent "10-22 second delays"',
        '\fontsize{10}\rm • These are actually Inter-Trial Intervals (ITI)',
        '\fontsize{10}\rm • Solution: Use E-based timeline for correct mapping'
    };
    
    text(1, 7.5, error_text, 'VerticalAlignment', 'middle', 'Interpreter', 'tex');
    
    % Correction note
    text(5, 4.5, 'All timelines in this figure use corrected E-based mapping', ...
         'HorizontalAlignment', 'center', 'FontSize', 12, 'FontWeight', 'bold', ...
         'Color', colors.annotation, ...
         'BackgroundColor', colors.judgment_window, 'EdgeColor', 'k');
    
    % Timeline comparison
    text(1, 3, '\fontsize{11}\bf Correct Timeline:', 'Interpreter', 'tex');
    text(1, 2.5, 'E(0s) → Licks(0-1s) → W(~1s) → ITI → Next E', 'FontSize', 10);
    
    text(1, 1.5, '\fontsize{11}\bf MED Recording:', 'Interpreter', 'tex', 'Color', colors.error_border);
    text(1, 1, 'E(0s) → Licks(0-1s) → W(~1s) → ITI → Next E + B/H', 'FontSize', 10, 'Color', colors.error_border);
end

function create_statistics_panel(trials, colors)
    % Create statistics panel with real data
    
    hold on;
    set(gca, 'Color', colors.background);
    
    xlim([0, 10]);
    ylim([0, 10]);
    axis off;
    
    % Title
    text(5, 9.5, 'DT1878 Session Statistics (Real Data)', ...
         'HorizontalAlignment', 'center', 'FontSize', 14, 'FontWeight', 'bold');
    
    % Calculate statistics
    total_trials = length(trials);
    hit_trials = sum(strcmp({trials.type}, 'Hit'));
    miss_trials = sum(strcmp({trials.type}, 'Miss'));
    correct_trials = sum([trials.correct]);
    
    itis = [trials.iti];
    itis = itis(~isnan(itis));
    
    % Display statistics
    stats_text = {
        sprintf('Total Trials: %d', total_trials),
        sprintf('Hit Trials: %d (%.1f%%)', hit_trials, hit_trials/total_trials*100),
        sprintf('Miss Trials: %d (%.1f%%)', miss_trials, miss_trials/total_trials*100),
        sprintf('Judgment Accuracy: %.1f%%', correct_trials/total_trials*100),
        '',
        sprintf('VI15 Schedule Performance:'),
        sprintf('Mean ITI: %.2f ± %.2f seconds', mean(itis), std(itis)),
        sprintf('ITI Range: %.2f - %.2f seconds', min(itis), max(itis))
    };
    
    text(1, 7.5, stats_text, 'VerticalAlignment', 'top', 'FontSize', 11);
    
    % Performance indicator
    accuracy = correct_trials/total_trials*100;
    if accuracy >= 90
        perf_color = colors.go_cue;
        perf_text = 'EXCELLENT';
    elseif accuracy >= 70
        perf_color = colors.warning;
        perf_text = 'GOOD';
    else
        perf_color = colors.error_border;
        perf_text = 'NEEDS REVIEW';
    end
    
    text(7, 6, sprintf('Performance: %s', perf_text), ...
         'FontSize', 12, 'FontWeight', 'bold', 'Color', perf_color, ...
         'BackgroundColor', 'white', 'EdgeColor', perf_color);
    
    % Schedule visualization
    text(5, 3, 'VI15 Schedule Visualization', 'HorizontalAlignment', 'center', ...
         'FontSize', 12, 'FontWeight', 'bold');
    
    % Simple ITI distribution
    iti_bins = 11:2:21;
    iti_counts = histcounts(itis, iti_bins);
    bar_width = 0.3;
    
    for i = 1:length(iti_counts)
        bar_height = iti_counts(i) / max(iti_counts) * 1.5;  % Normalize to max 1.5
        bar_x = 3 + i * 0.5;
        rectangle('Position', [bar_x, 0.5, bar_width, bar_height], ...
                  'FaceColor', colors.vi15_marker, 'EdgeColor', 'k');
        text(bar_x + bar_width/2, 0.3, sprintf('%d', iti_bins(i)), ...
             'HorizontalAlignment', 'center', 'FontSize', 8);
    end
    
    text(5, 0.1, 'ITI Distribution (seconds)', 'HorizontalAlignment', 'center', ...
         'FontSize', 10);
end

function create_example_statistics_panel(colors)
    % Create example statistics when real data unavailable
    
    hold on;
    set(gca, 'Color', colors.background);
    
    xlim([0, 10]);
    ylim([0, 10]);
    axis off;
    
    text(5, 9.5, 'Example Session Statistics', ...
         'HorizontalAlignment', 'center', 'FontSize', 14, 'FontWeight', 'bold');
    
    text(5, 7, 'Real data loading failed - showing example', ...
         'HorizontalAlignment', 'center', 'FontSize', 12, 'FontStyle', 'italic', ...
         'Color', colors.warning);
    
    example_text = {
        'Typical DT1878 Session:',
        '• 50 total trials',
        '• ~58% Hit rate (29 trials)',
        '• ~42% Miss rate (21 trials)',
        '• VI15: 11-21s variable intervals',
        '• High judgment accuracy when correctly mapped'
    };
    
    text(1, 5, example_text, 'VerticalAlignment', 'top', 'FontSize', 11);
end

function save_enhanced_figure(fig)
    % Save high-resolution figure
    
    timestamp = datestr(now, 'yyyymmdd_HHMMSS');
    
    % PNG for general use
    filename_png = sprintf('dt1878_timecourse_enhanced_%s.png', timestamp);
    print(fig, filename_png, '-dpng', '-r300');
    
    % EPS for publication
    filename_eps = sprintf('dt1878_timecourse_enhanced_%s.eps', timestamp);
    print(fig, filename_eps, '-depsc', '-r300');
    
    % PDF for presentations
    filename_pdf = sprintf('dt1878_timecourse_enhanced_%s.pdf', timestamp);
    print(fig, filename_pdf, '-dpdf', '-r300');
    
    fprintf('Enhanced figures saved:\n');
    fprintf('  PNG: %s\n', filename_png);
    fprintf('  EPS: %s\n', filename_eps);
    fprintf('  PDF: %s\n', filename_pdf);
end

% Execute the enhanced visualization
if exist('visualize_timecourse_enhanced', 'file')
    visualize_timecourse_enhanced();
end
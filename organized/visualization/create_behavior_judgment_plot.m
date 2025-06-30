%% Behavior Judgment Plot Creation for DT1878
% Creates comprehensive visualization of behavioral judgments with E-based timeline
% Corrects for MED-PC timing errors discovered by dev1

function create_behavior_judgment_plot()
    fprintf('=== Creating DT1878 Behavior Judgment Plot ===\n');
    
    % Load MEDx data
    data_file = 'D:\DN001_TF\2025_G00(DT1878,1899,1909)\Data_raw\20250629_DT1878_MEDx.txt';
    
    % Parse events (using existing batch file structure)
    events = parse_medx_events(data_file);
    
    % Analyze trials with E-based timeline
    trials = analyze_trials_e_based(events);
    
    % Create comprehensive plot
    create_main_plot(trials, events);
    
    % Save results
    save_trial_data(trials);
    
    fprintf('Behavior judgment plot creation completed.\n');
end

function events = parse_medx_events(filename)
    % Parse MEDx file to extract events
    fprintf('Loading data from: %s\n', filename);
    
    % Read the file (simplified version - in real implementation use proper parser)
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
    
    % Extract E events (Go cue)
    events.E = extract_event_at_position(box, endlength, index_B + 3);
    
    % Extract B events (Hit record)
    events.B = extract_event_at_position(box, endlength, index_B);
    
    % Extract H events (Miss record)
    events.H = extract_event_at_position(box, endlength, index_B + 6);
    
    % Extract W events (Hit detection)
    events.W = extract_event_at_position(box, endlength, index_B + 13);
    
    % Extract C events (All licks)
    events.C = extract_event_at_position(box, endlength, index_B + 1);
    
    % Extract N events (1st lick)
    events.N = extract_event_at_position(box, endlength, index_B + 8);
    
    fprintf('Events extracted:\n');
    fprintf('  E (Go cue): %d\n', length(events.E));
    fprintf('  B (Hit record): %d\n', length(events.B));
    fprintf('  H (Miss record): %d\n', length(events.H));
    fprintf('  W (Hit detection): %d\n', length(events.W));
    fprintf('  C (All licks): %d\n', length(events.C));
    fprintf('  N (1st lick): %d\n', length(events.N));
end

function event_times = extract_event_at_position(box, endlength, position)
    % Extract events at specific position
    event_times = [];
    temp_box = box;
    
    for i = endlength:-1:1
        if temp_box(i,1) >= 0 && temp_box(i,2) == position
            % Keep this row
        else
            temp_box(i,:) = [];
        end
    end
    
    if ~isempty(temp_box)
        event_times = temp_box(:,1);
    end
end

function trials = analyze_trials_e_based(events)
    % Analyze trials with E-based timeline
    fprintf('\nAnalyzing trials with E-based timeline...\n');
    
    E_times = sort(events.E);
    B_times = sort(events.B);
    H_times = sort(events.H);
    W_times = sort(events.W);
    C_times = sort(events.C);
    N_times = sort(events.N);
    
    trials = struct();
    
    for i = 1:length(E_times)
        trials(i).number = i;
        trials(i).e_time = E_times(i);
        trials(i).judgment = 'Unknown';
        trials(i).licks_in_window = [];
        trials(i).first_lick_time = NaN;
        trials(i).w_detection = NaN;
        trials(i).correct = NaN;
        
        % Find licks in 0-1s window
        window_start = E_times(i);
        window_end = E_times(i) + 1.0;
        licks_in_window = C_times(C_times >= window_start & C_times < window_end);
        trials(i).licks_in_window = licks_in_window;
        trials(i).lick_count = length(licks_in_window);
        
        % Find first lick in window
        first_licks = N_times(N_times >= window_start & N_times < window_end);
        if ~isempty(first_licks)
            trials(i).first_lick_time = first_licks(1) - E_times(i);
        end
        
        % Find W detection for this trial
        w_for_trial = W_times(W_times > E_times(i) & W_times < E_times(i) + 2);
        if ~isempty(w_for_trial)
            trials(i).w_detection = w_for_trial(1) - E_times(i);
        end
        
        % Determine judgment (from next trial recording)
        if i < length(E_times)
            next_e = E_times(i + 1);
            
            % Check what's recorded at next E (within 0.01s)
            has_b = any(abs(B_times - next_e) < 0.01);
            has_h = any(abs(H_times - next_e) < 0.01);
            
            if has_b
                trials(i).judgment = 'Hit';
            elseif has_h
                trials(i).judgment = 'Miss';
            end
        end
        
        % Determine correctness
        has_lick = trials(i).lick_count > 0;
        if ~strcmp(trials(i).judgment, 'Unknown')
            if strcmp(trials(i).judgment, 'Hit') && has_lick
                trials(i).correct = 1;
            elseif strcmp(trials(i).judgment, 'Miss') && ~has_lick
                trials(i).correct = 1;
            else
                trials(i).correct = 0;
            end
        end
    end
    
    % Print summary
    hit_count = sum(strcmp({trials.judgment}, 'Hit'));
    miss_count = sum(strcmp({trials.judgment}, 'Miss'));
    correct_count = sum([trials.correct] == 1);
    judged_count = sum(~isnan([trials.correct]));
    
    fprintf('Trial analysis summary:\n');
    fprintf('  Total trials: %d\n', length(trials));
    fprintf('  Hit judgments: %d\n', hit_count);
    fprintf('  Miss judgments: %d\n', miss_count);
    fprintf('  Correct judgments: %d/%d (%.1f%%)\n', correct_count, judged_count, correct_count/judged_count*100);
end

function create_main_plot(trials, events)
    % Create comprehensive behavioral plot
    fprintf('\nCreating behavioral judgment plot...\n');
    
    % Create figure with subplots
    figure('Position', [100, 100, 1400, 1000]);
    
    % Define colors (high contrast, colorblind-friendly)
    colors.go_cue = [0, 0.5, 0];      % Dark green
    colors.hit = [0, 0, 0.7];         % Dark blue
    colors.miss = [0.7, 0, 0];        % Dark red
    colors.lick = [0.3, 0.3, 0.3];    % Dark gray
    colors.first_lick = [0.8, 0, 0.8]; % Purple
    colors.window = [1, 1, 0];        % Yellow
    colors.correct = [0, 0.6, 0];     % Green
    colors.error = [1, 0, 0];         % Red
    
    % Plot 1: Trial-by-trial raster plot
    subplot(3, 1, 1);
    create_raster_plot(trials, colors);
    
    % Plot 2: Judgment accuracy summary
    subplot(3, 1, 2);
    create_judgment_summary(trials, colors);
    
    % Plot 3: Lick behavior patterns
    subplot(3, 1, 3);
    create_lick_patterns(trials, colors);
    
    % Main title
    sgtitle({'DT1878 Behavior Judgment Analysis - E-based Timeline'; ...
             'VI15 Schedule | 0s = Go cue | Corrected for MED-PC timing error'}, ...
            'FontSize', 16, 'FontWeight', 'bold');
    
    % Save figure
    timestamp = datestr(now, 'yyyymmdd_HHMMSS');
    filename = sprintf('dt1878_behavior_judgment_plot_%s', timestamp);
    saveas(gcf, filename, 'png');
    fprintf('Plot saved as: %s.png\n', filename);
end

function create_raster_plot(trials, colors)
    % Create trial-by-trial raster plot
    title('Trial-by-Trial Raster Plot (E-based timeline)', 'FontSize', 14, 'FontWeight', 'bold');
    hold on;
    
    n_trials = length(trials);
    
    for i = 1:n_trials
        trial = trials(i);
        y_pos = n_trials - i + 1; % Reverse order
        
        % Go cue at 0
        plot([0, 0], [y_pos-0.3, y_pos+0.3], 'Color', colors.go_cue, 'LineWidth', 3);
        
        % Judgment window
        fill([0, 1, 1, 0], [y_pos-0.2, y_pos-0.2, y_pos+0.2, y_pos+0.2], ...
             colors.window, 'FaceAlpha', 0.3, 'EdgeColor', 'none');
        
        % Licks in window
        for j = 1:length(trial.licks_in_window)
            lick_time = trial.licks_in_window(j) - trial.e_time;
            plot([lick_time, lick_time], [y_pos-0.15, y_pos+0.15], ...
                 'Color', colors.lick, 'LineWidth', 2);
        end
        
        % First lick marker
        if ~isnan(trial.first_lick_time)
            plot([trial.first_lick_time, trial.first_lick_time], ...
                 [y_pos-0.25, y_pos+0.25], ...
                 'Color', colors.first_lick, 'LineWidth', 3);
        end
        
        % W detection
        if ~isnan(trial.w_detection)
            plot([trial.w_detection, trial.w_detection], ...
                 [y_pos-0.3, y_pos+0.3], ...
                 'Color', colors.hit, 'LineWidth', 2, 'LineStyle', '--');
        end
        
        % Judgment background
        if strcmp(trial.judgment, 'Hit')
            fill([-0.5, 2.5, 2.5, -0.5], [y_pos-0.4, y_pos-0.4, y_pos+0.4, y_pos+0.4], ...
                 colors.hit, 'FaceAlpha', 0.1, 'EdgeColor', 'none');
        elseif strcmp(trial.judgment, 'Miss')
            fill([-0.5, 2.5, 2.5, -0.5], [y_pos-0.4, y_pos-0.4, y_pos+0.4, y_pos+0.4], ...
                 colors.miss, 'FaceAlpha', 0.1, 'EdgeColor', 'none');
        end
        
        % Correctness indicator
        if ~isnan(trial.correct)
            marker_color = colors.correct;
            if trial.correct == 0
                marker_color = colors.error;
            end
            plot(2.2, y_pos, 'o', 'Color', marker_color, 'MarkerSize', 6, 'MarkerFaceColor', marker_color);
        end
    end
    
    xlim([-0.5, 2.5]);
    ylim([0.5, n_trials + 0.5]);
    xlabel('Time from Go cue (s)');
    ylabel('Trial number (reversed)');
    grid on;
    grid('minor');
    
    % Add legend
    legend_x = 1.8;
    legend_y = n_trials * 0.95;
    text(legend_x, legend_y, 'Legend:', 'FontSize', 10, 'FontWeight', 'bold');
    text(legend_x, legend_y-2, '— Go cue', 'Color', colors.go_cue, 'FontSize', 9);
    text(legend_x, legend_y-4, '— Licks', 'Color', colors.lick, 'FontSize', 9);
    text(legend_x, legend_y-6, '— 1st Lick', 'Color', colors.first_lick, 'FontSize', 9);
    text(legend_x, legend_y-8, '-- W detect', 'Color', colors.hit, 'FontSize', 9);
end

function create_judgment_summary(trials, colors)
    % Create judgment accuracy summary
    title('Judgment Accuracy Summary', 'FontSize', 14, 'FontWeight', 'bold');
    hold on;
    
    % Count judgments
    hit_correct = sum(strcmp({trials.judgment}, 'Hit') & [trials.correct] == 1);
    hit_incorrect = sum(strcmp({trials.judgment}, 'Hit') & [trials.correct] == 0);
    miss_correct = sum(strcmp({trials.judgment}, 'Miss') & [trials.correct] == 1);
    miss_incorrect = sum(strcmp({trials.judgment}, 'Miss') & [trials.correct] == 0);
    unknown = sum(strcmp({trials.judgment}, 'Unknown'));
    
    % Create bar chart
    categories = {'Hit\n(Correct)', 'Hit\n(Incorrect)', 'Miss\n(Correct)', 'Miss\n(Incorrect)', 'Unknown'};
    values = [hit_correct, hit_incorrect, miss_correct, miss_incorrect, unknown];
    bar_colors = [colors.correct; colors.error; colors.correct; colors.error; [0.5, 0.5, 0.5]];
    
    b = bar(1:5, values, 'FaceColor', 'flat');
    b.CData = bar_colors;
    
    % Add value labels
    for i = 1:5
        if values(i) > 0
            text(i, values(i) + 0.5, num2str(values(i)), ...
                 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
        end
    end
    
    % Calculate accuracy
    total_judged = hit_correct + hit_incorrect + miss_correct + miss_incorrect;
    if total_judged > 0
        accuracy = (hit_correct + miss_correct) / total_judged * 100;
        text(3, max(values) * 0.9, sprintf('Overall Accuracy: %.1f%%', accuracy), ...
             'HorizontalAlignment', 'center', 'FontSize', 14, 'FontWeight', 'bold', ...
             'BackgroundColor', 'lightblue');
    end
    
    set(gca, 'XTick', 1:5, 'XTickLabel', categories);
    ylabel('Number of trials');
    ylim([0, max(values) * 1.2]);
    grid on;
end

function create_lick_patterns(trials, colors)
    % Create lick pattern analysis
    title('Lick Behavior Patterns', 'FontSize', 14, 'FontWeight', 'bold');
    hold on;
    
    % Get lick counts
    hit_lick_counts = [];
    miss_lick_counts = [];
    
    for i = 1:length(trials)
        if strcmp(trials(i).judgment, 'Hit')
            hit_lick_counts(end+1) = trials(i).lick_count;
        elseif strcmp(trials(i).judgment, 'Miss')
            miss_lick_counts(end+1) = trials(i).lick_count;
        end
    end
    
    % Create histogram
    max_licks = max([hit_lick_counts, miss_lick_counts, 1]);
    bins = 0:max_licks;
    
    hit_hist = hist(hit_lick_counts, bins);
    miss_hist = hist(miss_lick_counts, bins);
    
    % Plot histograms
    bar(bins - 0.2, hit_hist, 0.4, 'FaceColor', colors.hit, 'FaceAlpha', 0.7, ...
        'DisplayName', sprintf('Hit trials (n=%d)', length(hit_lick_counts)));
    bar(bins + 0.2, miss_hist, 0.4, 'FaceColor', colors.miss, 'FaceAlpha', 0.7, ...
        'DisplayName', sprintf('Miss trials (n=%d)', length(miss_lick_counts)));
    
    xlabel('Number of licks in 0-1s window');
    ylabel('Number of trials');
    legend('Location', 'best');
    grid on;
    
    % Add mean lines
    if ~isempty(hit_lick_counts)
        hit_mean = mean(hit_lick_counts);
        line([hit_mean, hit_mean], ylim, 'Color', colors.hit, 'LineStyle', '--', 'LineWidth', 2);
        text(hit_mean + 0.1, max(ylim) * 0.9, sprintf('Hit mean: %.1f', hit_mean), ...
             'Color', colors.hit, 'FontWeight', 'bold');
    end
    
    if ~isempty(miss_lick_counts)
        miss_mean = mean(miss_lick_counts);
        line([miss_mean, miss_mean], ylim, 'Color', colors.miss, 'LineStyle', '--', 'LineWidth', 2);
        text(miss_mean + 0.1, max(ylim) * 0.8, sprintf('Miss mean: %.1f', miss_mean), ...
             'Color', colors.miss, 'FontWeight', 'bold');
    end
end

function save_trial_data(trials)
    % Save detailed trial data
    timestamp = datestr(now, 'yyyymmdd_HHMMSS');
    filename = sprintf('dt1878_behavior_summary_%s.txt', timestamp);
    
    fid = fopen(filename, 'w');
    fprintf(fid, 'DT1878 Behavior Judgment Analysis Summary\n');
    fprintf(fid, '==================================================\n\n');
    
    fprintf(fid, 'Total trials analyzed: %d\n', length(trials));
    
    hit_trials = sum(strcmp({trials.judgment}, 'Hit'));
    miss_trials = sum(strcmp({trials.judgment}, 'Miss'));
    correct_trials = sum([trials.correct] == 1);
    judged_trials = sum(~isnan([trials.correct]));
    
    fprintf(fid, 'Hit judgments: %d\n', hit_trials);
    fprintf(fid, 'Miss judgments: %d\n', miss_trials);
    fprintf(fid, 'Correct judgments: %d\n', correct_trials);
    
    if judged_trials > 0
        accuracy = correct_trials / judged_trials * 100;
        fprintf(fid, 'Accuracy: %.1f%%\n\n', accuracy);
    end
    
    fprintf(fid, 'Trial Details:\n');
    fprintf(fid, '------------------------------\n');
    for i = 1:length(trials)
        trial = trials(i);
        fprintf(fid, 'Trial %2d: %4s | Licks: %2d | Correct: %d\n', ...
                trial.number, trial.judgment, trial.lick_count, trial.correct);
    end
    
    fclose(fid);
    fprintf('Summary saved as: %s\n', filename);
end

% Main execution
if exist('create_behavior_judgment_plot', 'file')
    create_behavior_judgment_plot();
end
%% Interactive Time Course Viewer
% User-friendly interface for exploring DT1878 timing data
% Features: Trial navigation, zoom, overlay options, export

function interactive_timecourse_viewer()
    clear all; close all;
    
    fprintf('=== Interactive Time Course Viewer ===\n');
    fprintf('Loading DT1878 data...\n');
    
    %% Load data
    try
        data = load_session_data();
        fprintf('Data loaded: %d trials\n', length(data.trials));
    catch
        fprintf('Error loading data. Using example.\n');
        data = create_example_session();
    end
    
    %% Create interactive GUI
    create_interactive_gui(data);
end

function data = load_session_data()
    % Load and process session data
    
    data_file = 'D:\DN001_TF\2025_G00(DT1878,1899,1909)\Data_raw\20250629_DT1878_MEDx.txt';
    
    % Parse MEDx file (simplified)
    ipt_data = readmatrix(data_file);
    endlength = length(ipt_data);
    
    TF = ismissing(ipt_data);
    ipt_data(:,3) = [];
    ipt_data(:,1) = [];
    T_s = cumsum(TF);
    T_s(:,3) = [];
    T_s(:,1) = [];
    
    box = cat(2, ipt_data, T_s);
    index_B = box(18,2);
    
    % Extract all events
    events.E = extract_events_at_position(box, endlength, index_B + 3);
    events.B = extract_events_at_position(box, endlength, index_B);
    events.H = extract_events_at_position(box, endlength, index_B + 6);
    events.W = extract_events_at_position(box, endlength, index_B + 13);
    events.C = extract_events_at_position(box, endlength, index_B + 1);
    events.N = extract_events_at_position(box, endlength, index_B + 8);
    
    % Analyze trials
    data.trials = analyze_session_trials(events);
    data.events = events;
    data.session_info = get_session_info();
end

function events = extract_events_at_position(box, endlength, position)
    temp_box = box;
    for i = endlength:-1:1
        if temp_box(i,1) >= 0 && temp_box(i,2) == position
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

function trials = analyze_session_trials(events)
    % Comprehensive trial analysis
    
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
        trials(i).licks = [];
        trials(i).lick_times = [];
        trials(i).first_lick = NaN;
        trials(i).w_detection = NaN;
        trials(i).iti = NaN;
        trials(i).correct = false;
        
        % Find licks in judgment window
        window_licks = C_times(C_times >= E_times(i) & C_times < E_times(i) + 1);
        trials(i).lick_times = window_licks;
        trials(i).licks = window_licks - E_times(i);  % Relative to E
        trials(i).lick_count = length(window_licks);
        
        % Find first lick
        first_licks = N_times(N_times >= E_times(i) & N_times < E_times(i) + 1);
        if ~isempty(first_licks)
            trials(i).first_lick = first_licks(1) - E_times(i);
        end
        
        % Find W detection
        w_in_trial = W_times(W_times > E_times(i) & W_times < E_times(i) + 2);
        if ~isempty(w_in_trial)
            trials(i).w_detection = w_in_trial(1) - E_times(i);
        end
        
        % Determine judgment from next trial recording
        if i < length(E_times)
            next_e = E_times(i + 1);
            trials(i).iti = next_e - E_times(i);
            
            % Check B/H at next E
            has_b = any(abs(B_times - next_e) < 0.01);
            has_h = any(abs(H_times - next_e) < 0.01);
            
            if has_b
                trials(i).judgment = 'Hit';
            elseif has_h
                trials(i).judgment = 'Miss';
            end
        end
        
        % Determine correctness
        expected_hit = trials(i).lick_count > 0;
        actual_hit = strcmp(trials(i).judgment, 'Hit');
        trials(i).correct = (expected_hit == actual_hit);
        
        % Performance metrics
        trials(i).reaction_time = trials(i).first_lick;
        trials(i).lick_rate = trials(i).lick_count;  % Licks per second (in 1s window)
    end
end

function session_info = get_session_info()
    % Session metadata
    session_info.animal = 'DT1878';
    session_info.date = '2025-06-29';
    session_info.schedule = 'VI15';
    session_info.task = 'Go/No-Go';
    session_info.corrected_analysis = true;
end

function data = create_example_session()
    % Example data when real data unavailable
    
    data.trials = struct();
    for i = 1:10
        data.trials(i).number = i;
        data.trials(i).judgment = mod(i,3)==0 ? 'Miss' : 'Hit';
        data.trials(i).licks = rand(1, randi(5)) * 0.8 + 0.1;
        data.trials(i).correct = true;
        data.trials(i).iti = 15 + randn() * 3;
    end
    
    data.session_info = get_session_info();
end

function create_interactive_gui(data)
    % Create the main interactive interface
    
    %% Main figure
    fig = figure('Position', [100, 100, 1600, 900], 'Name', 'Interactive Time Course Viewer', ...
                 'NumberTitle', 'off', 'Color', 'white', 'Toolbar', 'none', 'MenuBar', 'none');
    
    %% Create UI components
    create_control_panel(fig, data);
    create_main_display(fig, data);
    create_info_panel(fig, data);
    
    %% Store data in figure
    setappdata(fig, 'data', data);
    setappdata(fig, 'current_trial', 1);
    setappdata(fig, 'display_options', get_default_options());
    
    %% Update initial display
    update_display(fig);
    
    fprintf('Interactive viewer ready. Use controls to explore data.\n');
end

function create_control_panel(fig, data)
    % Create control panel with navigation and options
    
    % Control panel background
    control_panel = uipanel('Parent', fig, 'Position', [0.02, 0.02, 0.25, 0.96], ...
                           'Title', 'Controls', 'FontSize', 12, 'FontWeight', 'bold');
    
    % Session info
    uicontrol('Parent', control_panel, 'Style', 'text', ...
              'Position', [10, 500, 180, 60], ...
              'String', sprintf('%s - %s\n%s Task (%s)', ...
                               data.session_info.animal, data.session_info.date, ...
                               data.session_info.task, data.session_info.schedule), ...
              'FontSize', 11, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
    
    % Trial navigation
    uicontrol('Parent', control_panel, 'Style', 'text', ...
              'Position', [10, 460, 100, 20], 'String', 'Trial Navigation:', ...
              'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'left');
    
    % Trial selector
    trial_numbers = 1:length(data.trials);
    uicontrol('Parent', control_panel, 'Style', 'popupmenu', ...
              'Position', [10, 430, 180, 25], ...
              'String', arrayfun(@(x) sprintf('Trial %d', x), trial_numbers, 'UniformOutput', false), ...
              'Callback', @(src,evt) trial_selection_callback(fig, src), ...
              'Tag', 'trial_selector');
    
    % Navigation buttons
    uicontrol('Parent', control_panel, 'Style', 'pushbutton', ...
              'Position', [10, 400, 85, 25], 'String', '← Previous', ...
              'Callback', @(src,evt) navigate_trial(fig, -1));
    
    uicontrol('Parent', control_panel, 'Style', 'pushbutton', ...
              'Position', [105, 400, 85, 25], 'String', 'Next →', ...
              'Callback', @(src,evt) navigate_trial(fig, 1));
    
    % Display options
    uicontrol('Parent', control_panel, 'Style', 'text', ...
              'Position', [10, 360, 100, 20], 'String', 'Display Options:', ...
              'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'left');
    
    % Checkboxes for display elements
    uicontrol('Parent', control_panel, 'Style', 'checkbox', ...
              'Position', [10, 335, 180, 20], 'String', 'Show Judgment Window', ...
              'Value', 1, 'Tag', 'show_window', ...
              'Callback', @(src,evt) update_display_options(fig));
    
    uicontrol('Parent', control_panel, 'Style', 'checkbox', ...
              'Position', [10, 310, 180, 20], 'String', 'Show Lick Details', ...
              'Value', 1, 'Tag', 'show_licks', ...
              'Callback', @(src,evt) update_display_options(fig));
    
    uicontrol('Parent', control_panel, 'Style', 'checkbox', ...
              'Position', [10, 285, 180, 20], 'String', 'Show W Detection', ...
              'Value', 1, 'Tag', 'show_w', ...
              'Callback', @(src,evt) update_display_options(fig));
    
    uicontrol('Parent', control_panel, 'Style', 'checkbox', ...
              'Position', [10, 260, 180, 20], 'String', 'Show ITI', ...
              'Value', 1, 'Tag', 'show_iti', ...
              'Callback', @(src,evt) update_display_options(fig));
    
    % Filter options
    uicontrol('Parent', control_panel, 'Style', 'text', ...
              'Position', [10, 220, 100, 20], 'String', 'Filter Trials:', ...
              'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'left');
    
    uicontrol('Parent', control_panel, 'Style', 'popupmenu', ...
              'Position', [10, 190, 180, 25], ...
              'String', {'All Trials', 'Hit Trials Only', 'Miss Trials Only', 'Correct Only', 'Incorrect Only'}, ...
              'Tag', 'trial_filter', ...
              'Callback', @(src,evt) apply_trial_filter(fig));
    
    % Statistics display
    uicontrol('Parent', control_panel, 'Style', 'text', ...
              'Position', [10, 150, 100, 20], 'String', 'Session Stats:', ...
              'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'left');
    
    stats_text = get_session_stats_text(data);
    uicontrol('Parent', control_panel, 'Style', 'text', ...
              'Position', [10, 50, 180, 95], 'String', stats_text, ...
              'FontSize', 9, 'HorizontalAlignment', 'left', 'Tag', 'stats_display');
    
    % Export button
    uicontrol('Parent', control_panel, 'Style', 'pushbutton', ...
              'Position', [10, 15, 180, 30], 'String', 'Export Current View', ...
              'FontSize', 10, 'FontWeight', 'bold', ...
              'Callback', @(src,evt) export_current_view(fig));
end

function create_main_display(fig, data)
    % Create main visualization area
    
    % Main axes for time course
    main_axes = axes('Parent', fig, 'Position', [0.3, 0.55, 0.65, 0.4], ...
                     'Tag', 'main_axes');
    title('Trial Time Course', 'FontSize', 14, 'FontWeight', 'bold');
    
    % Secondary axes for overview
    overview_axes = axes('Parent', fig, 'Position', [0.3, 0.05, 0.65, 0.4], ...
                        'Tag', 'overview_axes');
    title('Session Overview', 'FontSize', 14, 'FontWeight', 'bold');
end

function create_info_panel(fig, data)
    % Create information panel for current trial details
    
    info_panel = uipanel('Parent', fig, 'Position', [0.3, 0.02, 0.65, 0.02], ...
                        'Title', 'Trial Information', 'FontSize', 10);
    
    % Will be populated by update_display
end

function update_display(fig)
    % Update all display elements
    
    data = getappdata(fig, 'data');
    current_trial = getappdata(fig, 'current_trial');
    options = getappdata(fig, 'display_options');
    
    % Update main time course display
    update_main_timecourse(fig, data.trials(current_trial), options);
    
    % Update overview display
    update_session_overview(fig, data.trials, current_trial, options);
    
    % Update trial selector
    trial_selector = findobj(fig, 'Tag', 'trial_selector');
    set(trial_selector, 'Value', current_trial);
end

function update_main_timecourse(fig, trial, options)
    % Update main time course visualization
    
    main_axes = findobj(fig, 'Tag', 'main_axes');
    axes(main_axes);
    cla;
    hold on;
    
    % Define colors
    colors = get_display_colors();
    
    % Time range
    xlim([-0.5, 2.5]);
    ylim([0, 1]);
    
    % Go cue at 0
    plot([0, 0], [0, 1], 'Color', colors.go_cue, 'LineWidth', 4);
    text(0, 1.05, 'Go Cue', 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    
    % Judgment window
    if options.show_window
        patch([0, 1, 1, 0], [0.1, 0.1, 0.9, 0.9], colors.window, ...
              'FaceAlpha', 0.3, 'EdgeColor', 'k');
        text(0.5, 0.05, 'Judgment Window', 'HorizontalAlignment', 'center', ...
             'FontSize', 9);
    end
    
    % Licks
    if options.show_licks && ~isempty(trial.licks)
        for i = 1:length(trial.licks)
            lick_time = trial.licks(i);
            if i == 1
                plot([lick_time, lick_time], [0.2, 0.8], 'Color', colors.first_lick, ...
                     'LineWidth', 3);
            else
                plot([lick_time, lick_time], [0.25, 0.75], 'Color', colors.lick, ...
                     'LineWidth', 2);
            end
        end
        
        text(1.2, 0.8, sprintf('%d licks', length(trial.licks)), ...
             'FontSize', 10, 'FontWeight', 'bold');
    end
    
    % W detection
    if options.show_w && ~isnan(trial.w_detection)
        plot([trial.w_detection, trial.w_detection], [0.15, 0.85], ...
             'Color', colors.hit, 'LineWidth', 3, 'LineStyle', '--');
        text(trial.w_detection, 0.95, sprintf('W: %.2fs', trial.w_detection), ...
             'HorizontalAlignment', 'center', 'FontSize', 9);
    end
    
    % ITI display
    if options.show_iti && ~isnan(trial.iti)
        text(2.0, 0.5, sprintf('ITI: %.1fs', trial.iti), ...
             'FontSize', 10, 'HorizontalAlignment', 'center');
    end
    
    % Trial info
    judgment_color = strcmp(trial.judgment, 'Hit') ? colors.hit : colors.miss;
    correctness = trial.correct ? '✓' : '✗';
    
    title(sprintf('Trial %d: %s %s', trial.number, trial.judgment, correctness), ...
          'FontSize', 14, 'Color', judgment_color);
    
    xlabel('Time from Go Cue (s)');
    ylabel('Events');
    grid on;
end

function update_session_overview(fig, trials, current_trial, options)
    % Update session overview display
    
    overview_axes = findobj(fig, 'Tag', 'overview_axes');
    axes(overview_axes);
    cla;
    hold on;
    
    colors = get_display_colors();
    
    % Plot trial performance
    trial_numbers = [trials.number];
    hit_trials = strcmp({trials.judgment}, 'Hit');
    miss_trials = strcmp({trials.judgment}, 'Miss');
    correct_trials = [trials.correct];
    
    % Performance bars
    for i = 1:length(trials)
        if hit_trials(i)
            bar_color = correct_trials(i) ? colors.hit : colors.error;
            bar(i, 1, 'FaceColor', bar_color, 'EdgeColor', 'k');
        else
            bar_color = correct_trials(i) ? colors.miss : colors.error;
            bar(i, -1, 'FaceColor', bar_color, 'EdgeColor', 'k');
        end
    end
    
    % Highlight current trial
    bar(current_trial, hit_trials(current_trial) ? 1 : -1, ...
        'FaceColor', 'none', 'EdgeColor', 'black', 'LineWidth', 3);
    
    xlim([0.5, length(trials) + 0.5]);
    ylim([-1.5, 1.5]);
    xlabel('Trial Number');
    ylabel('Hit (+1) / Miss (-1)');
    title('Session Overview (Highlighted = Current Trial)');
    
    % Add accuracy line
    accuracy_line = cumsum(correct_trials) ./ (1:length(trials)) * 2 - 1;
    plot(trial_numbers, accuracy_line, 'k--', 'LineWidth', 2);
    
    legend({'Hit (Correct)', 'Miss (Correct)', 'Incorrect', 'Current Trial', 'Cumulative Accuracy'}, ...
           'Location', 'best');
end

function colors = get_display_colors()
    % Standard color scheme for display
    colors.go_cue = [0, 0.5, 0];
    colors.hit = [0, 0, 0.7];
    colors.miss = [0.7, 0, 0];
    colors.lick = [0.3, 0.3, 0.3];
    colors.first_lick = [0.8, 0, 0.8];
    colors.window = [1, 1, 0];
    colors.error = [1, 0, 0];
end

function options = get_default_options()
    % Default display options
    options.show_window = true;
    options.show_licks = true;
    options.show_w = true;
    options.show_iti = true;
end

function stats_text = get_session_stats_text(data)
    % Generate session statistics text
    
    trials = data.trials;
    total = length(trials);
    hits = sum(strcmp({trials.judgment}, 'Hit'));
    misses = sum(strcmp({trials.judgment}, 'Miss'));
    correct = sum([trials.correct]);
    
    stats_text = sprintf(['Total: %d trials\n' ...
                         'Hits: %d (%.1f%%)\n' ...
                         'Misses: %d (%.1f%%)\n' ...
                         'Accuracy: %.1f%%\n' ...
                         'Schedule: %s'], ...
                         total, hits, hits/total*100, ...
                         misses, misses/total*100, ...
                         correct/total*100, ...
                         data.session_info.schedule);
end

% Callback functions
function trial_selection_callback(fig, src)
    trial_num = get(src, 'Value');
    setappdata(fig, 'current_trial', trial_num);
    update_display(fig);
end

function navigate_trial(fig, direction)
    current = getappdata(fig, 'current_trial');
    data = getappdata(fig, 'data');
    new_trial = max(1, min(length(data.trials), current + direction));
    setappdata(fig, 'current_trial', new_trial);
    update_display(fig);
end

function update_display_options(fig)
    options = getappdata(fig, 'display_options');
    
    options.show_window = get(findobj(fig, 'Tag', 'show_window'), 'Value');
    options.show_licks = get(findobj(fig, 'Tag', 'show_licks'), 'Value');
    options.show_w = get(findobj(fig, 'Tag', 'show_w'), 'Value');
    options.show_iti = get(findobj(fig, 'Tag', 'show_iti'), 'Value');
    
    setappdata(fig, 'display_options', options);
    update_display(fig);
end

function apply_trial_filter(fig)
    % Apply trial filtering (placeholder for full implementation)
    fprintf('Trial filter applied (feature in development)\n');
end

function export_current_view(fig)
    % Export current view to file
    timestamp = datestr(now, 'yyyymmdd_HHMMSS');
    filename = sprintf('interactive_view_export_%s', timestamp);
    
    print(fig, filename, '-dpng', '-r300');
    fprintf('View exported as: %s.png\n', filename);
end

% Main execution
if exist('interactive_timecourse_viewer', 'file')
    interactive_timecourse_viewer();
end
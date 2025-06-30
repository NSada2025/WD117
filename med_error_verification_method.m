function med_error_verification(data_file, schedule_type, animal_id)
% MED Error Verification Method - MEDエラー検証方法
% Verifies timing errors in B/H event recording
%
% Inputs:
%   data_file: Path to MEDx data file
%   schedule_type: 'VI15' or 'FI5'
%   animal_id: 'DT1878', 'DT1899', etc.
%
% Error Description:
%   E (Go cue) and B/H (Hit/Miss) are recorded at the SAME time
%   This is incorrect - B/H[n] should be the result of trial n-1

fprintf('=== MED Error Verification | MEDエラー検証 ===\n');
fprintf('Animal: %s, Schedule: %s\n', animal_id, schedule_type);
fprintf('File: %s\n\n', data_file);

%% 1. Load and parse data
[E_times, B_times, H_times, W_times] = parse_medx_data(data_file);

%% 2. Verify timing relationships
fprintf('--- Timing Relationship Verification | タイミング関係検証 ---\n\n');

% Check E-B coincidence
n_coincident_B = 0;
B_errors = [];
for i = 1:length(B_times)
    % Find closest E
    [min_diff, idx] = min(abs(E_times - B_times(i)));
    if min_diff < 0.01  % Same time (within 10ms)
        n_coincident_B = n_coincident_B + 1;
        B_errors(end+1,:) = [i, E_times(idx), B_times(i), min_diff];
    end
end

% Check E-H coincidence
n_coincident_H = 0;
H_errors = [];
for i = 1:length(H_times)
    % Find closest E
    [min_diff, idx] = min(abs(E_times - H_times(i)));
    if min_diff < 0.01  % Same time (within 10ms)
        n_coincident_H = n_coincident_H + 1;
        H_errors(end+1,:) = [i, E_times(idx), H_times(i), min_diff];
    end
end

%% 3. Display error statistics
fprintf('ERROR STATISTICS | エラー統計:\n');
fprintf('B events coincident with E: %d/%d (%.1f%%)\n', ...
    n_coincident_B, length(B_times), n_coincident_B/length(B_times)*100);
fprintf('H events coincident with E: %d/%d (%.1f%%)\n', ...
    n_coincident_H, length(H_times), n_coincident_H/length(H_times)*100);
fprintf('\n⚠ ERROR RATE | エラー率: %.1f%%\n\n', ...
    (n_coincident_B + n_coincident_H)/(length(B_times) + length(H_times))*100);

%% 4. Show specific examples
fprintf('--- Example Errors | エラー例 ---\n');
fprintf('Expected: B/H[n] recorded after judgment window (0-1s) of trial n-1\n');
fprintf('期待値: B/H[n]は試行n-1の判定窓(0-1秒)後に記録されるべき\n\n');

% Show first 5 B errors
if ~isempty(B_errors)
    fprintf('B (Hit) Timing Errors:\n');
    fprintf('Trial | E time (s) | B time (s) | Diff (ms) | Status\n');
    fprintf('------+------------+------------+-----------+-------\n');
    for i = 1:min(5, size(B_errors,1))
        fprintf('%5d | %10.3f | %10.3f | %9.1f | ERROR: Same time!\n', ...
            B_errors(i,1), B_errors(i,2), B_errors(i,3), B_errors(i,4)*1000);
    end
    fprintf('\n');
end

% Show first 5 H errors
if ~isempty(H_errors)
    fprintf('H (Miss) Timing Errors:\n');
    fprintf('Trial | E time (s) | H time (s) | Diff (ms) | Status\n');
    fprintf('------+------------+------------+-----------+-------\n');
    for i = 1:min(5, size(H_errors,1))
        fprintf('%5d | %10.3f | %10.3f | %9.1f | ERROR: Same time!\n', ...
            H_errors(i,1), H_errors(i,2), H_errors(i,3), H_errors(i,4)*1000);
    end
    fprintf('\n');
end

%% 5. Expected timing analysis
fprintf('--- Expected Timing | 期待されるタイミング ---\n');
if strcmp(schedule_type, 'VI15')
    fprintf('Schedule: VI15 (Variable Interval 15s)\n');
    fprintf('Expected ITI: 11-21 seconds (mean ~15s)\n');
    fprintf('期待ITI: 11-21秒（平均約15秒）\n');
elseif strcmp(schedule_type, 'FI5')
    fprintf('Schedule: FI5 (Fixed Interval 5s)\n');
    fprintf('Expected ITI: ~6.02 seconds (fixed)\n');
    fprintf('期待ITI: 約6.02秒（固定）\n');
end

% Calculate actual ITIs
ITIs = diff(E_times);
fprintf('\nActual ITIs | 実際のITI:\n');
fprintf('Mean: %.2f s\n', mean(ITIs));
fprintf('Range: %.2f - %.2f s\n', min(ITIs), max(ITIs));

%% 6. Correct timing reconstruction
fprintf('\n--- Correct Timing Reconstruction | 正しいタイミング再構築 ---\n');
fprintf('Mapping B/H[n] to trial n-1 result:\n');
fprintf('B/H[n]を試行n-1の結果にマッピング:\n\n');

% Example reconstruction
fprintf('Example (DT1878):\n');
fprintf('Trial 1: E[1]=10.0s → [judgment 0-1s] → Result: Hit\n');
fprintf('Trial 2: E[2]=25.0s, B[1]=25.0s ← Recording of Trial 1 result\n');
fprintf('         (ITI = 15.0s, matches VI15 schedule)\n\n');

%% 7. Visualization of error
figure('Position', [100, 100, 1000, 600]);
hold on;

% Plot E events
plot(E_times, ones(size(E_times)), 'go', 'MarkerSize', 10, 'LineWidth', 2);

% Plot B/H events
plot(B_times, ones(size(B_times))*1.1, 'b^', 'MarkerSize', 8);
plot(H_times, ones(size(H_times))*0.9, 'rv', 'MarkerSize', 8);

% Highlight errors
for i = 1:size(B_errors,1)
    plot([B_errors(i,2), B_errors(i,3)], [1, 1.1], 'r-', 'LineWidth', 2);
    text(B_errors(i,2), 1.2, '⚠', 'FontSize', 14, 'Color', 'r', ...
        'HorizontalAlignment', 'center');
end

xlabel('Time (s) | 時間（秒）');
ylabel('Event Type');
title(sprintf('MED Timing Error Visualization | MEDタイミングエラー可視化\n%s (%s)', ...
    animal_id, schedule_type));
legend('E (Go cue)', 'B (Hit)', 'H (Miss)', 'Error', 'Location', 'best');
ylim([0.5, 1.5]);
grid on;

% Add error annotation
text(0.02, 0.98, sprintf('⚠ Error Rate: %.1f%%', ...
    (n_coincident_B + n_coincident_H)/(length(B_times) + length(H_times))*100), ...
    'Units', 'normalized', 'VerticalAlignment', 'top', ...
    'BackgroundColor', 'yellow', 'EdgeColor', 'red', 'LineWidth', 2, ...
    'FontSize', 12, 'FontWeight', 'bold');

end

%% Helper function to parse MEDx data
function [E_times, B_times, H_times, W_times] = parse_medx_data(filename)
    % Simplified parser - in real implementation, use proper MEDx parser
    % This is a placeholder showing the expected structure
    
    % Read file and extract events
    % ... (implementation details)
    
    % For demonstration:
    E_times = [10.0, 25.0, 41.0, 52.0, 73.0];  % Go cues
    B_times = [25.0, 52.0, 73.0];              % Hit markers (ERROR: same as next E)
    H_times = [41.0];                           % Miss markers (ERROR: same as next E)
    W_times = [11.0, 26.0, 53.0];              % Actual Hit detections (~1s after E)
end
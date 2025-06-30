%% Emergency B/H Event Timing Check Script
% Check actual timing relationships between E, B, and H events

clear all;
clc;

%% Load data
txt_file = 'D:\DN001_TF\2025_G00(DT1878,1899,1909)\Data_raw\20250629_DT1878_MEDx.txt';
ipt_data = readmatrix(txt_file);
endlength = length(ipt_data);

TF = ismissing(ipt_data);
ipt_data(:,3) = [];
ipt_data(:,1) = [];
T_s = cumsum(TF);
T_s(:,3) = [];
T_s(:,1) = [];

box = cat(2,ipt_data, T_s);
index_B = box(18,2);

%% Extract all event types
fprintf('=== Index Values ===\n');
fprintf('index_B = %d\n', index_B);
fprintf('index_B+3 (E event) = %d\n', index_B+3);
fprintf('index_B+6 (H event) = %d\n', index_B+6);
fprintf('index_B+13 (Hit cue) = %d\n', index_B+13);

%% Extract E events (Go cue)
E_events = [];
for i = 1:endlength
    if box(i,1) >= 0 && box(i,2) == index_B + 3
        E_events = [E_events; box(i,1)];
    end
end

%% Extract B events (Hit cue - actually at index_B+13)
B_events_13 = [];
for i = 1:endlength
    if box(i,1) >= 0 && box(i,2) == index_B + 13
        B_events_13 = [B_events_13; box(i,1)];
    end
end

%% Extract B events at index_B position
B_events_0 = [];
for i = 1:endlength
    if box(i,1) >= 0 && box(i,2) == index_B
        B_events_0 = [B_events_0; box(i,1)];
    end
end

%% Extract H events (Miss cue)
H_events = [];
for i = 1:endlength
    if box(i,1) >= 0 && box(i,2) == index_B + 6
        H_events = [H_events; box(i,1)];
    end
end

%% Display event counts
fprintf('\n=== Event Counts ===\n');
fprintf('E events (Go cue): %d\n', length(E_events));
fprintf('B events at index_B+13: %d\n', length(B_events_13));
fprintf('B events at index_B: %d\n', length(B_events_0));
fprintf('H events (Miss cue): %d\n', length(H_events));

%% Calculate time differences between E and B/H events
fprintf('\n=== Time Difference Analysis ===\n');

% For each E event, find closest B or H event
all_outcomes = sort([B_events_13; H_events]);
time_diffs = [];

for i = 1:length(E_events)
    e_time = E_events(i);
    
    % Find next outcome after this E
    next_outcomes = all_outcomes(all_outcomes > e_time);
    if ~isempty(next_outcomes)
        diff = next_outcomes(1) - e_time;
        time_diffs = [time_diffs; diff];
        
        if i <= 5  % Show first 5 examples
            fprintf('E at %.2f -> Next outcome at %.2f (diff = %.2f sec)\n', ...
                    e_time, next_outcomes(1), diff);
        end
    end
end

fprintf('\nTime difference statistics:\n');
fprintf('Mean: %.3f sec\n', mean(time_diffs));
fprintf('Std: %.3f sec\n', std(time_diffs));
fprintf('Min: %.3f sec\n', min(time_diffs));
fprintf('Max: %.3f sec\n', max(time_diffs));

%% List all B and H timestamps
fprintf('\n=== B Events (Hit cue at index_B+13) Timestamps ===\n');
for i = 1:min(10, length(B_events_13))  % Show first 10
    fprintf('B%d: %.3f sec\n', i, B_events_13(i));
end
if length(B_events_13) > 10
    fprintf('... (%d more)\n', length(B_events_13) - 10);
end

fprintf('\n=== H Events (Miss cue) Timestamps ===\n');
for i = 1:min(10, length(H_events))  % Show first 10
    fprintf('H%d: %.3f sec\n', i, H_events(i));
end
if length(H_events) > 10
    fprintf('... (%d more)\n', length(H_events) - 10);
end

%% Check for multiple B/H recordings at different offsets
fprintf('\n=== Checking Other Potential B/H Positions ===\n');
for offset = 0:15
    count = 0;
    for i = 1:endlength
        if box(i,1) >= 0 && box(i,2) == index_B + offset
            count = count + 1;
        end
    end
    if count > 0
        fprintf('index_B+%d: %d events\n', offset, count);
    end
end

%% Save detailed results
save('emergency_timing_analysis.mat');
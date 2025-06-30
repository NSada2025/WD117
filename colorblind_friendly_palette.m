%% Colorblind-friendly color palette for visualization
% Based on research for deuteranopia, protanopia, and tritanopia

function colors = get_colorblind_friendly_colors()
    % Paul Tol's colorblind-safe qualitative palette
    % Reference: https://personal.sron.nl/~pault/
    
    colors = struct();
    
    % Main event colors (optimized for all types of colorblindness)
    colors.go_cue = [0.2, 0.6, 0.2];      % Bluish-green (distinguishable)
    colors.hit = [0.1, 0.4, 0.8];         % Blue (safe for all types)
    colors.miss = [0.9, 0.6, 0];          % Orange (instead of red)
    colors.judgment_window = [0.95, 0.9, 0.25]; % Light yellow
    colors.lick = [0.35, 0.35, 0.35];    % Dark gray
    colors.first_lick = [0.5, 0, 0.5];   % Purple (distinguishable)
    colors.error = [0.8, 0.4, 0];         % Dark orange for errors
    
    % Additional colors for contrast
    colors.background = [0.98, 0.98, 0.98];
    colors.grid = [0.7, 0.7, 0.7];
    colors.text = [0.1, 0.1, 0.1];
    
    % Line styles for additional distinction
    colors.line_styles = {'-', '--', ':', '-.'};
    colors.line_widths = [3, 4, 3, 4];
    
    % Markers for different events
    colors.markers = {'o', 's', '^', 'v', 'd', 'p'};
    
    fprintf('Colorblind-friendly palette loaded.\n');
    fprintf('Optimized for: Deuteranopia, Protanopia, Tritanopia\n');
end

%% Test visualization function
function test_colorblind_palette()
    colors = get_colorblind_friendly_colors();
    
    figure('Position', [100, 100, 800, 600]);
    hold on;
    
    % Test each color
    y_pos = 1;
    fields = fieldnames(colors);
    
    for i = 1:length(fields)
        if ~strcmp(fields{i}, 'line_styles') && ...
           ~strcmp(fields{i}, 'line_widths') && ...
           ~strcmp(fields{i}, 'markers')
            
            color = colors.(fields{i});
            if length(color) == 3  % RGB color
                rectangle('Position', [1, y_pos, 2, 0.8], ...
                         'FaceColor', color, 'EdgeColor', 'k');
                text(3.5, y_pos+0.4, fields{i}, 'FontSize', 12);
                text(6, y_pos+0.4, sprintf('[%.2f, %.2f, %.2f]', ...
                     color(1), color(2), color(3)), 'FontSize', 10);
                y_pos = y_pos + 1;
            end
        end
    end
    
    xlim([0, 10]);
    ylim([0, y_pos]);
    title('Colorblind-Friendly Color Palette Test');
    xlabel('Color samples optimized for accessibility');
    
    % Add simulation note
    text(5, 0.5, 'Use colorblind simulation tools to verify', ...
         'HorizontalAlignment', 'center', 'FontStyle', 'italic');
end

%% Apply to visualization
function apply_colorblind_mode(figure_handle)
    % Apply colorblind-friendly colors to existing figure
    colors = get_colorblind_friendly_colors();
    
    % Find and update plot elements
    all_lines = findall(figure_handle, 'Type', 'Line');
    all_patches = findall(figure_handle, 'Type', 'Patch');
    
    % Update based on display names or colors
    for i = 1:length(all_lines)
        line_obj = all_lines(i);
        display_name = get(line_obj, 'DisplayName');
        
        if contains(display_name, 'Go cue', 'IgnoreCase', true)
            set(line_obj, 'Color', colors.go_cue);
        elseif contains(display_name, 'Hit', 'IgnoreCase', true)
            set(line_obj, 'Color', colors.hit);
        elseif contains(display_name, 'Miss', 'IgnoreCase', true)
            set(line_obj, 'Color', colors.miss);
        end
    end
    
    fprintf('Colorblind-friendly mode applied to figure.\n');
end
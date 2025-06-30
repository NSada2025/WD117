#!/usr/bin/env python3
"""
Behavior Judgment Plot Creation for DT1878
Creates comprehensive visualization of behavioral judgments with E-based timeline
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

def create_behavior_judgment_plot(filepath):
    """Create comprehensive behavior judgment plot"""
    
    print("=== Creating Behavior Judgment Plot ===")
    print(f"Data file: {filepath}\n")
    
    # Extract events
    events = extract_all_events_from_file(filepath)
    
    e_times = sorted(events['E_Go_cue'])
    b_times = sorted(events['B_reward'])
    w_times = sorted(events['W_Hit'])
    h_times = sorted(events['H_Miss'])
    n_times = sorted(events['N_1st_Lick'])
    c_times = sorted(events['C_Licks'])
    
    print(f"Events loaded:")
    print(f"  E (Go cue): {len(e_times)}")
    print(f"  W (Hit detection): {len(w_times)}")
    print(f"  B (Hit record): {len(b_times)}")
    print(f"  H (Miss record): {len(h_times)}")
    print(f"  N (1st Lick): {len(n_times)}")
    print(f"  C (All Licks): {len(c_times)}")
    
    # Analyze trials
    trials = analyze_trials_e_based(e_times, b_times, h_times, w_times, c_times, n_times)
    
    # Create the plot
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    fig.suptitle('DT1878 Behavior Judgment Analysis - E-based Timeline\n' +
                 'VI15 Schedule | 0s = Go cue | Corrected for MED-PC timing error', 
                 fontsize=16, fontweight='bold')
    
    # Define colors (high contrast)
    colors = {
        'go_cue': [0, 0.5, 0],         # Dark green
        'hit': [0, 0, 0.7],            # Dark blue
        'miss': [0.7, 0, 0],           # Dark red
        'lick': [0.3, 0.3, 0.3],       # Dark gray
        'first_lick': [0.8, 0, 0.8],   # Purple
        'window': [1, 1, 0],           # Yellow
        'correct': [0, 0.6, 0],        # Green
        'error': [1, 0, 0]             # Red
    }
    
    # Plot 1: Trial-by-trial raster plot
    create_raster_plot(axes[0], trials, colors)
    
    # Plot 2: Hit/Miss judgment summary
    create_judgment_summary(axes[1], trials, colors)
    
    # Plot 3: Lick behavior patterns
    create_lick_patterns(axes[2], trials, colors)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'/mnt/d/multiagent-system/dt1878_behavior_judgment_plot_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved as: {filename}")
    
    # Save data summary
    save_trial_summary(trials, timestamp)
    
    plt.show()
    return trials

def extract_all_events_from_file(filepath):
    """Extract all events from MEDx file"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find index_B
    char_positions = {}
    char_count = 0
    
    for line in lines:
        line = line.strip()
        if line and len(line) == 2 and line.endswith(':'):
            char = line[0]
            char_count += 1
            char_positions[char] = char_count
    
    index_B = char_positions['B']
    
    event_map = {
        'B_reward': index_B,
        'C_Licks': index_B + 1,
        'E_Go_cue': index_B + 3,
        'H_Miss': index_B + 6,
        'N_1st_Lick': index_B + 8,
        'W_Hit': index_B + 13,
    }
    
    events = {name: [] for name in event_map}
    current_cumsum = 0
    current_type = None
    
    for line in lines:
        line = line.strip()
        
        if line and len(line) == 2 and line.endswith(':'):
            current_cumsum += 1
            current_type = None
            for name, pos in event_map.items():
                if current_cumsum == pos:
                    current_type = name
                    break
            continue
        
        if current_type and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    timestamp = float(parts[1].strip())
                    events[current_type].append(timestamp)
                except:
                    pass
    
    return events

def analyze_trials_e_based(e_times, b_times, h_times, w_times, c_times, n_times):
    """Analyze trials with E-based timeline"""
    trials = []
    
    for i, e_time in enumerate(e_times):
        trial = {
            'number': i + 1,
            'e_time': e_time,
            'judgment': 'Unknown',
            'licks_in_window': [],
            'first_lick_time': None,
            'w_detection': None,
            'correct': None
        }
        
        # Find licks in 0-1s window
        window_start = e_time
        window_end = e_time + 1.0
        licks_in_window = [l for l in c_times if window_start <= l < window_end]
        trial['licks_in_window'] = licks_in_window
        
        # Find first lick in window
        first_lick = next((n for n in n_times if window_start <= n < window_end), None)
        if first_lick:
            trial['first_lick_time'] = first_lick - e_time
        
        # Find W detection for this trial
        w_for_trial = next((w for w in w_times if e_time < w < e_time + 2), None)
        if w_for_trial:
            trial['w_detection'] = w_for_trial - e_time
        
        # Determine judgment (from next trial recording)
        if i < len(e_times) - 1:  # Not the last trial
            next_e = e_times[i + 1]
            
            # Check what's recorded at next E
            has_b = any(abs(next_e - b) < 0.01 for b in b_times)
            has_h = any(abs(next_e - h) < 0.01 for h in h_times)
            
            if has_b:
                trial['judgment'] = 'Hit'
            elif has_h:
                trial['judgment'] = 'Miss'
        
        # Determine if judgment is correct
        has_lick = len(licks_in_window) > 0
        if trial['judgment'] != 'Unknown':
            if trial['judgment'] == 'Hit' and has_lick:
                trial['correct'] = True
            elif trial['judgment'] == 'Miss' and not has_lick:
                trial['correct'] = True
            else:
                trial['correct'] = False
        
        trials.append(trial)
    
    return trials

def create_raster_plot(ax, trials, colors):
    """Create raster plot of trials"""
    ax.set_title('Trial-by-Trial Raster Plot (E-based timeline)', fontsize=14, fontweight='bold')
    
    y_positions = []
    trial_numbers = []
    
    for i, trial in enumerate(trials):
        y_pos = len(trials) - i  # Reverse order (newest on top)
        y_positions.append(y_pos)
        trial_numbers.append(trial['number'])
        
        # Go cue at 0
        ax.plot([0, 0], [y_pos-0.3, y_pos+0.3], color=colors['go_cue'], linewidth=3)
        
        # Judgment window
        ax.fill_between([0, 1], y_pos-0.2, y_pos+0.2, 
                       color=colors['window'], alpha=0.3)
        
        # Licks in window
        for lick_time in trial['licks_in_window']:
            relative_time = lick_time - trial['e_time']
            ax.plot([relative_time, relative_time], [y_pos-0.15, y_pos+0.15], 
                   color=colors['lick'], linewidth=2)
        
        # First lick marker
        if trial['first_lick_time']:
            ax.plot([trial['first_lick_time'], trial['first_lick_time']], 
                   [y_pos-0.25, y_pos+0.25], 
                   color=colors['first_lick'], linewidth=3)
        
        # W detection
        if trial['w_detection']:
            ax.plot([trial['w_detection'], trial['w_detection']], 
                   [y_pos-0.3, y_pos+0.3], 
                   color=colors['hit'], linewidth=2, linestyle='--')
        
        # Judgment result (color code trial)
        if trial['judgment'] == 'Hit':
            ax.fill_between([-0.5, 2.5], y_pos-0.4, y_pos+0.4, 
                           color=colors['hit'], alpha=0.1)
        elif trial['judgment'] == 'Miss':
            ax.fill_between([-0.5, 2.5], y_pos-0.4, y_pos+0.4, 
                           color=colors['miss'], alpha=0.1)
        
        # Correctness indicator
        if trial['correct'] is not None:
            marker_color = colors['correct'] if trial['correct'] else colors['error']
            ax.plot([2.2], [y_pos], 'o', color=marker_color, markersize=6)
    
    ax.set_xlim([-0.5, 2.5])
    ax.set_ylim([0.5, len(trials) + 0.5])
    ax.set_xlabel('Time from Go cue (s)')
    ax.set_ylabel('Trial number (reversed)')
    ax.grid(True, alpha=0.3)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], color=colors['go_cue'], linewidth=3, label='Go cue'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors['window'], alpha=0.3, label='Judgment window'),
        plt.Line2D([0], [0], color=colors['lick'], linewidth=2, label='Licks'),
        plt.Line2D([0], [0], color=colors['first_lick'], linewidth=3, label='1st Lick'),
        plt.Line2D([0], [0], color=colors['hit'], linewidth=2, linestyle='--', label='W detection'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors['hit'], alpha=0.1, label='Hit trial'),
        plt.Rectangle((0, 0), 1, 1, facecolor=colors['miss'], alpha=0.1, label='Miss trial')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

def create_judgment_summary(ax, trials, colors):
    """Create judgment summary plot"""
    ax.set_title('Judgment Accuracy Summary', fontsize=14, fontweight='bold')
    
    # Count judgments
    hit_correct = sum(1 for t in trials if t['judgment'] == 'Hit' and t['correct'])
    hit_incorrect = sum(1 for t in trials if t['judgment'] == 'Hit' and not t['correct'])
    miss_correct = sum(1 for t in trials if t['judgment'] == 'Miss' and t['correct'])
    miss_incorrect = sum(1 for t in trials if t['judgment'] == 'Miss' and not t['correct'])
    unknown = sum(1 for t in trials if t['judgment'] == 'Unknown')
    
    # Create bar chart
    categories = ['Hit\n(Correct)', 'Hit\n(Incorrect)', 'Miss\n(Correct)', 'Miss\n(Incorrect)', 'Unknown']
    values = [hit_correct, hit_incorrect, miss_correct, miss_incorrect, unknown]
    bar_colors = [colors['correct'], colors['error'], colors['correct'], colors['error'], [0.5, 0.5, 0.5]]
    
    bars = ax.bar(categories, values, color=bar_colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        if value > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   str(value), ha='center', va='bottom', fontweight='bold')
    
    # Calculate accuracy
    total_judged = hit_correct + hit_incorrect + miss_correct + miss_incorrect
    if total_judged > 0:
        accuracy = (hit_correct + miss_correct) / total_judged * 100
        ax.text(0.5, 0.95, f'Overall Accuracy: {accuracy:.1f}%', 
               transform=ax.transAxes, ha='center', va='top', 
               fontsize=14, fontweight='bold', 
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    ax.set_ylabel('Number of trials')
    ax.set_ylim([0, max(values) * 1.2 if max(values) > 0 else 1])
    ax.grid(True, alpha=0.3, axis='y')

def create_lick_patterns(ax, trials, colors):
    """Create lick pattern analysis"""
    ax.set_title('Lick Behavior Patterns', fontsize=14, fontweight='bold')
    
    # Histogram of lick counts in judgment window
    hit_lick_counts = []
    miss_lick_counts = []
    
    for trial in trials:
        lick_count = len(trial['licks_in_window'])
        if trial['judgment'] == 'Hit':
            hit_lick_counts.append(lick_count)
        elif trial['judgment'] == 'Miss':
            miss_lick_counts.append(lick_count)
    
    # Create histogram
    bins = np.arange(0, max(max(hit_lick_counts, default=0), max(miss_lick_counts, default=0)) + 2) - 0.5
    
    ax.hist(hit_lick_counts, bins=bins, alpha=0.7, color=colors['hit'], 
           label=f'Hit trials (n={len(hit_lick_counts)})', edgecolor='black')
    ax.hist(miss_lick_counts, bins=bins, alpha=0.7, color=colors['miss'], 
           label=f'Miss trials (n={len(miss_lick_counts)})', edgecolor='black')
    
    ax.set_xlabel('Number of licks in 0-1s window')
    ax.set_ylabel('Number of trials')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add statistics
    if hit_lick_counts:
        hit_mean = np.mean(hit_lick_counts)
        ax.axvline(hit_mean, color=colors['hit'], linestyle='--', alpha=0.7, 
                  label=f'Hit mean: {hit_mean:.1f}')
    
    if miss_lick_counts:
        miss_mean = np.mean(miss_lick_counts)
        ax.axvline(miss_mean, color=colors['miss'], linestyle='--', alpha=0.7, 
                  label=f'Miss mean: {miss_mean:.1f}')

def save_trial_summary(trials, timestamp):
    """Save detailed trial summary"""
    filename = f'/mnt/d/multiagent-system/dt1878_behavior_summary_{timestamp}.txt'
    
    with open(filename, 'w') as f:
        f.write("DT1878 Behavior Judgment Analysis Summary\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total trials analyzed: {len(trials)}\n")
        
        hit_trials = [t for t in trials if t['judgment'] == 'Hit']
        miss_trials = [t for t in trials if t['judgment'] == 'Miss']
        
        f.write(f"Hit judgments: {len(hit_trials)}\n")
        f.write(f"Miss judgments: {len(miss_trials)}\n")
        
        correct_trials = [t for t in trials if t['correct']]
        f.write(f"Correct judgments: {len(correct_trials)}\n")
        
        if len(trials) > 0:
            accuracy = len(correct_trials) / len([t for t in trials if t['correct'] is not None]) * 100
            f.write(f"Accuracy: {accuracy:.1f}%\n\n")
        
        f.write("Trial Details:\n")
        f.write("-" * 30 + "\n")
        for trial in trials:
            f.write(f"Trial {trial['number']:2d}: {trial['judgment']:4s} | " +
                   f"Licks: {len(trial['licks_in_window']):2d} | " +
                   f"Correct: {trial['correct']}\n")
    
    print(f"Summary saved as: {filename}")

if __name__ == "__main__":
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    trials = create_behavior_judgment_plot(filepath)
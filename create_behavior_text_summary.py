#!/usr/bin/env python3
"""
Behavior Judgment Text Summary for DT1878
Creates text-based analysis when matplotlib is not available
"""

def create_behavior_text_summary(filepath):
    """Create comprehensive text-based behavior analysis"""
    
    print("=== DT1878 Behavior Judgment Text Summary ===")
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
    trials = analyze_trials_detailed(e_times, b_times, h_times, w_times, c_times, n_times)
    
    # Create text-based visualizations
    create_trial_raster_text(trials)
    create_judgment_summary_text(trials)
    create_lick_pattern_analysis(trials)
    
    # Save detailed report
    save_comprehensive_report(trials, filepath)
    
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

def analyze_trials_detailed(e_times, b_times, h_times, w_times, c_times, n_times):
    """Detailed trial analysis with E-based timeline"""
    trials = []
    
    for i, e_time in enumerate(e_times):
        trial = {
            'number': i + 1,
            'e_time': e_time,
            'judgment': 'Unknown',
            'licks_in_window': [],
            'first_lick_time': None,
            'w_detection': None,
            'correct': None,
            'iti': None
        }
        
        # Find licks in 0-1s window
        window_start = e_time
        window_end = e_time + 1.0
        licks_in_window = [l for l in c_times if window_start <= l < window_end]
        trial['licks_in_window'] = licks_in_window
        trial['lick_count'] = len(licks_in_window)
        
        # Find first lick in window
        first_lick = next((n for n in n_times if window_start <= n < window_end), None)
        if first_lick:
            trial['first_lick_time'] = first_lick - e_time
        
        # Find W detection for this trial
        w_for_trial = next((w for w in w_times if e_time < w < e_time + 2), None)
        if w_for_trial:
            trial['w_detection'] = w_for_trial - e_time
        
        # Calculate ITI
        if i < len(e_times) - 1:
            trial['iti'] = e_times[i + 1] - e_time
            next_e = e_times[i + 1]
            
            # Check what's recorded at next E
            has_b = any(abs(next_e - b) < 0.01 for b in b_times)
            has_h = any(abs(next_e - h) < 0.01 for h in h_times)
            
            if has_b:
                trial['judgment'] = 'Hit'
            elif has_h:
                trial['judgment'] = 'Miss'
        
        # Determine correctness
        has_lick = trial['lick_count'] > 0
        if trial['judgment'] != 'Unknown':
            if trial['judgment'] == 'Hit' and has_lick:
                trial['correct'] = True
            elif trial['judgment'] == 'Miss' and not has_lick:
                trial['correct'] = True
            else:
                trial['correct'] = False
        
        trials.append(trial)
    
    return trials

def create_trial_raster_text(trials):
    """Create text-based raster plot representation"""
    print("\n" + "="*80)
    print("TRIAL-BY-TRIAL RASTER (E-based timeline)")
    print("="*80)
    print("Legend: E=Go cue, |=Lick, F=1st Lick, W=Hit detection, []=Judgment window")
    print("Time:   0----1----2----3----4----5  (seconds from Go cue)")
    print("-"*80)
    
    for trial in trials[:20]:  # Show first 20 trials
        # Create timeline string
        timeline = [' '] * 50  # 50 characters for 5 seconds (10 chars per second)
        
        # Go cue at position 0
        timeline[0] = 'E'
        
        # Judgment window (0-1s)
        for pos in range(1, 10):
            timeline[pos] = '-'
        timeline[10] = ']'
        
        # Licks in window
        for lick_time in trial['licks_in_window']:
            relative_time = lick_time - trial['e_time']
            if 0 <= relative_time <= 1:
                pos = int(relative_time * 10) + 1
                if pos < len(timeline):
                    timeline[pos] = '|'
        
        # First lick
        if trial['first_lick_time']:
            pos = int(trial['first_lick_time'] * 10) + 1
            if pos < len(timeline):
                timeline[pos] = 'F'
        
        # W detection
        if trial['w_detection']:
            pos = int(trial['w_detection'] * 10)
            if pos < len(timeline):
                timeline[pos] = 'W'
        
        # Display
        timeline_str = ''.join(timeline)
        judgment_color = '✓' if trial['correct'] else '✗' if trial['correct'] is False else '?'
        
        print(f"T{trial['number']:2d}: {timeline_str[:30]} | {trial['judgment']:4s} {judgment_color} " +
              f"| Licks:{trial['lick_count']:2d}")
    
    if len(trials) > 20:
        print(f"... (showing first 20 of {len(trials)} trials)")

def create_judgment_summary_text(trials):
    """Create text-based judgment summary"""
    print("\n" + "="*60)
    print("JUDGMENT ACCURACY SUMMARY")
    print("="*60)
    
    # Count judgments
    hit_correct = sum(1 for t in trials if t['judgment'] == 'Hit' and t['correct'])
    hit_incorrect = sum(1 for t in trials if t['judgment'] == 'Hit' and not t['correct'])
    miss_correct = sum(1 for t in trials if t['judgment'] == 'Miss' and t['correct'])
    miss_incorrect = sum(1 for t in trials if t['judgment'] == 'Miss' and not t['correct'])
    unknown = sum(1 for t in trials if t['judgment'] == 'Unknown')
    
    total_judged = hit_correct + hit_incorrect + miss_correct + miss_incorrect
    
    print(f"Hit trials (correct):    {hit_correct:3d}")
    print(f"Hit trials (incorrect):  {hit_incorrect:3d}")
    print(f"Miss trials (correct):   {miss_correct:3d}")
    print(f"Miss trials (incorrect): {miss_incorrect:3d}")
    print(f"Unknown trials:          {unknown:3d}")
    print("-" * 30)
    print(f"Total judged:            {total_judged:3d}")
    
    if total_judged > 0:
        accuracy = (hit_correct + miss_correct) / total_judged * 100
        print(f"Overall accuracy:        {accuracy:5.1f}%")
        
        # Create simple bar chart with characters
        print("\nVisual representation:")
        print("Correct  : " + "█" * (hit_correct + miss_correct))
        print("Incorrect: " + "░" * (hit_incorrect + miss_incorrect))

def create_lick_pattern_analysis(trials):
    """Create lick pattern analysis"""
    print("\n" + "="*60)
    print("LICK BEHAVIOR PATTERNS")
    print("="*60)
    
    # Separate Hit and Miss trials
    hit_lick_counts = [t['lick_count'] for t in trials if t['judgment'] == 'Hit']
    miss_lick_counts = [t['lick_count'] for t in trials if t['judgment'] == 'Miss']
    
    print("Lick count distribution:")
    print("Licks | Hit trials | Miss trials")
    print("------|------------|------------")
    
    max_licks = max(max(hit_lick_counts, default=0), max(miss_lick_counts, default=0))
    
    for lick_count in range(max_licks + 1):
        hit_count = hit_lick_counts.count(lick_count)
        miss_count = miss_lick_counts.count(lick_count)
        
        hit_bar = "█" * hit_count
        miss_bar = "░" * miss_count
        
        print(f"  {lick_count:2d}  |     {hit_count:2d}     |     {miss_count:2d}")
        if hit_count > 0 or miss_count > 0:
            print(f"      | {hit_bar:<10} | {miss_bar:<10}")
    
    # Statistics
    if hit_lick_counts:
        hit_mean = sum(hit_lick_counts) / len(hit_lick_counts)
        print(f"\nHit trials - Mean licks: {hit_mean:.2f}")
    
    if miss_lick_counts:
        miss_mean = sum(miss_lick_counts) / len(miss_lick_counts)
        print(f"Miss trials - Mean licks: {miss_mean:.2f}")
    
    # ITI analysis
    itis = [t['iti'] for t in trials if t['iti'] is not None]
    if itis:
        print(f"\nInter-Trial Intervals (VI15 schedule):")
        print(f"Mean ITI: {sum(itis)/len(itis):.2f}s")
        print(f"Range: {min(itis):.2f} - {max(itis):.2f}s")

def save_comprehensive_report(trials, filepath):
    """Save comprehensive behavior report"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f'/mnt/d/multiagent-system/dt1878_behavior_comprehensive_report_{timestamp}.txt'
    
    with open(report_file, 'w') as f:
        f.write("DT1878 Comprehensive Behavior Judgment Report\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data source: {filepath}\n\n")
        
        # Summary statistics
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total trials: {len(trials)}\n")
        
        hit_trials = [t for t in trials if t['judgment'] == 'Hit']
        miss_trials = [t for t in trials if t['judgment'] == 'Miss']
        correct_trials = [t for t in trials if t['correct']]
        
        f.write(f"Hit judgments: {len(hit_trials)}\n")
        f.write(f"Miss judgments: {len(miss_trials)}\n")
        f.write(f"Correct judgments: {len(correct_trials)}\n")
        
        judged_trials = [t for t in trials if t['correct'] is not None]
        if judged_trials:
            accuracy = len(correct_trials) / len(judged_trials) * 100
            f.write(f"Accuracy: {accuracy:.1f}%\n\n")
        
        # Detailed trial data
        f.write("DETAILED TRIAL DATA\n")
        f.write("-" * 40 + "\n")
        f.write("Trial | E time   | Judgment | Licks | 1st Lick | W detect | ITI   | Correct\n")
        f.write("-" * 80 + "\n")
        
        for trial in trials:
            first_lick_str = f"{trial['first_lick_time']:.3f}" if trial['first_lick_time'] else "None "
            w_detect_str = f"{trial['w_detection']:.3f}" if trial['w_detection'] else "None "
            iti_str = f"{trial['iti']:.2f}" if trial['iti'] else "None "
            correct_str = "✓" if trial['correct'] else "✗" if trial['correct'] is False else "?"
            
            f.write(f"{trial['number']:5d} | {trial['e_time']:8.2f} | " +
                   f"{trial['judgment']:8s} | {trial['lick_count']:5d} | " +
                   f"{first_lick_str:9s} | {w_detect_str:8s} | " +
                   f"{iti_str:5s} | {correct_str:7s}\n")
        
        # Analysis notes
        f.write("\nANALYSIS NOTES\n")
        f.write("-" * 40 + "\n")
        f.write("- E-based timeline corrects for MED-PC timing error\n")
        f.write("- B/H judgments recorded at next trial start (confirmed bug)\n")
        f.write("- Judgment window: 0-1 seconds after Go cue\n")
        f.write("- VI15 schedule: Variable interval averaging 15 seconds\n")
        f.write("- All timing references use Go cue (E event) as time 0\n")
    
    print(f"\nComprehensive report saved: {report_file}")

if __name__ == "__main__":
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    trials = create_behavior_text_summary(filepath)
#!/usr/bin/env python3
"""
B/H Timing Variability Detailed Analysis
Investigate the true meaning of B/H events and timing distributions
"""

def analyze_bh_timing_details(filepath):
    """Detailed analysis of B/H timing variability"""
    
    print(f"=== B/H Timing Detailed Analysis ===\n")
    print(f"Reading {filepath}...")
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find character positions
    char_positions = {}
    char_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and len(line) == 2 and line.endswith(':'):
            char = line[0]
            char_count += 1
            char_positions[char] = (char_count, i)
    
    index_B = char_positions['B'][0]
    
    # Define all event types
    event_defs = {
        'B_reward': (index_B, 'B - Reward delivery?'),
        'C_Licks': (index_B + 1, 'C - All Licks'),
        'E_Go_cue': (index_B + 3, 'E - Go cue (CSp)'),
        'H_Miss': (index_B + 6, 'H - Miss/Trial end?'),
        'N_1st_Lick': (index_B + 8, 'N - First Lick'),
        'R_Licks_reward': (index_B + 11, 'R - Licks during reward'),
        'Hit_cue_W': (index_B + 13, 'W - Hit cue/outcome'),
    }
    
    # Extract all events
    events = {}
    for event_name, (pos, desc) in event_defs.items():
        events[event_name] = extract_events_at_position(lines, pos)
        print(f"{desc}: {len(events[event_name])} events")
    
    # Analyze E->B/H timing in detail
    e_times = sorted(events['E_Go_cue'])
    b_times = sorted(events['Hit_cue_W'])  # Using W (index_B+13)
    h_times = sorted(events['H_Miss'])
    
    print(f"\n=== Trial-by-trial E->B/H Timing ===")
    
    # Map each E to next B or H
    trial_data = []
    for i, e_time in enumerate(e_times):
        # Find next B
        next_b = None
        for b in b_times:
            if b > e_time:
                next_b = b
                break
        
        # Find next H
        next_h = None
        for h in h_times:
            if h > e_time:
                next_h = h
                break
        
        # Determine which comes first
        if next_b and next_h:
            if next_b < next_h:
                outcome = 'Hit'
                outcome_time = next_b
            else:
                outcome = 'Miss'
                outcome_time = next_h
        elif next_b:
            outcome = 'Hit'
            outcome_time = next_b
        elif next_h:
            outcome = 'Miss'
            outcome_time = next_h
        else:
            outcome = 'None'
            outcome_time = None
        
        if outcome_time:
            delay = outcome_time - e_time
            trial_data.append({
                'trial': i+1,
                'e_time': e_time,
                'outcome': outcome,
                'outcome_time': outcome_time,
                'delay': delay
            })
    
    # Print first 15 trials
    print("\nFirst 15 trials:")
    print("Trial | E (Go cue) | Outcome | Outcome Time | Delay")
    print("-" * 55)
    for td in trial_data[:15]:
        print(f"{td['trial']:5d} | {td['e_time']:10.2f} | {td['outcome']:7s} | "
              f"{td['outcome_time']:12.2f} | {td['delay']:6.2f}")
    
    # Analyze delay distribution
    delays = [td['delay'] for td in trial_data]
    
    print(f"\n=== E->B/H Delay Distribution ===")
    
    # Create histogram bins
    bins = [0, 1.5, 2.5, 5, 10, 15, 20, 25]
    hist = {f"{bins[i]}-{bins[i+1]}s": 0 for i in range(len(bins)-1)}
    
    for delay in delays:
        for i in range(len(bins)-1):
            if bins[i] <= delay < bins[i+1]:
                hist[f"{bins[i]}-{bins[i+1]}s"] += 1
                break
    
    print("\nDelay distribution:")
    for bin_range, count in hist.items():
        bar = '#' * count
        print(f"{bin_range:10s}: {count:3d} {bar}")
    
    # Check for 1-second clustering
    one_sec_count = sum(1 for d in delays if 0.9 <= d <= 1.1)
    print(f"\nDelays around 1 second (0.9-1.1s): {one_sec_count} ({one_sec_count/len(delays)*100:.1f}%)")
    
    # Analyze R events (Licks during reward)
    print(f"\n=== R Events Analysis ===")
    r_times = events['R_Licks_reward']
    print(f"Total R events: {len(r_times)}")
    
    # Check R events near B events
    r_near_b = 0
    for b_time in b_times:
        # Count R events within 2 seconds after B
        r_in_window = sum(1 for r in r_times if b_time <= r <= b_time + 2)
        if r_in_window > 0:
            r_near_b += 1
    
    print(f"B events with R events within 2 sec: {r_near_b}/{len(b_times)}")
    
    # Check trial structure
    print(f"\n=== Trial Structure Analysis ===")
    
    # Calculate inter-trial intervals (E to next E)
    iti_values = []
    for i in range(len(e_times)-1):
        iti = e_times[i+1] - e_times[i]
        iti_values.append(iti)
    
    if iti_values:
        print(f"Inter-trial intervals (E to next E):")
        print(f"  Mean: {sum(iti_values)/len(iti_values):.2f} sec")
        print(f"  Min: {min(iti_values):.2f} sec")
        print(f"  Max: {max(iti_values):.2f} sec")
    
    # Check if long delays correspond to ITI
    print(f"\n=== Long Delay Analysis ===")
    long_delays = [(i+1, d) for i, d in enumerate(delays) if d > 10]
    print(f"Trials with delays > 10 sec: {len(long_delays)}")
    for trial, delay in long_delays[:5]:
        print(f"  Trial {trial}: {delay:.2f} sec")
    
    return trial_data, events

def extract_events_at_position(lines, position):
    """Extract timestamps at a specific cumsum position"""
    events = []
    current_cumsum = 0
    in_target_section = False
    
    for line in lines:
        line = line.strip()
        
        if line and len(line) == 2 and line.endswith(':'):
            current_cumsum += 1
            in_target_section = (current_cumsum == position)
            continue
        
        if in_target_section and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    timestamp = float(parts[1].strip())
                    events.append(timestamp)
                except:
                    pass
        
        if in_target_section and line and not ':' in line:
            break
    
    return sorted(events)

if __name__ == "__main__":
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    trial_data, events = analyze_bh_timing_details(filepath)
    
    # Save detailed trial data
    with open('bh_timing_trial_data.txt', 'w') as f:
        f.write("=== Complete Trial-by-Trial Data ===\n\n")
        f.write("Trial | E (Go cue) | Outcome | Outcome Time | Delay\n")
        f.write("-" * 55 + "\n")
        for td in trial_data:
            f.write(f"{td['trial']:5d} | {td['e_time']:10.2f} | {td['outcome']:7s} | "
                    f"{td['outcome_time']:12.2f} | {td['delay']:6.2f}\n")
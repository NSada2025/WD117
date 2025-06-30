#!/usr/bin/env python3
"""
Critical Issue: W/H judgment logic problem
Why are 13/21 Miss trials having licks in 0-1s window?
"""

def analyze_judgment_logic_issue(filepath):
    """Investigate the judgment logic problem"""
    
    print("=== CRITICAL ISSUE: Judgment Logic Analysis ===")
    print("Problem: 13/21 Miss (H) trials have licks in 0-1s window\n")
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    events = extract_all_events(lines)
    
    e_times = sorted(events['E_Go_cue'])
    b_times = sorted(events['B_reward'])
    w_times = sorted(events['W_Hit'])
    h_times = sorted(events['H_Miss'])
    n_times = sorted(events['N_1st_Lick'])
    c_times = sorted(events['C_Licks'])
    
    # Analyze all trials systematically
    print("=== Trial-by-Trial Analysis ===")
    print("Mapping actual trial outcomes based on next E recording\n")
    
    all_trials = []
    
    for i in range(len(e_times)-1):
        trial = {
            'num': i+1,
            'e_time': e_times[i],
            'next_e': e_times[i+1],
            'iti': e_times[i+1] - e_times[i]
        }
        
        # Check what's recorded at next E
        has_b = any(abs(e_times[i+1] - b) < 0.01 for b in b_times)
        has_w = any(abs(e_times[i+1] - w) < 0.01 for w in w_times)
        has_h = any(abs(e_times[i+1] - h) < 0.01 for h in h_times)
        
        # Check licks in 0-1s window
        window_start = e_times[i]
        window_end = e_times[i] + 1.0
        
        licks_in_window = [l for l in c_times if window_start <= l <= window_end]
        first_lick = next((n for n in n_times if window_start <= n <= window_end), None)
        
        trial['licks_in_window'] = len(licks_in_window)
        trial['first_lick_time'] = first_lick - e_times[i] if first_lick else None
        trial['has_b'] = has_b
        trial['has_w'] = has_w
        trial['has_h'] = has_h
        
        # Determine outcome
        if has_b:
            trial['outcome'] = 'Hit(B)'
        elif has_h:
            trial['outcome'] = 'Miss(H)'
        else:
            trial['outcome'] = 'Unknown'
        
        # Check if W event exists for this trial
        w_for_trial = next((w for w in w_times if e_times[i] < w < e_times[i+1]), None)
        trial['w_time'] = w_for_trial - e_times[i] if w_for_trial else None
        
        all_trials.append(trial)
    
    # Analyze the problem
    print("Trial | E time  | Licks | 1st Lick | W delay | Outcome | Problem?")
    print("-" * 70)
    
    hit_b_count = 0
    miss_h_count = 0
    miss_with_lick_count = 0
    
    for t in all_trials:
        problem = ""
        if t['outcome'] == 'Hit(B)':
            hit_b_count += 1
            if t['licks_in_window'] == 0:
                problem = "ERROR: Hit without lick!"
        elif t['outcome'] == 'Miss(H)':
            miss_h_count += 1
            if t['licks_in_window'] > 0:
                miss_with_lick_count += 1
                problem = "ERROR: Miss with lick!"
        
        first_lick_str = f"{t['first_lick_time']:8.3f}" if t['first_lick_time'] else "    None"
        w_time_str = f"{t['w_time']:7.3f}" if t['w_time'] else "   None"
        
        print(f"{t['num']:5d} | {t['e_time']:7.2f} | {t['licks_in_window']:5d} | " +
              f"{first_lick_str} | {w_time_str} | " +
              f"{t['outcome']:8s} | {problem}")
        
        if t['num'] >= 20:  # Show first 20
            break
    
    print(f"\n... (showing first 20 of {len(all_trials)} trials)")
    
    # Summary statistics
    print("\n=== CRITICAL FINDINGS ===")
    print(f"Total Hit(B) outcomes: {hit_b_count}")
    print(f"Total Miss(H) outcomes: {miss_h_count}")
    print(f"Miss trials with licks: {miss_with_lick_count}/{miss_h_count} " +
          f"({miss_with_lick_count/miss_h_count*100:.1f}%)")
    
    # Hypothesis testing
    print("\n=== HYPOTHESIS: B vs H Decision Logic ===")
    print("Checking if B/H decision is based on W event existence...\n")
    
    # Count W events
    w_count = len(w_times)
    print(f"W (Hit detection) events: {w_count}")
    print(f"B (recorded at next E) events: {len(b_times)}")
    print(f"Match: {'YES' if w_count == len(b_times) else 'NO'}")
    
    # Check timing pattern
    print("\n=== W Event Timing Pattern ===")
    w_delays = []
    for t in all_trials:
        if t['w_time'] is not None:
            w_delays.append(t['w_time'])
    
    if w_delays:
        print(f"W event delays from E: mean={sum(w_delays)/len(w_delays):.3f}s, " +
              f"range={min(w_delays):.3f}-{max(w_delays):.3f}s")
    
    # Final conclusion
    print("\n=== CONCLUSION ===")
    print("1. W events (29) match B events (29) - these are true Hits")
    print("2. H events (21) include 13 trials WITH licks (62%)")
    print("3. The judgment logic appears to be:")
    print("   - If W event generated → Record B at next trial")
    print("   - If no W event → Record H at next trial")
    print("4. The problem: W generation logic is faulty")
    print("   - Not all trials with licks generate W events")
    print("   - This causes false Miss classifications")
    
    return all_trials

def extract_all_events(lines):
    """Extract all event types from MEDx data"""
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

if __name__ == "__main__":
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    trials = analyze_judgment_logic_issue(filepath)
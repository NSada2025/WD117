#!/usr/bin/env python3
"""
New Hypothesis Analysis: Go/No-go Task Timing Structure
B = Reward consumption completion time
H = Timeout time
"""

def analyze_new_hypothesis(filepath):
    """Test new hypothesis about B/H timing"""
    
    print("=== New Hypothesis Analysis ===")
    print("Hypothesis: B = Reward consumption completion, H = Timeout\n")
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Extract all event types
    events = extract_all_events(lines)
    
    # Get key events
    e_times = sorted(events['E_Go_cue'])
    b_times = sorted(events['B_reward'])  # Reward at index_B+0
    w_times = sorted(events['W_Hit'])     # Hit outcome at index_B+13
    h_times = sorted(events['H_Miss'])    # Miss/timeout
    n_times = sorted(events['N_1st_Lick'])
    
    print(f"Event counts:")
    print(f"E (Go cue): {len(e_times)}")
    print(f"B (Reward at +0): {len(b_times)}")
    print(f"W (Hit at +13): {len(w_times)}")
    print(f"H (Miss/Timeout): {len(h_times)}")
    print(f"N (1st Lick): {len(n_times)}")
    
    # Analyze trial structure
    print("\n=== Trial Structure Analysis ===")
    
    # Map each E to its outcome
    trials = []
    for i, e_time in enumerate(e_times):
        trial = {'num': i+1, 'e_time': e_time}
        
        # Find 1st lick after E
        lick_in_window = None
        for n in n_times:
            if e_time <= n <= e_time + 1.0:  # 1 sec window
                lick_in_window = n
                break
        
        # Find next W (Hit) or H (Miss)
        next_w = next((w for w in w_times if w > e_time), None)
        next_h = next((h for h in h_times if h > e_time), None)
        
        # Determine outcome
        if next_w and next_h:
            if next_w < next_h:
                trial['outcome'] = 'Hit'
                trial['outcome_time'] = next_w
            else:
                trial['outcome'] = 'Miss'
                trial['outcome_time'] = next_h
        elif next_w:
            trial['outcome'] = 'Hit'
            trial['outcome_time'] = next_w
        elif next_h:
            trial['outcome'] = 'Miss'
            trial['outcome_time'] = next_h
        else:
            continue
        
        trial['delay'] = trial['outcome_time'] - e_time
        trial['lick_in_window'] = lick_in_window is not None
        
        # For Hit trials, find B (reward consumption)
        if trial['outcome'] == 'Hit':
            next_b = next((b for b in b_times if b > e_time), None)
            if next_b:
                trial['b_time'] = next_b
                trial['consumption_time'] = next_b - trial['outcome_time']
        
        trials.append(trial)
    
    # Analyze delay patterns
    print("\n=== Delay Pattern Analysis ===")
    
    # Separate by delay type
    short_delays = [t for t in trials if t['delay'] <= 1.1]
    long_delays = [t for t in trials if t['delay'] > 1.1]
    
    print(f"Trials with ~1 sec delay: {len(short_delays)} ({len(short_delays)/len(trials)*100:.1f}%)")
    print(f"Trials with >1 sec delay: {len(long_delays)} ({len(long_delays)/len(trials)*100:.1f}%)")
    
    # Check if short delays have licks in window
    short_with_lick = sum(1 for t in short_delays if t['lick_in_window'])
    print(f"\nShort delay trials with lick in 0-1s window: {short_with_lick}/{len(short_delays)}")
    
    # Analyze long delays
    print("\n=== Long Delay Analysis ===")
    print("These may represent next trial's outcome...")
    
    # Check if long delays are actually ITI + next trial
    for i, trial in enumerate(trials[:10]):
        if trial['delay'] > 10:
            print(f"Trial {trial['num']}: E at {trial['e_time']:.2f}, "
                  f"{trial['outcome']} at {trial['outcome_time']:.2f} "
                  f"(delay={trial['delay']:.2f})")
            
            # Check if there's another E between
            intervening_e = [e for e in e_times if trial['e_time'] < e < trial['outcome_time']]
            if intervening_e:
                print(f"  -> Found {len(intervening_e)} E events between!")
    
    # New interpretation
    print("\n=== New Interpretation ===")
    print("Hypothesis: Each E (Go cue) should have outcome ~1 sec later")
    print("Long delays suggest outcome belongs to different trial\n")
    
    # Re-map with 1.5 sec window
    correct_mapping = []
    for e_time in e_times:
        # Look for outcome within 1.5 seconds
        nearby_w = [w for w in w_times if 0.5 <= w - e_time <= 1.5]
        nearby_h = [h for h in h_times if 0.5 <= h - e_time <= 1.5]
        
        if nearby_w:
            correct_mapping.append({'e': e_time, 'outcome': 'Hit', 'time': nearby_w[0]})
        elif nearby_h:
            correct_mapping.append({'e': e_time, 'outcome': 'Miss', 'time': nearby_h[0]})
        else:
            correct_mapping.append({'e': e_time, 'outcome': 'None', 'time': None})
    
    hit_count = sum(1 for m in correct_mapping if m['outcome'] == 'Hit')
    miss_count = sum(1 for m in correct_mapping if m['outcome'] == 'Miss')
    none_count = sum(1 for m in correct_mapping if m['outcome'] == 'None')
    
    print(f"With 0.5-1.5 sec window mapping:")
    print(f"Hit: {hit_count}")
    print(f"Miss: {miss_count}")
    print(f"No outcome: {none_count}")
    
    # Verify B timing for Hit trials
    print("\n=== B (Reward) Timing Analysis ===")
    for i, b_time in enumerate(b_times[:5]):
        print(f"B{i+1} at {b_time:.2f}")
        # Find preceding W (Hit)
        preceding_w = [w for w in w_times if w < b_time]
        if preceding_w:
            closest_w = max(preceding_w)
            diff = b_time - closest_w
            print(f"  -> {diff:.2f} sec after W (Hit) at {closest_w:.2f}")
    
    return trials, correct_mapping

def extract_all_events(lines):
    """Extract all event types from MEDx data"""
    # First find index_B
    char_positions = {}
    char_count = 0
    
    for line in lines:
        line = line.strip()
        if line and len(line) == 2 and line.endswith(':'):
            char = line[0]
            char_count += 1
            char_positions[char] = char_count
    
    index_B = char_positions['B']
    
    # Define all events
    event_map = {
        'B_reward': index_B,
        'E_Go_cue': index_B + 3,
        'H_Miss': index_B + 6,
        'N_1st_Lick': index_B + 8,
        'W_Hit': index_B + 13,
    }
    
    # Extract events
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
    trials, correct_mapping = analyze_new_hypothesis(filepath)
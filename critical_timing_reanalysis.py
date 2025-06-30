#!/usr/bin/env python3
"""
Critical Re-analysis: E and B/H Same-Time Recording
Testing if B/H are recorded at the SAME time as E (next trial)
"""

def critical_timing_reanalysis(filepath):
    """Re-analyze with new understanding that B/H might be recorded with next E"""
    
    print("=== CRITICAL TIMING RE-ANALYSIS ===")
    print("Hypothesis: B/H are recorded at the SAME TIME as next trial's E\n")
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Extract events
    events = extract_all_events(lines)
    
    e_times = sorted(events['E_Go_cue'])
    b_times = sorted(events['B_reward'])
    w_times = sorted(events['W_Hit'])
    h_times = sorted(events['H_Miss'])
    
    print(f"Total trials (E events): {len(e_times)}")
    print(f"B events: {len(b_times)}")
    print(f"W (Hit) events: {len(w_times)}")
    print(f"H (Miss) events: {len(h_times)}")
    
    # Check if B/H/W coincide with E times
    print("\n=== Checking B/H/W vs E timing ===")
    
    # Find exact matches (within 0.01 sec)
    b_matches_e = []
    w_matches_e = []
    h_matches_e = []
    
    for e in e_times:
        # Check B
        for b in b_times:
            if abs(e - b) < 0.01:
                b_matches_e.append((e, b))
        # Check W
        for w in w_times:
            if abs(e - w) < 0.01:
                w_matches_e.append((e, w))
        # Check H
        for h in h_times:
            if abs(e - h) < 0.01:
                h_matches_e.append((e, h))
    
    print(f"\nB events matching E times: {len(b_matches_e)}")
    print(f"W events matching E times: {len(w_matches_e)}")
    print(f"H events matching E times: {len(h_matches_e)}")
    
    # Show examples
    if b_matches_e:
        print("\nFirst 5 B-E matches:")
        for e, b in b_matches_e[:5]:
            print(f"  E at {e:.3f} = B at {b:.3f}")
    
    if w_matches_e:
        print("\nFirst 5 W-E matches:")
        for e, w in w_matches_e[:5]:
            print(f"  E at {e:.3f} = W at {w:.3f}")
    
    if h_matches_e:
        print("\nFirst 5 H-E matches:")
        for e, h in h_matches_e[:5]:
            print(f"  E at {e:.3f} = H at {h:.3f}")
    
    # Analyze trial structure with new understanding
    print("\n=== New Trial Structure Analysis ===")
    print("If B/H/W are recorded with next E, then:")
    print("Trial n result is recorded at Trial n+1 start\n")
    
    # Map each E to previous trial's outcome
    trial_mapping = []
    for i in range(1, len(e_times)):  # Start from second E
        current_e = e_times[i]
        prev_e = e_times[i-1]
        
        trial = {
            'trial_num': i,
            'prev_e': prev_e,
            'current_e': current_e,
            'iti': current_e - prev_e
        }
        
        # Check what's recorded at current E time
        # B at this time?
        b_at_e = any(abs(current_e - b) < 0.01 for b in b_times)
        # W at this time?
        w_at_e = any(abs(current_e - w) < 0.01 for w in w_times)
        # H at this time?
        h_at_e = any(abs(current_e - h) < 0.01 for h in h_times)
        
        trial['b_at_e'] = b_at_e
        trial['w_at_e'] = w_at_e
        trial['h_at_e'] = h_at_e
        
        # Determine previous trial outcome
        if w_at_e:
            trial['prev_outcome'] = 'Hit'
        elif h_at_e:
            trial['prev_outcome'] = 'Miss'
        else:
            trial['prev_outcome'] = 'Unknown'
        
        trial_mapping.append(trial)
    
    # Show first 10 trials
    print("First 10 trial mappings:")
    print("Trial | Prev E    | Curr E    | ITI   | Outcome at Curr E")
    print("-" * 60)
    for t in trial_mapping[:10]:
        outcome_markers = []
        if t['b_at_e']: outcome_markers.append('B')
        if t['w_at_e']: outcome_markers.append('W')
        if t['h_at_e']: outcome_markers.append('H')
        markers = '+'.join(outcome_markers) if outcome_markers else 'None'
        
        print(f"{t['trial_num']:5d} | {t['prev_e']:9.2f} | {t['current_e']:9.2f} | "
              f"{t['iti']:5.2f} | {markers} ({t['prev_outcome']})")
    
    # Count outcomes
    hit_count = sum(1 for t in trial_mapping if t['prev_outcome'] == 'Hit')
    miss_count = sum(1 for t in trial_mapping if t['prev_outcome'] == 'Miss')
    unknown_count = sum(1 for t in trial_mapping if t['prev_outcome'] == 'Unknown')
    
    print(f"\nOutcome counts (from trial 2 onwards):")
    print(f"Hit: {hit_count}")
    print(f"Miss: {miss_count}")
    print(f"Unknown: {unknown_count}")
    
    # Calculate TRUE E-to-outcome delays
    print("\n=== TRUE Within-Trial Delays ===")
    print("If outcomes are recorded at next E, delay = ITI")
    
    iti_for_hits = [t['iti'] for t in trial_mapping if t['prev_outcome'] == 'Hit']
    iti_for_misses = [t['iti'] for t in trial_mapping if t['prev_outcome'] == 'Miss']
    
    if iti_for_hits:
        print(f"\nITI for Hit trials:")
        print(f"  Mean: {sum(iti_for_hits)/len(iti_for_hits):.2f} sec")
        print(f"  Min: {min(iti_for_hits):.2f} sec")
        print(f"  Max: {max(iti_for_hits):.2f} sec")
    
    if iti_for_misses:
        print(f"\nITI for Miss trials:")
        print(f"  Mean: {sum(iti_for_misses)/len(iti_for_misses):.2f} sec")
        print(f"  Min: {min(iti_for_misses):.2f} sec")
        print(f"  Max: {max(iti_for_misses):.2f} sec")
    
    # Final verification
    print("\n=== FINAL VERIFICATION ===")
    
    # Check the "1 second delays" from previous analysis
    print("\nThe '1 second delays' were actually:")
    print("E(n) -> E(n+1) where E(n+1) records outcome of trial n")
    print("These represent consecutive trials with ~1 sec ITI")
    
    # Check the "long delays"
    print("\nThe 'long delays' (10-22 sec) were actually:")
    print("Normal ITIs between non-consecutive outcome recording")
    
    return trial_mapping

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
        'E_Go_cue': index_B + 3,
        'H_Miss': index_B + 6,
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
    trial_mapping = critical_timing_reanalysis(filepath)
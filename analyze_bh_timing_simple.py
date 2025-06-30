#!/usr/bin/env python3
"""
Emergency B/H Event Timing Analysis (Simple version)
"""

def analyze_medx_timing(filepath):
    """Analyze timing relationships in MEDx data"""
    
    print(f"Reading {filepath}...")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # First, find where character labels are
    char_positions = {}
    char_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and len(line) == 2 and line.endswith(':'):
            char = line[0]
            char_count += 1
            char_positions[char] = (char_count, i)
            print(f"Found '{char}' at cumsum position {char_count} (line {i})")
    
    # Get index_B
    if 'B' not in char_positions:
        print("ERROR: B not found")
        return
    
    index_B = char_positions['B'][0]
    print(f"\nindex_B = {index_B}")
    
    # Define event positions
    event_defs = {
        'B_at_0': index_B,
        'C_Licks': index_B + 1,
        'E_Go_cue': index_B + 3,
        'H_Miss': index_B + 6,
        'N_1st_Lick': index_B + 8,
        'Hit_cue_13': index_B + 13,
    }
    
    print("\n=== Event Definitions ===")
    for name, pos in event_defs.items():
        print(f"{name}: index_B+{pos-index_B} = {pos}")
    
    # Extract events
    events = {name: [] for name in event_defs}
    
    # Parse data with cumsum tracking
    current_cumsum = 0
    in_data_section = False
    current_event_type = None
    
    for line in lines:
        line = line.strip()
        
        # Check for character marker
        if line and len(line) == 2 and line.endswith(':'):
            current_cumsum += 1
            in_data_section = True
            
            # Check which event type this is
            current_event_type = None
            for event_name, event_pos in event_defs.items():
                if current_cumsum == event_pos:
                    current_event_type = event_name
                    break
            continue
        
        # Parse data lines
        if in_data_section and current_event_type and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    idx = int(parts[0].strip())
                    timestamp = float(parts[1].strip())
                    events[current_event_type].append(timestamp)
                except:
                    pass
        
        # Check for end of section
        if in_data_section and line and not ':' in line:
            in_data_section = False
            current_event_type = None
    
    # Display counts
    print("\n=== Event Counts ===")
    for event_name, timestamps in events.items():
        if timestamps:
            print(f"{event_name}: {len(timestamps)} events")
    
    # Analyze E->B/H timing
    e_times = sorted(events['E_Go_cue'])
    b_times = sorted(events['Hit_cue_13'])
    h_times = sorted(events['H_Miss'])
    
    print(f"\nE events (Go cue): {len(e_times)}")
    print(f"B events (Hit at +13): {len(b_times)}")
    print(f"H events (Miss): {len(h_times)}")
    
    # Calculate time differences
    all_outcomes = sorted(b_times + h_times)
    time_diffs = []
    
    print("\n=== E to B/H Time Differences ===")
    for i, e_time in enumerate(e_times):
        # Find next outcome
        next_outcome = None
        for outcome_time in all_outcomes:
            if outcome_time > e_time:
                next_outcome = outcome_time
                break
        
        if next_outcome:
            diff = next_outcome - e_time
            time_diffs.append(diff)
            
            if i < 5:  # Show first 5
                outcome_type = 'B' if next_outcome in b_times else 'H'
                print(f"E at {e_time:.2f} -> {outcome_type} at {next_outcome:.2f} (diff = {diff:.2f} sec)")
    
    if time_diffs:
        print(f"\nTime difference statistics:")
        print(f"  Mean: {sum(time_diffs)/len(time_diffs):.3f} sec")
        print(f"  Min: {min(time_diffs):.3f} sec")
        print(f"  Max: {max(time_diffs):.3f} sec")
        
        # Count unique values
        unique_diffs = {}
        for d in time_diffs:
            rounded = round(d, 2)
            unique_diffs[rounded] = unique_diffs.get(rounded, 0) + 1
        
        print(f"  Unique values: {sorted(unique_diffs.keys())}")
    
    # List timestamps
    print("\n=== B Event Timestamps (first 10) ===")
    for i, t in enumerate(b_times[:10]):
        print(f"B{i+1}: {t:.3f} sec")
    
    print("\n=== H Event Timestamps (first 10) ===")
    for i, t in enumerate(h_times[:10]):
        print(f"H{i+1}: {t:.3f} sec")
    
    return events

if __name__ == "__main__":
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    results = analyze_medx_timing(filepath)
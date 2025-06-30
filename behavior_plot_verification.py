#!/usr/bin/env python3
"""
Behavior Plot Verification
Cross-check with previous analysis to identify discrepancy
"""

def verify_behavior_analysis():
    """Verify the behavior analysis results"""
    
    print("=== Behavior Analysis Verification ===")
    print("Comparing current results with previous analysis\n")
    
    # Read the previous analysis file
    try:
        with open('/mnt/d/multiagent-system/dt1878_trial_analysis.csv', 'r') as f:
            lines = f.readlines()
        
        print("Previous analysis (CSV) results:")
        header = lines[0].strip().split(',')
        print(f"Header: {header}")
        
        correct_count = 0
        total_count = 0
        
        for line in lines[1:]:  # Skip header
            if line.strip():
                fields = line.strip().split(',')
                if len(fields) >= 6:
                    correct = fields[5]  # 'correct' field
                    if correct == 'True':
                        correct_count += 1
                    elif correct == 'False':
                        pass  # Count as incorrect
                    else:
                        continue  # Skip if not judged
                    total_count += 1
        
        if total_count > 0:
            prev_accuracy = correct_count / total_count * 100
            print(f"Previous accuracy: {prev_accuracy:.1f}% ({correct_count}/{total_count})")
        
    except FileNotFoundError:
        print("Previous CSV analysis not found")
    
    # Current analysis summary
    print("\nCurrent text-based analysis:")
    print("Accuracy: 46.9% (23/49)")
    
    print("\n=== Discrepancy Analysis ===")
    print("The discrepancy suggests different trial mapping methods:")
    print("1. Previous analysis: Direct E-B/H mapping by trial order")
    print("2. Current analysis: E-based with next-trial recording correction")
    
    print("\n=== Manual Verification ===")
    print("Let's check a few specific trials manually...")
    
    # Load raw data for manual check
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    events = extract_events_simple(filepath)
    
    e_times = sorted(events['E'])
    b_times = sorted(events['B'])
    h_times = sorted(events['H'])
    c_times = sorted(events['C'])
    
    print(f"\nRaw event counts:")
    print(f"E: {len(e_times)}, B: {len(b_times)}, H: {len(h_times)}, C: {len(c_times)}")
    
    # Check first few trials manually
    print("\nManual trial check (first 10 trials):")
    print("Trial | E time   | Next E   | B/H at next E | Licks 0-1s | Expected | Actual")
    print("-" * 80)
    
    for i in range(min(10, len(e_times)-1)):
        e_time = e_times[i]
        next_e = e_times[i+1]
        
        # Check licks in 0-1s window
        licks_in_window = sum(1 for c in c_times if e_time <= c < e_time + 1.0)
        expected = "Hit" if licks_in_window > 0 else "Miss"
        
        # Check what's recorded at next E
        has_b = any(abs(next_e - b) < 0.01 for b in b_times)
        has_h = any(abs(next_e - h) < 0.01 for h in h_times)
        
        if has_b:
            actual = "Hit"
        elif has_h:
            actual = "Miss"
        else:
            actual = "None"
        
        match = "✓" if expected == actual else "✗"
        
        print(f"{i+1:5d} | {e_time:8.2f} | {next_e:8.2f} | {actual:13s} | " +
              f"{licks_in_window:10d} | {expected:8s} | {actual:6s} {match}")
    
    return True

def extract_events_simple(filepath):
    """Simple event extraction"""
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
        'B': index_B,
        'C': index_B + 1,
        'E': index_B + 3,
        'H': index_B + 6,
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
    verify_behavior_analysis()
#!/usr/bin/env python3
"""
Emergency B/H Event Timing Analysis
Check actual timing relationships between E, B, and H events
"""

import numpy as np
import pandas as pd
from collections import defaultdict

def analyze_medx_timing(filepath):
    """Analyze timing relationships in MEDx data"""
    
    # Read the data
    print(f"Reading {filepath}...")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Parse data
    data_lines = []
    header_end = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip header
        if not header_end and line.startswith('0:'):
            header_end = True
        
        if header_end and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    idx = int(parts[0].strip())
                    value = float(parts[1].strip())
                    data_lines.append((idx, value))
                except:
                    pass
    
    # Identify character positions
    char_positions = {}
    current_char = None
    char_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and len(line) == 2 and line.endswith(':'):
            current_char = line[0]
            char_count += 1
            char_positions[current_char] = char_count
            print(f"Found character '{current_char}' at position {char_count}")
    
    # Get index_B
    if 'B' in char_positions:
        index_B = char_positions['B']
        print(f"\nindex_B = {index_B}")
    else:
        print("ERROR: B not found in data")
        return
    
    # Extract events by type
    events = defaultdict(list)
    event_map = {
        'B': index_B,
        'E': index_B + 3,
        'H': index_B + 6,
        'Hit_cue': index_B + 13,
        'C': index_B + 1,
        'N': index_B + 8,
    }
    
    # Build cumulative sum for character detection
    cumsum_idx = 0
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Check for section markers
        if line and len(line) == 2 and line.endswith(':'):
            cumsum_idx += 1
            current_section = cumsum_idx
            continue
        
        # Parse data lines
        if current_section and ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    timestamp = float(parts[1].strip())
                    
                    # Check which event type this belongs to
                    for event_name, event_idx in event_map.items():
                        if current_section == event_idx:
                            events[event_name].append(timestamp)
                except:
                    pass
    
    # Display results
    print("\n=== Event Counts ===")
    for event_name, timestamps in events.items():
        print(f"{event_name}: {len(timestamps)} events")
    
    # Analyze E-B and E-H timing
    print("\n=== E-B/H Timing Analysis ===")
    e_events = sorted(events.get('E', []))
    b_events = sorted(events.get('Hit_cue', []))
    h_events = sorted(events.get('H', []))
    
    all_outcomes = sorted(b_events + h_events)
    
    time_diffs = []
    for e_time in e_events:
        # Find next outcome
        next_outcomes = [t for t in all_outcomes if t > e_time]
        if next_outcomes:
            diff = next_outcomes[0] - e_time
            time_diffs.append(diff)
    
    if time_diffs:
        print(f"Time differences between E and next B/H:")
        print(f"  Mean: {np.mean(time_diffs):.3f} sec")
        print(f"  Std: {np.std(time_diffs):.3f} sec")
        print(f"  Min: {np.min(time_diffs):.3f} sec")
        print(f"  Max: {np.max(time_diffs):.3f} sec")
        print(f"  Unique values: {sorted(set(np.round(time_diffs, 2)))}")
    
    # Show first few timestamps
    print("\n=== Sample Timestamps ===")
    
    if e_events:
        print(f"\nFirst 5 E events (Go cue):")
        for i, t in enumerate(e_events[:5]):
            print(f"  E{i+1}: {t:.3f} sec")
    
    if b_events:
        print(f"\nFirst 5 B events (Hit cue at +13):")
        for i, t in enumerate(b_events[:5]):
            print(f"  B{i+1}: {t:.3f} sec")
    
    if h_events:
        print(f"\nFirst 5 H events (Miss cue):")
        for i, t in enumerate(h_events[:5]):
            print(f"  H{i+1}: {t:.3f} sec")
    
    # Check all offsets
    print("\n=== All Event Types Found ===")
    all_offsets = defaultdict(int)
    
    cumsum_idx = 0
    for line in lines:
        line = line.strip()
        if line and len(line) == 2 and line.endswith(':'):
            cumsum_idx += 1
            continue
        
        if ':' in line and cumsum_idx > 0:
            parts = line.split(':')
            if len(parts) == 2:
                try:
                    _ = float(parts[1].strip())
                    all_offsets[cumsum_idx] += 1
                except:
                    pass
    
    for idx in sorted(all_offsets.keys()):
        if all_offsets[idx] > 0:
            offset = idx - index_B
            print(f"  index_B+{offset}: {all_offsets[idx]} events")
    
    # Return results
    return {
        'events': dict(events),
        'time_diffs': time_diffs,
        'index_B': index_B
    }

if __name__ == "__main__":
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    results = analyze_medx_timing(filepath)
    
    # Save detailed timestamps
    if results:
        with open('bh_timing_analysis.txt', 'w') as f:
            f.write("=== Detailed B/H Event Timestamps ===\n\n")
            
            if 'Hit_cue' in results['events']:
                f.write("B Events (Hit cue at index_B+13):\n")
                for i, t in enumerate(results['events']['Hit_cue']):
                    f.write(f"B{i+1}: {t:.3f} sec\n")
            
            f.write("\n")
            
            if 'H' in results['events']:
                f.write("H Events (Miss cue at index_B+6):\n")
                for i, t in enumerate(results['events']['H']):
                    f.write(f"H{i+1}: {t:.3f} sec\n")
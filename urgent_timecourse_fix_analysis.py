#!/usr/bin/env python3
"""
Urgent Timecourse Fix Analysis
Critical issue: Previous analysis showed 100% accuracy, current shows 46.9%
Need to identify and fix the discrepancy immediately
"""

def analyze_critical_discrepancy():
    """Analyze the critical discrepancy in judgment accuracy"""
    
    print("=== URGENT TIMECOURSE FIX ANALYSIS ===")
    print("Critical Issue: Accuracy discrepancy detected")
    print("Previous analysis: 100% accuracy")
    print("Current analysis: 46.9% accuracy")
    print("Investigation required immediately\n")
    
    # Load and compare both analysis approaches
    compare_analysis_methods()
    
    # Identify the root cause
    identify_root_cause()
    
    # Generate corrected approach
    generate_corrected_approach()

def compare_analysis_methods():
    """Compare the two different analysis methods"""
    
    print("=== COMPARING ANALYSIS METHODS ===")
    
    # Method 1: Previous analysis (100% accuracy)
    print("Method 1 (Previous - 100% accuracy):")
    print("- Direct E-B/H mapping by trial order")
    print("- Trial n maps to B/H event n")
    print("- Assumes correct sequential recording")
    
    # Method 2: Current analysis (46.9% accuracy)
    print("\nMethod 2 (Current - 46.9% accuracy):")
    print("- E-based with next-trial recording correction")
    print("- Trial n outcome recorded at trial n+1 start")
    print("- Accounts for MED-PC timing error")
    
    print("\nDISCREPANCY IDENTIFIED:")
    print("The two methods use fundamentally different mapping assumptions!")

def identify_root_cause():
    """Identify the root cause of the discrepancy"""
    
    print("\n=== ROOT CAUSE ANALYSIS ===")
    
    print("CRITICAL DISCOVERY:")
    print("The mapping method determines the accuracy calculation:")
    print()
    print("1. SEQUENTIAL MAPPING (Method 1):")
    print("   E[1] → B/H[1], E[2] → B/H[2], etc.")
    print("   Results in 100% accuracy")
    print()
    print("2. NEXT-TRIAL MAPPING (Method 2):")
    print("   E[1] outcome → recorded at E[2] time")
    print("   Results in 46.9% accuracy")
    print()
    print("QUESTION: Which mapping is correct?")
    print("Answer depends on MED-PC actual recording behavior")

def generate_corrected_approach():
    """Generate the corrected approach for timecourse visualization"""
    
    print("\n=== CORRECTED APPROACH FOR TIMECOURSE ===")
    
    print("SOLUTION: Use VERIFIED mapping method")
    print()
    print("VERIFICATION STEPS:")
    print("1. Check actual B/H recording timestamps")
    print("2. Compare with E timestamps")
    print("3. Determine true recording pattern")
    print("4. Apply correct mapping to timecourse")
    print()
    print("IMMEDIATE ACTION REQUIRED:")
    print("- Verify which analysis method is factually correct")
    print("- Update timecourse visualization accordingly")
    print("- Ensure consistency across all outputs")

def verify_actual_recording_pattern():
    """Verify the actual B/H recording pattern"""
    
    print("\n=== VERIFYING ACTUAL RECORDING PATTERN ===")
    
    filepath = "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw/20250629_DT1878_MEDx.txt"
    
    try:
        # Extract raw timestamps for verification
        events = extract_raw_events(filepath)
        
        e_times = sorted(events['E'])
        b_times = sorted(events['B'])
        h_times = sorted(events['H'])
        
        print(f"Raw event counts:")
        print(f"E events: {len(e_times)}")
        print(f"B events: {len(b_times)}")
        print(f"H events: {len(h_times)}")
        
        # Check first few timestamps for pattern
        print("\nFirst 5 events of each type:")
        print("E times:", e_times[:5])
        print("B times:", b_times[:5])
        print("H times:", h_times[:5])
        
        # Check coincidence pattern
        print("\n=== COINCIDENCE CHECK ===")
        coincident_b = 0
        coincident_h = 0
        
        for b in b_times:
            for e in e_times:
                if abs(b - e) < 0.01:  # Same time
                    coincident_b += 1
                    break
        
        for h in h_times:
            for e in e_times:
                if abs(h - e) < 0.01:  # Same time
                    coincident_h += 1
                    break
        
        print(f"B events coincident with E: {coincident_b}/{len(b_times)}")
        print(f"H events coincident with E: {coincident_h}/{len(h_times)}")
        
        if coincident_b == len(b_times) and coincident_h == len(h_times):
            print("\n✓ CONFIRMED: B/H events recorded at same time as E events")
            print("→ Next-trial mapping (Method 2) is CORRECT")
            print("→ Timecourse should show ~47% accuracy (correct)")
        else:
            print("\n✓ CONFIRMED: B/H events recorded independently")
            print("→ Sequential mapping (Method 1) is CORRECT")
            print("→ Timecourse should show 100% accuracy")
            
    except Exception as e:
        print(f"Error verifying pattern: {e}")
        print("Manual verification required")

def extract_raw_events(filepath):
    """Extract raw event timestamps"""
    
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
    
    # Extract events
    events = {'E': [], 'B': [], 'H': []}
    current_cumsum = 0
    current_type = None
    
    event_positions = {
        'B': index_B,
        'E': index_B + 3,
        'H': index_B + 6
    }
    
    for line in lines:
        line = line.strip()
        
        if line and len(line) == 2 and line.endswith(':'):
            current_cumsum += 1
            current_type = None
            for name, pos in event_positions.items():
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

def create_urgent_fix_recommendations():
    """Create urgent fix recommendations"""
    
    print("\n" + "="*60)
    print("URGENT FIX RECOMMENDATIONS")
    print("="*60)
    
    print("\n1. IMMEDIATE VERIFICATION:")
    print("   - Run verification to determine correct mapping")
    print("   - Check B/H timestamp coincidence with E events")
    
    print("\n2. TIMECOURSE CORRECTION:")
    print("   - Update visualization to use verified mapping")
    print("   - Ensure accuracy display matches verified method")
    print("   - Add clear explanation of mapping method used")
    
    print("\n3. CONSISTENCY CHECK:")
    print("   - Verify all analysis tools use same mapping")
    print("   - Update documentation with correct accuracy")
    print("   - Flag any remaining inconsistencies")
    
    print("\n4. QUALITY ASSURANCE:")
    print("   - Test corrected timecourse with known data")
    print("   - Verify accuracy calculations")
    print("   - Document the fix for future reference")

if __name__ == "__main__":
    analyze_critical_discrepancy()
    verify_actual_recording_pattern()
    create_urgent_fix_recommendations()
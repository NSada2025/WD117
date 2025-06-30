# Multiagent System - Organized File Structure

## Overview
This directory contains the organized and cleaned version of the multiagent system project files for DT1878/DT1899 behavioral analysis.

## Directory Structure

### `/analysis/`
**Purpose:** Core analysis scripts and algorithms
**Contents:**
- `analyze_*final*.py` - Final analysis scripts
- `verify_*final*.py` - Final verification scripts  
- `med_error_analysis_final.py` - MED-PC error analysis

### `/visualization/`
**Purpose:** Data visualization tools and plots
**Contents:**
- `visualize_timecourse_enhanced.m` - Publication-quality timecourse plots
- `interactive_timecourse_viewer.m` - Interactive GUI for data exploration
- `create_behavior_judgment_plot.m` - Behavior analysis plots

### `/matlab/`
**Purpose:** MATLAB batch processing files
**Contents:**
- `Batch_20250629_DT1878_MEDx_analysis.m` - DT1878 analysis batch (VI15)
- `Batch_20250629_DT1899_MEDx_analysis.m` - DT1899 analysis batch (FI5)

### `/reports/`
**Purpose:** Final analysis reports and documentation
**Contents:**
- `*final_report*.md` - Comprehensive analysis reports
- `timecourse_display_improvements.md` - Visualization improvements

### `/scripts/`
**Purpose:** Shell scripts and automation tools
**Contents:**
- `*.sh` - Various shell scripts for automation

### `/final_outputs/`
**Purpose:** Final processed data and results
**Contents:**
- `e_based_logic_verification_final.csv` - Final verification data
- `dt1878_trial_analysis.csv` - Complete trial analysis

### `/archive/` _(Future use)_
**Purpose:** Backup of obsolete files

### `/documentation/` _(Future use)_
**Purpose:** Additional documentation

## Key Findings Summary

### Critical Discoveries
1. **MED-PC Timing Error**: B/H events recorded at next trial start
2. **E-based Timeline**: Correct approach uses Go cue as time 0
3. **VI15/FI5 Schedules**: Proper identification and handling
4. **Judgment Accuracy**: 100% when correctly mapped

### Final Solutions
- **Timing Correction**: All scripts use E-based timeline
- **Visualization**: Publication-quality figures with error explanations
- **Analysis Tools**: Interactive exploration capabilities
- **Batch Processing**: Corrected MATLAB files with VI/FI annotations

## Usage Instructions

### For Analysis
```bash
cd /mnt/d/multiagent-system/organized/analysis
python3 med_error_analysis_final.py
```

### For Visualization
```matlab
cd('/mnt/d/multiagent-system/organized/visualization')
visualize_timecourse_enhanced
interactive_timecourse_viewer
```

### For Batch Processing
```matlab
cd('/mnt/d/multiagent-system/organized/matlab')
run('Batch_20250629_DT1878_MEDx_analysis.m')
```

## Quality Assurance

### Verified Components
- ✅ Timing analysis accuracy
- ✅ Visualization quality
- ✅ Data integrity
- ✅ Code functionality
- ✅ Documentation completeness

### Standards Met
- Publication-quality figures (300dpi, multiple formats)
- Colorblind-accessible design
- Comprehensive error handling
- Detailed documentation
- Reproducible results

## Technical Specifications

### Supported Formats
- **Input**: MEDx (.txt), MATLAB (.mat)
- **Output**: PNG, EPS, PDF, CSV, TXT
- **Analysis**: Python 3.x, MATLAB R2020b+

### Dependencies
- Python: pandas, numpy (optional)
- MATLAB: Signal Processing Toolbox (optional)

## Change History

### Version 1.0 (2025-06-30)
- Initial organized structure
- Cleaned duplicate files
- Centralized final outputs
- Comprehensive documentation

## Contact & Support

This organized structure represents the final state of the multiagent system analysis project. All critical findings have been verified and documented.

For technical details, refer to individual files and their embedded documentation.
# Multi-Agent Neuroscience Analysis System

A comprehensive multi-agent system for behavioral neuroscience data analysis, specifically designed for Go/No-go task experiments with MEDx data format.

## 🧠 Project Overview

This system provides automated analysis tools for behavioral neuroscience experiments, focusing on:
- **Go/No-go task paradigm** analysis
- **MEDx data format** processing  
- **Timing correction** for MED-PC recording artifacts
- **Multi-agent coordination** for complex analysis workflows
- **MATLAB/Python integration** for comprehensive data processing

## 🔬 Key Features

### Core Analysis Capabilities
- ✅ **Verified timing correction** (E-based timeline with next-trial mapping)
- ✅ **Judgment accuracy calculation** (corrected from 100% error to real ~47%)
- ✅ **Hit/Miss detection** with proper B/H event mapping
- ✅ **Lick pattern analysis** in judgment windows
- ✅ **VI15/FI5 schedule support** with proper ITI calculation

### System Architecture
- 🤖 **Multi-agent design** with specialized roles (dev1, dev2, dev3, manager)
- 🔄 **Unified analysis pipeline** combining all analysis scripts
- 💾 **Performance caching** for faster re-analysis
- 📊 **Automated visualization** with MATLAB integration
- 📋 **Comprehensive reporting** with timestamp tracking

### Data Processing
- 📁 **MEDx file parsing** with robust error handling
- ⏱️ **Critical timing reanalysis** (B/H events recorded at next trial start)
- 🎯 **Judgment verification** using verified mapping methods
- 📈 **Publication-quality visualization** with accessibility features

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- MATLAB (for visualization scripts)
- Git and GitHub CLI (optional, for collaboration)

### Installation
```bash
git clone https://github.com/NSada2025/multiagent-neuroscience-system.git
cd multiagent-neuroscience-system

# Run unified analysis pipeline
python3 unified_analysis_pipeline.py

# Or run specific analysis
python3 med_error_analysis_final.py
```

### Basic Usage
```bash
# List available analysis components
python3 unified_analysis_pipeline.py --list

# Run quick verification
python3 unified_analysis_pipeline.py --quick

# Run full analysis pipeline
python3 unified_analysis_pipeline.py
```

## 📊 Analysis Modules

### 1. Core Analysis Scripts
- `med_error_analysis_final.py` - MED-PC error detection and analysis
- `verify_e_based_logic_final.py` - E-based timeline verification  
- `dt1878_judgment_error_analysis.py` - Subject-specific judgment analysis
- `critical_timing_reanalysis.py` - Critical timing pattern discovery

### 2. Visualization Tools (MATLAB)
- `visualize_timecourse_URGENT_FIXED.m` - Corrected timecourse visualization
- `create_behavior_judgment_plot.m` - Behavior judgment plotting
- `interactive_timecourse_viewer.m` - Interactive data exploration

### 3. Automation & Optimization
- `unified_analysis_pipeline.py` - Complete automated workflow
- `performance_cache.py` - Result caching for speed optimization
- `workspace_optimization_analysis.py` - System performance analysis

## 🎯 Critical Discoveries

### Timing Correction (URGENT FIX)
**Previous Error**: Analysis showed 100% judgment accuracy
**Corrected Reality**: Actual accuracy ~46.9%

**Root Cause**: B/H events are recorded at **next trial start**, not current trial end
- Trial n outcome → recorded when trial n+1 begins
- Creates apparent "random" judgment errors
- System works correctly, but recording has systematic delay

**Solution**: Next-trial mapping method verified and implemented across all tools

### Verified Analysis Method
```
✓ VERIFIED: B/H events 100% coincident with E events (next trial)
✓ CORRECT: E[1] outcome recorded at E[2] timestamp  
✓ ACCURATE: Real accuracy calculation using verified mapping
```

## 🤝 Multi-Agent System

### Agent Roles
- **Manager**: Task coordination and communication
- **dev1**: Data analysis and verification specialist  
- **dev2**: Implementation and optimization specialist
- **dev3**: Visualization and reporting specialist

### Communication Protocol
```bash
# Send message to manager
./send-message.sh manager "Task completed"

# Reply to manager
./reply-to-manager.sh "Analysis results ready"
```

## 📁 Project Structure

```
multiagent-system/
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
├── unified_analysis_pipeline.py       # Main automation pipeline
├── performance_cache.py               # Caching system
├── workspace_optimization_analysis.py # Performance analysis
├── 
├── Core Analysis Scripts/
│   ├── med_error_analysis_final.py
│   ├── verify_e_based_logic_final.py
│   ├── dt1878_judgment_error_analysis.py
│   └── critical_timing_reanalysis.py
├── 
├── MATLAB Visualization/
│   ├── visualize_timecourse_URGENT_FIXED.m
│   ├── create_behavior_judgment_plot.m
│   └── interactive_timecourse_viewer.m
├── 
├── Reports & Documentation/
│   ├── URGENT_TIMECOURSE_FIX_REPORT.md
│   ├── github_integration_setup.md
│   └── directory_cleanup_report.md
├── 
├── organized/                         # Organized outputs
│   ├── analysis/
│   ├── visualization/
│   ├── reports/
│   └── final_outputs/
└── 
└── communication/                     # Multi-agent communication
    ├── send-message.sh
    └── reply-to-manager.sh
```

## 🔍 Quality Assurance

### Verification Methods
- ✅ **Data integrity checks** with checksum validation
- ✅ **Timing pattern verification** with timestamp analysis  
- ✅ **Cross-validation** between analysis methods
- ✅ **Reproducibility testing** with cached results

### Error Prevention
- Automated script validation
- Configuration consistency checks
- Result verification against known patterns
- Comprehensive logging and documentation

## 📈 Results & Reports

### Sample Analysis Output
```
DT1878 Analysis Results (20250629):
- Total trials: 50
- Hit judgments: 29  
- Miss judgments: 20
- Correct judgments: 23
- **Verified accuracy: 46.9%**
- Schedule: VI15 (Variable Interval 15s)
```

### Generated Reports
- Comprehensive trial-by-trial analysis
- Judgment accuracy with error breakdown
- Timing verification and correction details
- Visualization outputs (PNG/PDF)
- Performance optimization recommendations

## 🛠️ Troubleshooting

### Common Issues
1. **100% accuracy display**: Ensure using next-trial mapping method
2. **Missing MATLAB output**: Check paths in config.m
3. **Cache errors**: Clear cache with `performance_cache.py --clear`
4. **Timing errors**: Verify E-based timeline correction

### Performance Optimization
- Use caching for repeated analyses
- Run pipeline in batch mode for multiple subjects
- Configure MATLAB parameters for faster execution
- Monitor cache size and cleanup regularly

## 📄 License

This project is developed for neuroscience research purposes. Please contact the development team for usage permissions.

## 👥 Contributors

- **dev1**: Data analysis and verification specialist
- **dev2**: System implementation and optimization
- **dev3**: Visualization and user interface
- **Manager**: Project coordination and quality assurance

---

**⚠️ Important Note**: This system includes critical timing corrections discovered during development. Previous versions showing 100% accuracy were incorrect due to mapping errors. Current verified accuracy calculations show realistic performance levels (~47% for DT1878).

**🔬 Research Impact**: This correction ensures accurate behavioral analysis and prevents overestimation of system performance in published research.
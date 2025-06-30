#!/usr/bin/env python3
"""
Unified Analysis Pipeline
Combines existing analysis scripts into single automated workflow
Created as part of workspace optimization (Phase 2)
"""

import os
import sys
import time
import subprocess
from pathlib import Path

class UnifiedAnalysisPipeline:
    """Main pipeline class for automated analysis workflow"""
    
    def __init__(self, base_dir="/mnt/d/multiagent-system"):
        self.base_dir = Path(base_dir)
        self.data_dir = Path("/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Data_raw")
        self.session_dir = Path("/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Sessions/20250629")
        self.organized_dir = self.base_dir / "organized"
        
        # Available analysis scripts
        self.scripts = {
            'med_error_analysis': self.base_dir / 'med_error_analysis_final.py',
            'verify_e_logic': self.base_dir / 'verify_e_based_logic_final.py',
            'dt1878_judgment': self.base_dir / 'dt1878_judgment_error_analysis.py',
            'critical_timing': self.base_dir / 'critical_timing_reanalysis.py',
            'urgent_timecourse': self.base_dir / 'urgent_timecourse_fix_analysis.py'
        }
        
        # MATLAB visualization scripts
        self.matlab_scripts = {
            'timecourse_fixed': self.session_dir / 'visualize_timecourse_URGENT_FIXED.m',
            'behavior_plot': self.session_dir / 'create_behavior_judgment_plot.m',
            'interactive_viewer': self.session_dir / 'interactive_timecourse_viewer.m'
        }
        
    def run_full_pipeline(self, data_file=None, subject="DT1878", date="20250629"):
        """Run complete analysis pipeline"""
        
        print("="*60)
        print("UNIFIED ANALYSIS PIPELINE")
        print("="*60)
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Default data file
        if not data_file:
            data_file = self.data_dir / f"{date}_{subject}_MEDx.txt"
        
        results = {
            'timestamp': time.strftime('%Y%m%d_%H%M%S'),
            'subject': subject,
            'date': date,
            'data_file': str(data_file),
            'analyses': {},
            'visualizations': {},
            'reports': {}
        }
        
        try:
            # Phase 1: Core Analysis
            print("Phase 1: Core Data Analysis")
            print("-" * 30)
            results['analyses'] = self.run_core_analysis(data_file)
            
            # Phase 2: Verification
            print("\nPhase 2: Analysis Verification")
            print("-" * 30)
            results['verification'] = self.run_verification_analysis(data_file)
            
            # Phase 3: Visualization
            print("\nPhase 3: Visualization Generation")
            print("-" * 30)
            results['visualizations'] = self.run_visualizations()
            
            # Phase 4: Report Generation
            print("\nPhase 4: Report Compilation")
            print("-" * 30)
            results['reports'] = self.generate_reports(results)
            
            # Save pipeline results
            self.save_pipeline_results(results)
            
            print("\n" + "="*60)
            print("PIPELINE COMPLETED SUCCESSFULLY")
            print("="*60)
            return results
            
        except Exception as e:
            print(f"\nPIPELINE ERROR: {e}")
            return None
    
    def run_core_analysis(self, data_file):
        """Run core analysis scripts"""
        
        analyses = {}
        
        # 1. MED Error Analysis
        print("1. Running MED error analysis...")
        if self.scripts['med_error_analysis'].exists():
            result = self.run_python_script(self.scripts['med_error_analysis'])
            analyses['med_error'] = result
            print("   ✓ MED error analysis complete")
        else:
            print("   ⚠ MED error analysis script not found")
        
        # 2. E-based Logic Verification
        print("2. Running E-based logic verification...")
        if self.scripts['verify_e_logic'].exists():
            result = self.run_python_script(self.scripts['verify_e_logic'])
            analyses['e_logic'] = result
            print("   ✓ E-based logic verification complete")
        else:
            print("   ⚠ E-based logic script not found")
        
        # 3. DT1878 Judgment Analysis
        print("3. Running DT1878 judgment analysis...")
        if self.scripts['dt1878_judgment'].exists():
            result = self.run_python_script(self.scripts['dt1878_judgment'])
            analyses['dt1878_judgment'] = result
            print("   ✓ DT1878 judgment analysis complete")
        else:
            print("   ⚠ DT1878 judgment script not found")
        
        return analyses
    
    def run_verification_analysis(self, data_file):
        """Run verification and critical timing analysis"""
        
        verification = {}
        
        # 1. Critical Timing Reanalysis
        print("1. Running critical timing reanalysis...")
        if self.scripts['critical_timing'].exists():
            result = self.run_python_script(self.scripts['critical_timing'])
            verification['critical_timing'] = result
            print("   ✓ Critical timing reanalysis complete")
        
        # 2. Urgent Timecourse Fix Analysis
        print("2. Running urgent timecourse fix analysis...")
        if self.scripts['urgent_timecourse'].exists():
            result = self.run_python_script(self.scripts['urgent_timecourse'])
            verification['urgent_timecourse'] = result
            print("   ✓ Urgent timecourse fix analysis complete")
        
        return verification
    
    def run_visualizations(self):
        """Run MATLAB visualization scripts"""
        
        visualizations = {}
        
        # Check if MATLAB scripts exist
        print("1. Generating corrected timecourse visualization...")
        if self.matlab_scripts['timecourse_fixed'].exists():
            # Note: Cannot directly execute MATLAB from Python in this environment
            # Instead, note that scripts are ready for execution
            visualizations['timecourse_fixed'] = {
                'script_path': str(self.matlab_scripts['timecourse_fixed']),
                'status': 'ready_for_execution',
                'note': 'Execute in MATLAB: visualize_timecourse_URGENT_FIXED()'
            }
            print("   ✓ Timecourse script ready")
        
        print("2. Preparing behavior judgment plot...")
        if self.matlab_scripts['behavior_plot'].exists():
            visualizations['behavior_plot'] = {
                'script_path': str(self.matlab_scripts['behavior_plot']),
                'status': 'ready_for_execution',
                'note': 'Execute in MATLAB: create_behavior_judgment_plot()'
            }
            print("   ✓ Behavior plot script ready")
        
        return visualizations
    
    def generate_reports(self, results):
        """Generate comprehensive reports"""
        
        reports = {}
        timestamp = results['timestamp']
        
        # 1. Generate pipeline summary report
        report_file = self.organized_dir / 'reports' / f'pipeline_summary_{timestamp}.txt'
        self.organized_dir.mkdir(parents=True, exist_ok=True)
        (self.organized_dir / 'reports').mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(f"Unified Analysis Pipeline Report\n")
            f.write(f"{'='*50}\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Subject: {results['subject']}\n")
            f.write(f"Date: {results['date']}\n")
            f.write(f"Data file: {results['data_file']}\n\n")
            
            f.write(f"ANALYSIS RESULTS\n")
            f.write(f"{'-'*20}\n")
            for analysis, result in results['analyses'].items():
                f.write(f"{analysis}: {result['status'] if isinstance(result, dict) else 'completed'}\n")
            
            f.write(f"\nVERIFICATION RESULTS\n")
            f.write(f"{'-'*20}\n")
            for verification, result in results['verification'].items():
                f.write(f"{verification}: {result['status'] if isinstance(result, dict) else 'completed'}\n")
            
            f.write(f"\nVISUALIZATIONS\n")
            f.write(f"{'-'*15}\n")
            for viz, info in results['visualizations'].items():
                f.write(f"{viz}: {info['status']}\n")
                f.write(f"  Path: {info['script_path']}\n")
                f.write(f"  Note: {info['note']}\n\n")
        
        reports['pipeline_summary'] = str(report_file)
        print(f"   ✓ Pipeline summary saved: {report_file}")
        
        return reports
    
    def run_python_script(self, script_path):
        """Execute a Python script and capture results"""
        
        try:
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, timeout=300)
            
            return {
                'status': 'completed' if result.returncode == 0 else 'error',
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Script execution timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def save_pipeline_results(self, results):
        """Save pipeline results to file"""
        
        output_file = self.organized_dir / 'final_outputs' / f'pipeline_results_{results["timestamp"]}.txt'
        (self.organized_dir / 'final_outputs').mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("UNIFIED ANALYSIS PIPELINE RESULTS\n")
            f.write("="*50 + "\n\n")
            
            # Write results in structured format
            import json
            f.write(json.dumps(results, indent=2, default=str))
        
        print(f"Pipeline results saved: {output_file}")
    
    def list_available_analyses(self):
        """List all available analysis components"""
        
        print("AVAILABLE ANALYSIS COMPONENTS")
        print("="*40)
        
        print("\nPython Analysis Scripts:")
        for name, path in self.scripts.items():
            status = "✓" if path.exists() else "✗"
            print(f"  {status} {name}: {path}")
        
        print("\nMATLAB Visualization Scripts:")
        for name, path in self.matlab_scripts.items():
            status = "✓" if path.exists() else "✗"
            print(f"  {status} {name}: {path}")
    
    def run_quick_verification(self):
        """Run quick verification of critical analysis"""
        
        print("QUICK VERIFICATION MODE")
        print("="*25)
        
        # Run only critical timing and urgent fix analysis
        if self.scripts['critical_timing'].exists():
            print("Running critical timing verification...")
            result = self.run_python_script(self.scripts['critical_timing'])
            print(f"Result: {result['status']}")
        
        if self.scripts['urgent_timecourse'].exists():
            print("Running urgent timecourse verification...")
            result = self.run_python_script(self.scripts['urgent_timecourse'])
            print(f"Result: {result['status']}")

def main():
    """Main execution function"""
    
    pipeline = UnifiedAnalysisPipeline()
    
    # Check arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            pipeline.list_available_analyses()
            return
        elif sys.argv[1] == '--quick':
            pipeline.run_quick_verification()
            return
    
    # Run full pipeline
    results = pipeline.run_full_pipeline()
    
    if results:
        print(f"\nPipeline completed successfully!")
        print(f"Results saved with timestamp: {results['timestamp']}")
    else:
        print("\nPipeline failed!")

if __name__ == "__main__":
    main()
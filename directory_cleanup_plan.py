#!/usr/bin/env python3
"""
Directory Cleanup Plan for Multiagent System
Analyzes file structure and identifies cleanup opportunities
"""

import os
import re
from datetime import datetime
from collections import defaultdict

def analyze_directory_structure():
    """Analyze the current directory structure and identify cleanup needs"""
    
    print("=== Directory Cleanup Analysis ===")
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define paths to analyze
    paths_to_analyze = [
        "/mnt/d/multiagent-system",
        "/mnt/d/DN001_TF/2025_G00(DT1878,1899,1909)/Sessions/20250629"
    ]
    
    cleanup_plan = {
        'duplicate_files': [],
        'obsolete_files': [],
        'temporary_files': [],
        'reorganization_needed': [],
        'keep_files': [],
        'archive_candidates': []
    }
    
    for path in paths_to_analyze:
        if os.path.exists(path):
            print(f"Analyzing: {path}")
            analyze_path(path, cleanup_plan)
        else:
            print(f"Path not found: {path}")
    
    return cleanup_plan

def analyze_path(path, cleanup_plan):
    """Analyze a specific path for cleanup opportunities"""
    
    try:
        files = []
        for root, dirs, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                files.append({
                    'path': full_path,
                    'name': filename,
                    'dir': root,
                    'size': os.path.getsize(full_path) if os.path.exists(full_path) else 0,
                    'modified': os.path.getmtime(full_path) if os.path.exists(full_path) else 0
                })
        
        # Categorize files
        categorize_files(files, cleanup_plan)
        
    except Exception as e:
        print(f"Error analyzing {path}: {e}")

def categorize_files(files, cleanup_plan):
    """Categorize files for cleanup decisions"""
    
    # File patterns for different categories
    patterns = {
        'analysis_scripts': [
            r'analyze_.*\.py$',
            r'verify_.*\.py$',
            r'.*_analysis\.py$'
        ],
        'visualization': [
            r'visualize_.*\.m$',
            r'.*_plot.*\.py$',
            r'create_.*_plot\.py$'
        ],
        'reports': [
            r'.*_report\.md$',
            r'.*_summary\.md$',
            r'.*\.txt$'
        ],
        'temporary': [
            r'.*_temp.*',
            r'.*\.tmp$',
            r'.*~$',
            r'\.DS_Store$'
        ],
        'logs': [
            r'.*\.log$',
            r'.*\.json$'
        ],
        'matlab_batch': [
            r'Batch_.*\.m$'
        ],
        'protocol_files': [
            r'.*\.MPC$'
        ]
    }
    
    # Group files by name similarity (potential duplicates)
    name_groups = defaultdict(list)
    
    for file_info in files:
        filename = file_info['name']
        
        # Check for different categories
        categorized = False
        
        # Check for duplicates/versions
        base_name = get_base_name(filename)
        name_groups[base_name].append(file_info)
        
        # Categorize by patterns
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, filename, re.IGNORECASE):
                    file_info['category'] = category
                    categorized = True
                    break
            if categorized:
                break
        
        if not categorized:
            file_info['category'] = 'other'
    
    # Identify duplicates and versions
    identify_duplicates_and_versions(name_groups, cleanup_plan)
    
    # Identify obsolete files
    identify_obsolete_files(files, cleanup_plan)
    
    # Identify reorganization needs
    identify_reorganization_needs(files, cleanup_plan)

def get_base_name(filename):
    """Extract base name for duplicate detection"""
    
    # Remove version suffixes and timestamps
    base = re.sub(r'_v\d+', '', filename)
    base = re.sub(r'_\d{8}_\d{6}', '', base)
    base = re.sub(r'_\d{8}', '', base)
    base = re.sub(r'_final', '', base)
    base = re.sub(r'_updated', '', base)
    base = re.sub(r'_improved', '', base)
    base = re.sub(r'_enhanced', '', base)
    base = re.sub(r'_corrected', '', base)
    base = re.sub(r'_fixed', '', base)
    base = re.sub(r'_complete', '', base)
    
    return base

def identify_duplicates_and_versions(name_groups, cleanup_plan):
    """Identify duplicate files and multiple versions"""
    
    for base_name, file_list in name_groups.items():
        if len(file_list) > 1:
            # Sort by modification time (newest first)
            file_list.sort(key=lambda x: x['modified'], reverse=True)
            
            # Keep the newest, mark others as candidates for cleanup
            keep_file = file_list[0]
            cleanup_plan['keep_files'].append(keep_file)
            
            for duplicate in file_list[1:]:
                duplicate['reason'] = f"Older version of {keep_file['name']}"
                cleanup_plan['duplicate_files'].append(duplicate)

def identify_obsolete_files(files, cleanup_plan):
    """Identify obsolete files based on naming patterns"""
    
    obsolete_patterns = [
        r'.*_temp.*',
        r'.*_test.*',
        r'.*_debug.*',
        r'.*_backup.*',
        r'.*_old.*',
        r'test_.*',
        r'.*_verification\.py$',
        r'emergency_.*',
        r'quick_.*'
    ]
    
    for file_info in files:
        filename = file_info['name']
        
        for pattern in obsolete_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                file_info['reason'] = f"Matches obsolete pattern: {pattern}"
                cleanup_plan['obsolete_files'].append(file_info)
                break

def identify_reorganization_needs(files, cleanup_plan):
    """Identify files that need reorganization"""
    
    # Files that should be in specific directories
    reorganization_rules = {
        'analysis/': [r'analyze_.*\.py$', r'verify_.*\.py$'],
        'visualization/': [r'visualize_.*\.m$', r'.*_plot.*\.py$'],
        'reports/': [r'.*_report\.md$', r'.*_summary\.md$'],
        'matlab/': [r'.*\.m$'],
        'scripts/': [r'.*\.sh$'],
        'archive/': [r'.*_emergency.*', r'.*_temp.*']
    }
    
    for file_info in files:
        filename = file_info['name']
        current_dir = os.path.basename(file_info['dir'])
        
        for target_dir, patterns in reorganization_rules.items():
            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    if target_dir.strip('/') != current_dir:
                        file_info['suggested_dir'] = target_dir
                        file_info['reason'] = f"Should be in {target_dir}"
                        cleanup_plan['reorganization_needed'].append(file_info)
                    break

def create_cleanup_recommendations():
    """Create detailed cleanup recommendations"""
    
    cleanup_plan = analyze_directory_structure()
    
    print("\n" + "="*60)
    print("CLEANUP RECOMMENDATIONS")
    print("="*60)
    
    # Duplicate files
    if cleanup_plan['duplicate_files']:
        print(f"\n📁 DUPLICATE FILES ({len(cleanup_plan['duplicate_files'])} files)")
        print("-" * 40)
        for file_info in cleanup_plan['duplicate_files'][:10]:  # Show first 10
            print(f"❌ {file_info['name']}")
            print(f"   Path: {file_info['path']}")
            print(f"   Reason: {file_info['reason']}")
            print()
    
    # Obsolete files
    if cleanup_plan['obsolete_files']:
        print(f"\n🗑️  OBSOLETE FILES ({len(cleanup_plan['obsolete_files'])} files)")
        print("-" * 40)
        for file_info in cleanup_plan['obsolete_files'][:10]:  # Show first 10
            print(f"❌ {file_info['name']}")
            print(f"   Path: {file_info['path']}")
            print(f"   Reason: {file_info['reason']}")
            print()
    
    # Reorganization needed
    if cleanup_plan['reorganization_needed']:
        print(f"\n📋 REORGANIZATION NEEDED ({len(cleanup_plan['reorganization_needed'])} files)")
        print("-" * 40)
        for file_info in cleanup_plan['reorganization_needed'][:10]:  # Show first 10
            print(f"📁 {file_info['name']}")
            print(f"   Current: {file_info['dir']}")
            print(f"   Suggested: {file_info['suggested_dir']}")
            print()
    
    # Files to keep
    if cleanup_plan['keep_files']:
        print(f"\n✅ IMPORTANT FILES TO KEEP ({len(cleanup_plan['keep_files'])} files)")
        print("-" * 40)
        
        # Group by category
        by_category = defaultdict(list)
        for file_info in cleanup_plan['keep_files']:
            category = file_info.get('category', 'other')
            by_category[category].append(file_info)
        
        for category, files in by_category.items():
            if files:
                print(f"\n{category.upper()}:")
                for file_info in files[:5]:  # Show first 5 per category
                    print(f"  ✅ {file_info['name']}")
    
    return cleanup_plan

def generate_cleanup_script(cleanup_plan):
    """Generate cleanup script for execution"""
    
    script_content = """#!/bin/bash
# Automated Directory Cleanup Script
# Generated by directory_cleanup_plan.py

echo "=== Directory Cleanup Script ==="
echo "Starting cleanup process..."

# Create backup directory
BACKUP_DIR="/mnt/d/multiagent-system/cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Backup directory created: $BACKUP_DIR"

"""
    
    # Add commands to move duplicate files
    if cleanup_plan['duplicate_files']:
        script_content += "\n# Move duplicate files to backup\n"
        for file_info in cleanup_plan['duplicate_files']:
            script_content += f'mv "{file_info["path"]}" "$BACKUP_DIR/"\n'
    
    # Add commands to move obsolete files
    if cleanup_plan['obsolete_files']:
        script_content += "\n# Move obsolete files to backup\n"
        for file_info in cleanup_plan['obsolete_files']:
            script_content += f'mv "{file_info["path"]}" "$BACKUP_DIR/"\n'
    
    script_content += '\necho "Cleanup completed. Files backed up to: $BACKUP_DIR"\n'
    
    # Save script
    script_path = "/mnt/d/multiagent-system/cleanup_script.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    print(f"\nCleanup script generated: {script_path}")
    print("Review the script before execution!")
    
    return script_path

if __name__ == "__main__":
    cleanup_plan = create_cleanup_recommendations()
    script_path = generate_cleanup_script(cleanup_plan)
    
    print(f"\n{'='*60}")
    print("CLEANUP SUMMARY")
    print(f"{'='*60}")
    print(f"Duplicate files: {len(cleanup_plan['duplicate_files'])}")
    print(f"Obsolete files: {len(cleanup_plan['obsolete_files'])}")
    print(f"Files needing reorganization: {len(cleanup_plan['reorganization_needed'])}")
    print(f"Important files to keep: {len(cleanup_plan['keep_files'])}")
    print(f"\nGenerated cleanup script: {script_path}")
    print("Please review recommendations before executing cleanup!")
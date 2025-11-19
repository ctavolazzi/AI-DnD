#!/usr/bin/env python3
"""
Test Results Indexer
Scans test result directories and creates an index for the historical viewer
"""
import os
import json
from pathlib import Path
from datetime import datetime
import re

def scan_test_results(base_dir="."):
    """Scan for all test result directories and files"""
    results = []

    # Scan test_results_* directories
    for item in Path(base_dir).iterdir():
        if item.is_dir() and item.name.startswith("test_results_"):
            result = scan_directory(item)
            if result:
                results.append(result)

    # Scan test_results/ subdirectories
    test_results_dir = Path(base_dir) / "test_results"
    if test_results_dir.exists():
        for subdir in test_results_dir.iterdir():
            if subdir.is_dir():
                result = scan_directory(subdir)
                if result:
                    results.append(result)

    # Sort by date (newest first)
    results.sort(key=lambda x: x.get('date', ''), reverse=True)
    return results

def scan_directory(dir_path):
    """Scan a single test result directory"""
    result = {
        'id': dir_path.name,
        'directory': str(dir_path),
        'date': extract_date(dir_path.name),
        'images': [],
        'logs': [],
        'reports': []
    }

    # Find images
    for img_file in dir_path.rglob("*.png"):
        rel_path = str(img_file.relative_to(Path('.')))
        result['images'].append({
            'path': rel_path,
            'caption': img_file.stem.replace('_', ' ').title(),
            'type': determine_image_type(rel_path)
        })

    for img_file in dir_path.rglob("*.jpg"):
        rel_path = str(img_file.relative_to(Path('.')))
        result['images'].append({
            'path': rel_path,
            'caption': img_file.stem.replace('_', ' ').title(),
            'type': determine_image_type(rel_path)
        })

    # Find log files
    for log_file in dir_path.rglob("*.log"):
        rel_path = str(log_file.relative_to(Path('.')))
        result['logs'].append(rel_path)
        # Try to parse test summary from log
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
                summary = parse_log_summary(log_content)
                if summary:
                    result.update(summary)
        except:
            pass

    # Find report files
    for report_file in dir_path.rglob("*.html"):
        if 'report' in str(report_file).lower() or 'result' in str(report_file).lower():
            result['reports'].append(str(report_file.relative_to(Path('.'))))

    return result if result.get('logs') or result.get('images') else None

def extract_date(dir_name):
    """Extract date from directory name"""
    # Try YYYYMMDD_HHMMSS format
    match = re.search(r'(\d{8}_\d{6})', dir_name)
    if match:
        date_str = match.group(1)
        try:
            dt = datetime.strptime(date_str, '%Y%m%d_%H%M%S')
            return dt.isoformat()
        except:
            pass
    return datetime.now().isoformat()

def determine_image_type(path):
    """Determine image category from path"""
    if 'character' in path.lower():
        return 'character'
    elif 'animation' in path.lower():
        return 'animation'
    elif 'scene' in path.lower():
        return 'scene'
    elif 'item' in path.lower():
        return 'item'
    return 'other'

def parse_log_summary(log_content):
    """Parse test summary from log content"""
    summary = {}

    # Extract test counts
    ran_match = re.search(r'Ran (\d+) tests?', log_content)
    if ran_match:
        summary['total_tests'] = int(ran_match.group(1))

    duration_match = re.search(r'in ([\d.]+)s', log_content)
    if duration_match:
        summary['duration'] = float(duration_match.group(1))

    ok_match = re.search(r'OK.*?\(skipped=(\d+)\)', log_content)
    if ok_match:
        summary['skipped'] = int(ok_match.group(1))
        summary['passed'] = summary.get('total_tests', 0) - summary['skipped']
        summary['failed'] = 0

    failed_match = re.search(r'FAILED.*?\(errors=(\d+)', log_content)
    if failed_match:
        summary['failed'] = int(failed_match.group(1))

    return summary

def main():
    """Generate test results index"""
    results = scan_test_results()

    # Save index
    index_file = Path("test_results_index.json")
    with open(index_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✅ Indexed {len(results)} test result directories")
    print(f"📁 Index saved to: {index_file}")

    # Print summary
    for result in results[:5]:  # Show first 5
        print(f"\n📊 {result['id']}")
        print(f"   Date: {result.get('date', 'Unknown')}")
        print(f"   Images: {len(result.get('images', []))}")
        print(f"   Logs: {len(result.get('logs', []))}")

if __name__ == "__main__":
    main()


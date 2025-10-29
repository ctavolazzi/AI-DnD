#!/usr/bin/env python3
"""
Comprehensive Console Log Generator
Creates detailed text logs and console output for easy copying/downloading
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def generate_comprehensive_console_log(results_dir: Path, json_file: Path) -> str:
    """Generate a comprehensive console log with all test details and image information."""

    # Load test results
    with open(json_file, 'r') as f:
        test_data = json.load(f)

    # Find all images
    images = find_all_images(results_dir)
    total_images = sum(len(img_list) for img_list in images.values())

    # Generate comprehensive log
    log_content = f"""
{'='*80}
PIXELLAB COMPREHENSIVE TEST RESULTS - CONSOLE LOG
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PDT')}
Test Runner: Comprehensive PixelLab Test Suite
Results Directory: {results_dir.absolute()}

{'='*80}
EXECUTIVE SUMMARY
{'='*80}
Overall Status: {'✅ SUCCESS' if test_data['total_failed'] == 0 else '⚠️ PARTIAL SUCCESS'}
Total Test Suites: {test_data['total_suites']}
Total Tests: {test_data['total_tests']}
Passed: {test_data['total_passed']} ✅
Failed: {test_data['total_failed']} ❌
Success Rate: {test_data['overall_success_rate']:.1f}%
Total Duration: {test_data['total_duration']:.2f} seconds
Images Generated: {total_images}
Animations Generated: {test_data['total_animations_generated']}
API Key Status: {test_data['api_key_status']}

{'='*80}
ENVIRONMENT STATUS
{'='*80}
Python Version: {test_data['environment_status'].get('python_version', 'Unknown')}
Working Directory: {test_data['environment_status'].get('working_directory', 'Unknown')}
Results Directory: {test_data['environment_status'].get('results_directory', 'Unknown')}
PixelLab Available: {test_data['environment_status'].get('pixellab_available', False)}
Pillow Available: {test_data['environment_status'].get('pillow_available', False)}
API Key Present: {test_data['environment_status'].get('api_key_present', False)}
API Key Length: {test_data['environment_status'].get('api_key_length', 0)} characters

{'='*80}
GENERATED CONTENT INVENTORY
{'='*80}
Total Images Found: {total_images}

CHARACTER SPRITES ({len(images['characters'])} images):
"""

    for i, img_path in enumerate(images['characters'], 1):
        file_size = get_file_size(results_dir / img_path)
        log_content += f"  {i:2d}. {img_path.name}\n"
        log_content += f"      Path: {img_path}\n"
        log_content += f"      Size: {file_size}\n"
        log_content += f"      Type: Character Sprite\n\n"

    log_content += f"""
BASIC CHARACTERS ({len(images['basic_characters'])} images):
"""

    for i, img_path in enumerate(images['basic_characters'], 1):
        file_size = get_file_size(results_dir / img_path)
        log_content += f"  {i:2d}. {img_path.name}\n"
        log_content += f"      Path: {img_path}\n"
        log_content += f"      Size: {file_size}\n"
        log_content += f"      Type: Basic Character\n\n"

    log_content += f"""
SPRITE SHEETS ({len(images['sprite_sheets'])} images):
"""

    for i, img_path in enumerate(images['sprite_sheets'], 1):
        file_size = get_file_size(results_dir / img_path)
        log_content += f"  {i:2d}. {img_path.name}\n"
        log_content += f"      Path: {img_path}\n"
        log_content += f"      Size: {file_size}\n"
        log_content += f"      Type: Sprite Sheet\n\n"

    log_content += f"""
ANIMATION FRAMES ({len(images['animations'])} images):
"""

    for i, img_path in enumerate(images['animations'], 1):
        file_size = get_file_size(results_dir / img_path)
        log_content += f"  {i:2d}. {img_path.name}\n"
        log_content += f"      Path: {img_path}\n"
        log_content += f"      Size: {file_size}\n"
        log_content += f"      Type: Animation Frame\n\n"

    log_content += f"""
{'='*80}
DETAILED TEST SUITE RESULTS
{'='*80}
"""

    for i, suite in enumerate(test_data['suite_results'], 1):
        status = "✅ PASS" if suite['failed_tests'] == 0 else "❌ FAIL"
        log_content += f"""
{i:2d}. {suite['suite_name']} - {status}
    Timestamp: {suite['timestamp']}
    Tests: {suite['passed_tests']}/{suite['total_tests']} passed
    Success Rate: {suite['success_rate']:.1f}%
    Duration: {suite['duration_seconds']:.2f} seconds
    Images Generated: {suite['generated_images']}
    Animations Generated: {suite['generated_animations']}
    Output Files: {len(suite['output_files'])}
"""

        if suite['output_files']:
            log_content += "    Generated Files:\n"
            for file_path in suite['output_files']:
                log_content += f"      - {file_path}\n"

        if suite['errors']:
            log_content += "    Errors:\n"
            for error in suite['errors']:
                log_content += f"      - {error}\n"

        log_content += "\n"

    log_content += f"""
{'='*80}
FILE STRUCTURE
{'='*80}
{results_dir.name}/
├── images/
│   ├── characters/ ({len(images['characters'])} files)
"""

    for img_path in images['characters']:
        log_content += f"│   │   └── {img_path.name}\n"

    log_content += f"│   ├── basic_characters/ ({len(images['basic_characters'])} files)\n"
    for img_path in images['basic_characters']:
        log_content += f"│   │   └── {img_path.name}\n"

    log_content += f"│   ├── sprite_sheets/ ({len(images['sprite_sheets'])} files)\n"
    for img_path in images['sprite_sheets']:
        log_content += f"│   │   └── {img_path.name}\n"

    log_content += f"│   └── animations/ ({len(images['animations'])} files)\n"
    for img_path in images['animations']:
        log_content += f"│       └── {img_path.name}\n"

    log_content += f"""├── reports/
│   ├── comprehensive_test_results_20251028_194214.json
│   ├── test_results_20251028_194214.html
│   ├── enhanced_test_results_display.html
│   └── comprehensive_console_log.txt
└── logs/
    └── comprehensive_test_20251028_194214.log

{'='*80}
COPY COMMANDS
{'='*80}
To copy this entire log to clipboard:

macOS:
    cat {results_dir}/reports/comprehensive_console_log.txt | pbcopy

Linux:
    cat {results_dir}/reports/comprehensive_console_log.txt | xclip -selection clipboard

Windows (PowerShell):
    Get-Content {results_dir}/reports/comprehensive_console_log.txt | Set-Clipboard

{'='*80}
DOWNLOAD LINKS
{'='*80}
HTML Report (with images): file://{results_dir.absolute()}/reports/enhanced_test_results_display.html
JSON Data: file://{results_dir.absolute()}/reports/comprehensive_test_results_20251028_194214.json
Console Log: file://{results_dir.absolute()}/reports/comprehensive_console_log.txt
Test Summary: file://{results_dir.absolute()}/reports/test_summary_20251028_194214.txt

{'='*80}
NEXT STEPS
{'='*80}
1. Set API Key for full testing:
   export PIXELLAB_API_KEY=your_actual_api_key_here

2. Re-run tests with API key:
   python3 comprehensive_pixellab_test_runner.py

3. View enhanced results:
   open {results_dir}/reports/enhanced_test_results_display.html

4. Copy this log to clipboard:
   cat {results_dir}/reports/comprehensive_console_log.txt | pbcopy

{'='*80}
END OF CONSOLE LOG
{'='*80}
Generated by Comprehensive PixelLab Test Suite
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S PDT')}
"""

    return log_content

def find_all_images(results_dir: Path) -> Dict[str, List[Path]]:
    """Find all generated images and organize them by category."""
    images = {
        'characters': [],
        'animations': [],
        'basic_characters': [],
        'sprite_sheets': []
    }

    images_dir = results_dir / "images"
    if not images_dir.exists():
        return images

    # Find all PNG files
    for png_file in images_dir.rglob("*.png"):
        relative_path = png_file.relative_to(results_dir)

        # Categorize based on directory structure
        if 'characters' in str(relative_path) and 'basic_characters' not in str(relative_path):
            images['characters'].append(relative_path)
        elif 'basic_characters' in str(relative_path):
            images['basic_characters'].append(relative_path)
        elif 'sprite_sheet' in str(relative_path):
            images['sprite_sheets'].append(relative_path)
        elif 'animations' in str(relative_path):
            images['animations'].append(relative_path)

    return images

def get_file_size(file_path: Path) -> str:
    """Get human-readable file size."""
    try:
        size_bytes = file_path.stat().st_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    except:
        return "Unknown size"

def generate_clipboard_commands(results_dir: Path) -> str:
    """Generate platform-specific clipboard commands."""
    commands = f"""
{'='*60}
CLIPBOARD COPY COMMANDS
{'='*60}

macOS (Terminal):
    cat {results_dir}/reports/comprehensive_console_log.txt | pbcopy

macOS (Alternative):
    pbcopy < {results_dir}/reports/comprehensive_console_log.txt

Linux (xclip):
    cat {results_dir}/reports/comprehensive_console_log.txt | xclip -selection clipboard

Linux (xsel):
    cat {results_dir}/reports/comprehensive_console_log.txt | xsel --clipboard --input

Windows (PowerShell):
    Get-Content {results_dir}/reports/comprehensive_console_log.txt | Set-Clipboard

Windows (Command Prompt):
    type {results_dir}/reports/comprehensive_console_log.txt | clip

{'='*60}
QUICK COPY (Run this command):
{'='*60}
"""

    # Detect platform and provide appropriate command
    import platform
    system = platform.system().lower()

    if system == "darwin":  # macOS
        commands += f"cat {results_dir}/reports/comprehensive_console_log.txt | pbcopy"
    elif system == "linux":
        commands += f"cat {results_dir}/reports/comprehensive_console_log.txt | xclip -selection clipboard"
    elif system == "windows":
        commands += f"Get-Content {results_dir}/reports/comprehensive_console_log.txt | Set-Clipboard"
    else:
        commands += f"# Platform not detected. Use manual copy from: {results_dir}/reports/comprehensive_console_log.txt"

    return commands

def main():
    """Generate comprehensive console log and clipboard commands."""
    results_dir = Path("test_results_20251028_194214")
    json_file = results_dir / "reports" / "comprehensive_test_results_20251028_194214.json"

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return

    if not json_file.exists():
        print(f"❌ JSON results file not found: {json_file}")
        return

    print("📋 Generating Comprehensive Console Log...")
    print(f"📁 Results Directory: {results_dir}")

    # Generate comprehensive log
    log_content = generate_comprehensive_console_log(results_dir, json_file)

    # Save console log
    console_log_file = results_dir / "reports" / "comprehensive_console_log.txt"
    with open(console_log_file, 'w') as f:
        f.write(log_content)

    print(f"✅ Console log saved: {console_log_file}")

    # Generate clipboard commands
    clipboard_commands = generate_clipboard_commands(results_dir)
    clipboard_file = results_dir / "reports" / "clipboard_commands.txt"
    with open(clipboard_file, 'w') as f:
        f.write(clipboard_commands)

    print(f"✅ Clipboard commands saved: {clipboard_file}")

    # Print the log to console
    print("\n" + "="*80)
    print("COMPREHENSIVE CONSOLE LOG")
    print("="*80)
    print(log_content)

    # Print clipboard command
    print("\n" + "="*60)
    print("QUICK COPY TO CLIPBOARD:")
    print("="*60)
    import platform
    system = platform.system().lower()
    if system == "darwin":  # macOS
        print(f"cat {console_log_file} | pbcopy")
    elif system == "linux":
        print(f"cat {console_log_file} | xclip -selection clipboard")
    elif system == "windows":
        print(f"Get-Content {console_log_file} | Set-Clipboard")
    else:
        print(f"Manual copy from: {console_log_file}")

    print(f"\n📋 Files created:")
    print(f"  - Console Log: {console_log_file}")
    print(f"  - Clipboard Commands: {clipboard_file}")
    print(f"  - Enhanced HTML: {results_dir}/reports/enhanced_test_results_display.html")

    return console_log_file

if __name__ == "__main__":
    main()

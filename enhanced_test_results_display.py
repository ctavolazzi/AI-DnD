#!/usr/bin/env python3
"""
Enhanced Test Results Display Generator
Creates a comprehensive HTML report with all generated images and animations displayed
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

ROOT_DIR = Path(__file__).resolve().parent
DASHBOARDS_DIR = ROOT_DIR / "dashboards"

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

def generate_enhanced_html_report(results_dir: Path, json_file: Path):
    """Generate an enhanced HTML report with all images displayed."""

    # Load test results
    with open(json_file, 'r') as f:
        test_data = json.load(f)

    # Find all images
    images = find_all_images(results_dir)
    total_images = sum(len(img_list) for img_list in images.values())

    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelLab Comprehensive Test Results - Enhanced Display</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .timestamp {{
            opacity: 0.8;
            margin-top: 10px;
        }}
        .summary {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .gallery-section {{
            padding: 30px;
        }}
        .gallery-section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        .images-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .image-card {{
            border: 2px solid #ddd;
            border-radius: 12px;
            overflow: hidden;
            background: white;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        .image-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        .image-card img {{
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #f8f9fa;
            padding: 10px;
        }}
        .image-info {{
            padding: 15px;
            background: #f8f9fa;
        }}
        .image-title {{
            font-weight: bold;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        .image-path {{
            font-size: 0.8em;
            color: #666;
            word-break: break-all;
        }}
        .animation-frames {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .animation-frame {{
            border: 1px solid #ddd;
            border-radius: 6px;
            overflow: hidden;
        }}
        .animation-frame img {{
            width: 100%;
            height: 80px;
            object-fit: contain;
        }}
        .suite-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .suite-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .suite-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
        }}
        .suite-content {{
            padding: 20px;
        }}
        .suite-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .suite-stat {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .error-section {{
            background: #fdf2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}
        .error-section h4 {{
            color: #dc2626;
            margin: 0 0 10px 0;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }}
        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            margin-top: 5%;
        }}
        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 PixelLab Comprehensive Test Results</h1>
            <div class="timestamp">{test_data['timestamp']}</div>
            <div style="margin-top: 10px; font-size: 1.2em;">
                📊 {test_data['total_passed']} Passed | {test_data['total_failed']} Failed |
                🖼️ {total_images} Images Generated
            </div>
        </div>

        <div class="summary">
            <h2>📊 Test Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number success">{test_data['total_passed']}</div>
                    <div class="stat-label">Tests Passed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number error">{test_data['total_failed']}</div>
                    <div class="stat-label">Tests Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{test_data['overall_success_rate']:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_images}</div>
                    <div class="stat-label">Images Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{test_data['total_animations_generated']}</div>
                    <div class="stat-label">Animations Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{test_data['total_duration']:.1f}s</div>
                    <div class="stat-label">Total Duration</div>
                </div>
            </div>
        </div>

        <div class="gallery-section">
            <h2>🖼️ Generated Images Gallery</h2>

            <h3>🎭 Character Sprites</h3>
            <div class="images-grid">
"""

    # Add character images
    for img_path in images['characters']:
        img_name = img_path.name
        html_content += f"""
                <div class="image-card" onclick="openModal('../{img_path}')">
                    <img src="../{img_path}" alt="{img_name}" loading="lazy">
                    <div class="image-info">
                        <div class="image-title">{img_name}</div>
                        <div class="image-path">{img_path}</div>
                    </div>
                </div>
"""

    html_content += """
            </div>

            <h3>👤 Basic Characters</h3>
            <div class="images-grid">
"""

    # Add basic character images
    for img_path in images['basic_characters']:
        img_name = img_path.name
        html_content += f"""
                <div class="image-card" onclick="openModal('../{img_path}')">
                    <img src="../{img_path}" alt="{img_name}" loading="lazy">
                    <div class="image-info">
                        <div class="image-title">{img_name}</div>
                        <div class="image-path">{img_path}</div>
                    </div>
                </div>
"""

    html_content += """
            </div>

            <h3>🎬 Sprite Sheets</h3>
            <div class="images-grid">
"""

    # Add sprite sheet images
    for img_path in images['sprite_sheets']:
        img_name = img_path.name
        html_content += f"""
                <div class="image-card" onclick="openModal('../{img_path}')">
                    <img src="../{img_path}" alt="{img_name}" loading="lazy">
                    <div class="image-info">
                        <div class="image-title">{img_name}</div>
                        <div class="image-path">{img_path}</div>
                    </div>
                </div>
"""

    html_content += """
            </div>

            <h3>🎭 Animation Frames</h3>
            <div class="images-grid">
"""

    # Add animation frames
    for img_path in images['animations']:
        img_name = img_path.name
        html_content += f"""
                <div class="image-card" onclick="openModal('../{img_path}')">
                    <img src="../{img_path}" alt="{img_name}" loading="lazy">
                    <div class="image-info">
                        <div class="image-title">{img_name}</div>
                        <div class="image-path">{img_path}</div>
                    </div>
                </div>
"""

    html_content += """
            </div>
        </div>

        <div class="suite-section">
            <h2>🧪 Test Suite Results</h2>
"""

    # Add suite results
    for suite in test_data['suite_results']:
        status_class = "success" if suite['failed_tests'] == 0 else "error"
        html_content += f"""
            <div class="suite-card">
                <div class="suite-header">
                    <span class="{status_class}">{'✓' if suite['failed_tests'] == 0 else '✗'}</span>
                    {suite['suite_name']}
                </div>
                <div class="suite-content">
                    <div class="suite-stats">
                        <div class="suite-stat">
                            <div class="stat-number">{suite['passed_tests']}/{suite['total_tests']}</div>
                            <div class="stat-label">Tests</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite['success_rate']:.1f}%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite['duration_seconds']:.1f}s</div>
                            <div class="stat-label">Duration</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite['generated_images']}</div>
                            <div class="stat-label">Images</div>
                        </div>
                        <div class="suite-stat">
                            <div class="stat-number">{suite['generated_animations']}</div>
                            <div class="stat-label">Animations</div>
                        </div>
                    </div>
"""

        # Add errors if any
        if suite['errors']:
            html_content += f"""
                    <div class="error-section">
                        <h4>⚠️ Errors</h4>
                        <ul>
"""
            for error in suite['errors']:
                html_content += f"<li>{error}</li>"
            html_content += """
                        </ul>
                    </div>
"""

        html_content += """
                </div>
            </div>
"""

    html_content += f"""
        </div>

        <div class="footer">
            <p>Generated by Enhanced PixelLab Test Results Display</p>
            <p>Results saved in: {results_dir}</p>
            <p>Total Images: {total_images} | Total Animations: {test_data['total_animations_generated']}</p>
        </div>
    </div>

    <!-- Modal for image viewing -->
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        function openModal(imagePath) {{
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = "block";
            modalImg.src = imagePath;
        }}

        function closeModal() {{
            document.getElementById('imageModal').style.display = "none";
        }}

        // Close modal when clicking outside the image
        window.onclick = function(event) {{
            const modal = document.getElementById('imageModal');
            if (event.target == modal) {{
                modal.style.display = "none";
            }}
        }}
    </script>
</body>
</html>
"""

    # Save the enhanced HTML report
    enhanced_html_file = results_dir / "reports" / "enhanced_test_results_display.html"
    with open(enhanced_html_file, 'w') as f:
        f.write(html_content)

    return enhanced_html_file


def _collect_run_metadata(run_dir: Path) -> Dict[str, Any] | None:
    json_files = sorted(run_dir.glob("reports/comprehensive_test_results_*.json"))
    if not json_files:
        return None

    with open(json_files[0], "r") as f:
        summary = json.load(f)

    images = find_all_images(run_dir)
    cover_path = None
    for category in ("characters", "basic_characters", "sprite_sheets", "animations"):
        if images[category]:
            cover_path = run_dir / images[category][0]
            break

    reports = []
    enhanced_report = run_dir / "reports" / "enhanced_test_results_display.html"
    if enhanced_report.exists():
        reports.append({
            "label": "Enhanced Report",
            "path": os.path.relpath(enhanced_report, DASHBOARDS_DIR)
        })

    base_report_html = json_files[0].with_suffix(".html")
    if base_report_html.exists():
        reports.append({
            "label": "Summary Report",
            "path": os.path.relpath(base_report_html, DASHBOARDS_DIR)
        })

    cover_rel = None
    if cover_path:
        cover_rel = os.path.relpath(cover_path, DASHBOARDS_DIR)

    return {
        "id": run_dir.name,
        "label": f"Run {run_dir.name.replace('test_results_', '')}",
        "timestamp": summary.get("timestamp"),
        "total_tests": summary.get("total_tests", 0),
        "total_passed": summary.get("total_passed", 0),
        "total_failed": summary.get("total_failed", 0),
        "total_duration": summary.get("total_duration", 0.0),
        "total_images": summary.get("total_images_generated", 0),
        "reports": reports,
        "cover_image": cover_rel,
    }


def write_history_index() -> Path:
    DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)

    runs: List[Dict[str, Any]] = []
    for run_dir in sorted(Path(".").glob("test_results_*"), reverse=True):
        if not run_dir.is_dir():
            continue
        metadata = _collect_run_metadata(run_dir)
        if metadata:
            runs.append(metadata)

    history_payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "runs": runs,
    }

    history_file = DASHBOARDS_DIR / "history.json"
    with open(history_file, "w") as fp:
        json.dump(history_payload, fp, indent=2)

    return history_file


def main():
    """Generate enhanced HTML report with image display."""
    # Find the most recent test results directory
    import glob
    result_dirs = glob.glob("test_results_*")
    if not result_dirs:
        print("❌ No test results directories found")
        return

    # Use the most recent one
    results_dir = Path(sorted(result_dirs)[-1])
    json_files = list(results_dir.glob("reports/comprehensive_test_results_*.json"))
    if not json_files:
        print(f"❌ No JSON results file found in {results_dir}")
        return

    json_file = json_files[0]

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return

    if not json_file.exists():
        print(f"❌ JSON results file not found: {json_file}")
        return

    print("🎨 Generating Enhanced Test Results Display...")
    print(f"📁 Results Directory: {results_dir}")

    # Find all images
    images = find_all_images(results_dir)
    total_images = sum(len(img_list) for img_list in images.values())

    print(f"🖼️ Found {total_images} images:")
    for category, img_list in images.items():
        if img_list:
            print(f"  {category}: {len(img_list)} images")

    # Generate enhanced HTML report
    enhanced_file = generate_enhanced_html_report(results_dir, json_file)
    history_file = write_history_index()

    print(f"✅ Enhanced HTML report generated: {enhanced_file}")
    print(f"🗂  History index updated: {history_file}")
    print(f"🌐 Open in browser: {enhanced_file.absolute()}")

    return enhanced_file

if __name__ == "__main__":
    main()

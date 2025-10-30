#!/usr/bin/env python3
"""
Live Adventure Monitor
Tracks backend server logs, API calls, and performance metrics in real-time
"""

import os
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class AdventureMonitor:
    def __init__(self):
        self.log_dir = Path("logs")
        self.start_time = datetime.now()
        self.metrics = {
            "nano_banana": defaultdict(int),
            "pixellab": defaultdict(int),
            "narrative": defaultdict(int)
        }
        self.api_calls = []
        self.errors = []
        self.images_generated = []

    def parse_log_line(self, line, server):
        """Parse a log line and extract useful information"""
        timestamp_match = re.search(r'\[(\d{2}/\w{3}/\d{4} \d{2}:\d{2}:\d{2})\]', line)
        timestamp = timestamp_match.group(1) if timestamp_match else None

        # Track API calls
        if "POST" in line or "GET" in line:
            method_match = re.search(r'(GET|POST) (/\S+)', line)
            if method_match:
                method, endpoint = method_match.groups()
                status_match = re.search(r'" (\d{3})', line)
                status = int(status_match.group(1)) if status_match else 0

                self.api_calls.append({
                    "server": server,
                    "timestamp": timestamp or datetime.now().isoformat(),
                    "method": method,
                    "endpoint": endpoint,
                    "status": status
                })

                self.metrics[server][f"{method}_{endpoint}"] += 1
                if status >= 200 and status < 300:
                    self.metrics[server]["successful_requests"] += 1
                else:
                    self.metrics[server]["failed_requests"] += 1

        # Track errors
        if "ERROR" in line or "error" in line.lower() or "exception" in line.lower():
            self.errors.append({
                "server": server,
                "timestamp": timestamp or datetime.now().isoformat(),
                "message": line.strip()
            })
            self.metrics[server]["errors"] += 1

        # Track image generation
        if "generate" in line.lower() and ("image" in line.lower() or "sprite" in line.lower()):
            self.images_generated.append({
                "server": server,
                "timestamp": timestamp or datetime.now().isoformat(),
                "details": line.strip()
            })
            self.metrics[server]["images_generated"] += 1

        return line

    def tail_log(self, log_file, server_name):
        """Tail a log file and parse lines"""
        try:
            with open(log_file, 'r') as f:
                # Go to end of file
                f.seek(0, 2)

                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue

                    self.parse_log_line(line, server_name)
                    yield line

        except FileNotFoundError:
            print(f"⚠️  Log file not found: {log_file}")
            return
        except KeyboardInterrupt:
            return

    def check_server_health(self):
        """Check health of all servers"""
        servers = {
            "nano_banana": "http://localhost:5000/health",
            "pixellab": "http://localhost:5001/health",
            "narrative": "http://localhost:5002/health"
        }

        health_status = {}
        for name, url in servers.items():
            try:
                import urllib.request
                response = urllib.request.urlopen(url, timeout=2)
                data = json.loads(response.read())
                health_status[name] = {"status": "healthy", "details": data}
            except Exception as e:
                health_status[name] = {"status": "unhealthy", "error": str(e)}

        return health_status

    def generate_report(self):
        """Generate comprehensive analysis report"""
        duration = (datetime.now() - self.start_time).total_seconds()

        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "test_start": self.start_time.isoformat(),
                "duration_seconds": duration,
                "duration_formatted": f"{duration:.1f}s"
            },
            "server_metrics": dict(self.metrics),
            "api_calls": self.api_calls,
            "errors": self.errors,
            "images_generated": self.images_generated,
            "health_check": self.check_server_health()
        }

        # Calculate aggregated metrics
        total_requests = sum(
            server_metrics.get("successful_requests", 0) + server_metrics.get("failed_requests", 0)
            for server_metrics in self.metrics.values()
        )
        total_errors = sum(
            server_metrics.get("errors", 0)
            for server_metrics in self.metrics.values()
        )
        total_images = sum(
            server_metrics.get("images_generated", 0)
            for server_metrics in self.metrics.values()
        )

        report["aggregated_metrics"] = {
            "total_api_calls": total_requests,
            "total_errors": total_errors,
            "total_images": total_images,
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0
        }

        return report

    def save_report(self, report):
        """Save report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"adventure_analysis_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        # Also create markdown version
        md_filename = f"adventure_analysis_{timestamp}.md"
        self.create_markdown_report(report, md_filename)

        return filename, md_filename

    def create_markdown_report(self, report, filename):
        """Create detailed markdown report"""
        md_content = f"""# 🎭 D&D Narrative Theater - Backend Analysis Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Test Duration:** {report['metadata']['duration_formatted']}
**Test Started:** {report['metadata']['test_start']}

---

## 📊 Aggregated Metrics

| Metric | Value |
|--------|-------|
| Total API Calls | {report['aggregated_metrics']['total_api_calls']} |
| Total Images Generated | {report['aggregated_metrics']['total_images']} |
| Total Errors | {report['aggregated_metrics']['total_errors']} |
| Error Rate | {report['aggregated_metrics']['error_rate']:.2f}% |

---

## 🖥️ Server Health Status

"""
        for server, health in report['health_check'].items():
            status_emoji = "✅" if health['status'] == 'healthy' else "❌"
            md_content += f"### {server.replace('_', ' ').title()} {status_emoji}\n"
            md_content += f"- **Status:** {health['status']}\n"
            if 'details' in health:
                md_content += f"- **Details:** {json.dumps(health['details'], indent=2)}\n"
            if 'error' in health:
                md_content += f"- **Error:** {health['error']}\n"
            md_content += "\n"

        md_content += """---

## 🌐 API Call Breakdown

### By Server

"""
        for server, metrics in report['server_metrics'].items():
            successful = metrics.get('successful_requests', 0)
            failed = metrics.get('failed_requests', 0)
            total = successful + failed
            success_rate = (successful / total * 100) if total > 0 else 0

            md_content += f"""#### {server.replace('_', ' ').title()}
- Total Requests: {total}
- Successful: {successful}
- Failed: {failed}
- Success Rate: {success_rate:.1f}%
- Images Generated: {metrics.get('images_generated', 0)}
- Errors Logged: {metrics.get('errors', 0)}

"""

        md_content += """---

## 📝 Recent API Calls

"""
        for idx, call in enumerate(report['api_calls'][-20:], 1):  # Last 20 calls
            status_emoji = "✅" if 200 <= call['status'] < 300 else "❌"
            md_content += f"""{idx}. {status_emoji} **{call['method']} {call['endpoint']}**
   - Server: {call['server']}
   - Status: {call['status']}
   - Time: {call['timestamp']}

"""

        if report['errors']:
            md_content += """---

## ⚠️ Errors Detected

"""
            for idx, error in enumerate(report['errors'][-10:], 1):  # Last 10 errors
                md_content += f"""{idx}. **{error['server']}** - {error['timestamp']}
   ```
   {error['message']}
   ```

"""

        if report['images_generated']:
            md_content += """---

## 🖼️ Images Generated

"""
            for idx, img in enumerate(report['images_generated'], 1):
                md_content += f"""{idx}. **{img['server']}** - {img['timestamp']}
   - {img['details']}

"""

        md_content += """---

## 🎯 Performance Insights

"""
        # Add insights based on metrics
        insights = []

        agg = report['aggregated_metrics']
        if agg['error_rate'] > 10:
            insights.append(f"⚠️ High error rate detected: {agg['error_rate']:.1f}%")
        elif agg['error_rate'] == 0:
            insights.append("✅ Perfect success rate - no errors detected!")
        else:
            insights.append(f"✅ Low error rate: {agg['error_rate']:.1f}%")

        if agg['total_images'] > 0:
            insights.append(f"🎨 Successfully generated {agg['total_images']} images")
        else:
            insights.append("⚠️ No images were generated during this session")

        duration_sec = report['metadata']['duration_seconds']
        if duration_sec > 60:
            insights.append(f"⏱️ Long session: {duration_sec/60:.1f} minutes")
        else:
            insights.append(f"⏱️ Quick session: {duration_sec:.1f} seconds")

        for insight in insights:
            md_content += f"- {insight}\n"

        md_content += """
---

**Report Complete** ✅

*Generated by Adventure Monitor*
"""

        with open(filename, 'w') as f:
            f.write(md_content)

    def display_live_stats(self):
        """Display live statistics in terminal"""
        os.system('clear' if os.name != 'nt' else 'cls')

        duration = (datetime.now() - self.start_time).total_seconds()

        print("=" * 80)
        print("🎭 D&D NARRATIVE THEATER - LIVE MONITORING 🎲")
        print("=" * 80)
        print(f"Duration: {duration:.1f}s | API Calls: {len(self.api_calls)} | Images: {len(self.images_generated)} | Errors: {len(self.errors)}")
        print("=" * 80)
        print()

        print("📊 SERVER METRICS:")
        for server, metrics in self.metrics.items():
            successful = metrics.get('successful_requests', 0)
            failed = metrics.get('failed_requests', 0)
            total = successful + failed
            print(f"  {server.upper():<15} | Requests: {total:>3} | Success: {successful:>3} | Failed: {failed:>2} | Images: {metrics.get('images_generated', 0):>2}")

        print()
        print("🌐 RECENT API CALLS (last 5):")
        for call in self.api_calls[-5:]:
            status_emoji = "✅" if 200 <= call['status'] < 300 else "❌"
            print(f"  {status_emoji} {call['method']:>4} {call['endpoint']:<30} [{call['status']}] - {call['server']}")

        if self.errors:
            print()
            print("⚠️  RECENT ERRORS:")
            for error in self.errors[-3:]:
                print(f"  ❌ [{error['server']}] {error['message'][:70]}")

        print()
        print("=" * 80)
        print("Press Ctrl+C to stop monitoring and generate report")
        print("=" * 80)


def main():
    """Main monitoring loop"""
    print("🎭 Starting Live Adventure Monitor...")
    print("⏳ Waiting for log activity...")
    print()

    monitor = AdventureMonitor()

    # Check if logs exist
    log_dir = Path("logs")
    if not log_dir.exists():
        print("⚠️  Logs directory not found. Make sure servers are running!")
        return

    log_files = {
        "nano_banana": log_dir / "nano_banana.log",
        "pixellab": log_dir / "pixellab_bridge.log",
        "narrative": log_dir / "narrative_server.log"
    }

    # Check which logs exist
    existing_logs = {name: path for name, path in log_files.items() if path.exists()}
    if not existing_logs:
        print("⚠️  No log files found. Start the servers with ./start_theater.sh")
        return

    print(f"📝 Monitoring {len(existing_logs)} log files:")
    for name in existing_logs:
        print(f"  - {name}")
    print()

    try:
        # Monitor in background (this is a simplified version)
        # In a real implementation, you'd want to use threading or multiprocessing
        import threading

        def monitor_log(log_file, server_name):
            for line in monitor.tail_log(log_file, server_name):
                pass  # Processing happens in tail_log

        threads = []
        for name, log_file in existing_logs.items():
            thread = threading.Thread(target=monitor_log, args=(log_file, name), daemon=True)
            thread.start()
            threads.append(thread)

        # Display stats every 2 seconds
        while True:
            time.sleep(2)
            monitor.display_live_stats()

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping monitor...")
        print("📊 Generating comprehensive report...")

        report = monitor.generate_report()
        json_file, md_file = monitor.save_report(report)

        print(f"\n✅ Reports generated:")
        print(f"   - {json_file} (JSON data)")
        print(f"   - {md_file} (Markdown report)")
        print("\n🎉 Monitoring complete!")


if __name__ == "__main__":
    main()




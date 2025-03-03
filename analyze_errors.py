#!/usr/bin/env python3
"""
Error Log Analyzer for AI-DnD

This script parses error logs and presents them in a more readable format,
helping to quickly identify and diagnose issues in the AI-DnD application.

The analyzer provides several features:
- Parsing error logs to extract structured information
- Grouping similar errors to identify patterns
- Generating statistics about error frequency and distribution
- Formatting error details for easy reading
- Filtering errors by type, file, or recency

Usage:
    python3 analyze_errors.py [options]

Options:
    --log-dir DIR         Directory containing log files (default: logs)
    --output FILE         Output file for analysis (default: stdout)
    --format FORMAT       Output format: text or json (default: text)
    --detailed            Show detailed error information
    --most-recent N       Show only the N most recent errors
    --error-type TYPE     Filter by error type
    --file-name NAME      Filter by file name

Examples:
    python3 analyze_errors.py --log-dir=logs --detailed
    python3 analyze_errors.py --most-recent=5 --format=json
"""
import os
import re
import sys
import argparse
import glob
from typing import Dict, List, Any, Optional
from collections import Counter
import datetime
import json


def parse_error_log(log_file: str) -> List[Dict[str, Any]]:
    """
    Parse an error log file and extract error information.

    This function reads an error log file and extracts structured information
    about each error, including timestamps, error messages, exception types,
    file and line information, context, and stack traces.

    Args:
        log_file: Path to the error log file

    Returns:
        List of dictionaries, each containing information about a single error
    """
    print(f"Parsing error log: {log_file}")
    errors = []
    current_error = None
    traceback_lines = []

    with open(log_file, 'r') as f:
        for line in f:
            # New error entry starts with timestamp and ERROR level
            if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - .+ - ERROR - ', line):
                # If we were collecting a traceback, add it to the current error
                if current_error and traceback_lines:
                    current_error['traceback'] = ''.join(traceback_lines)
                    traceback_lines = []

                # If previous error is fully processed, add to errors list
                if current_error:
                    errors.append(current_error)

                # Start new error record
                timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                    message = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - .+ - ERROR - ', '', line).strip()

                    current_error = {
                        'timestamp': timestamp,
                        'message': message,
                        'context': {},
                        'traceback': ''
                    }

                    # Extract error information
                    if message.startswith('Exception:'):
                        current_error['type'] = 'exception'
                        current_error['exception'] = message.replace('Exception:', '').strip()
                    elif message.startswith('Error:'):
                        current_error['type'] = 'error'
                        current_error['error'] = message.replace('Error:', '').strip()
                    elif message.startswith('Exception Type:'):
                        if current_error:
                            current_error['exception_type'] = message.replace('Exception Type:', '').strip()
                    elif message.startswith('Raised in file:'):
                        if current_error:
                            current_error['file'] = message.replace('Raised in file:', '').strip()
                    elif message.startswith('Raised in function:'):
                        if current_error:
                            current_error['function'] = message.replace('Raised in function:', '').strip()
                    elif message.startswith('Raised on line:'):
                        if current_error:
                            current_error['line'] = message.replace('Raised on line:', '').strip()
                    elif message.startswith('Context:'):
                        if current_error:
                            context_str = message.replace('Context:', '').strip()
                            try:
                                current_error['context'] = eval(context_str)
                            except:
                                current_error['context'] = {'raw': context_str}
                    elif message.startswith('Traceback:'):
                        # Start collecting traceback lines
                        traceback_start = True
                    elif current_error and current_error.get('type') is None:
                        # General error message
                        current_error['type'] = 'general'
                        current_error['error'] = message

            # Continuation of traceback
            elif current_error and line.strip():
                traceback_lines.append(line)

    # Add the last error if there is one
    if current_error:
        if traceback_lines:
            current_error['traceback'] = ''.join(traceback_lines)
        errors.append(current_error)

    print(f"Found {len(errors)} errors in {log_file}")
    return errors


def group_errors(errors: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group errors by type and file.

    This function groups similar errors together to help identify patterns.
    Errors are grouped by exception type or error message.

    Args:
        errors: List of error records

    Returns:
        Dictionary mapping error types to lists of error records
    """
    print(f"Grouping {len(errors)} errors by type and message")
    grouped = {}

    # Group by exception type / error message
    for error in errors:
        key = None
        if error.get('type') == 'exception' and error.get('exception_type'):
            key = error['exception_type']
        elif error.get('error'):
            # Simplify the error message for grouping
            key = re.sub(r'[0-9]', '#', error['error'])
            key = re.sub(r'".+"', '"..."', key)
            key = key[:50]  # Truncate long messages

        if key:
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(error)

    print(f"Grouped errors into {len(grouped)} categories")
    return grouped


def analyze_errors(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze errors and produce statistics.

    This function analyzes a list of error records and produces statistics
    about error frequency, distribution by type and location, and timing.

    Args:
        errors: List of error records

    Returns:
        Dictionary containing error statistics
    """
    print(f"Analyzing {len(errors)} errors")
    stats = {
        'total_errors': len(errors),
        'error_types': Counter(),
        'error_files': Counter(),
        'error_functions': Counter(),
        'first_error_time': None,
        'last_error_time': None,
    }

    for error in errors:
        # Count error types
        error_type = error.get('type', 'unknown')
        if error_type == 'exception' and error.get('exception_type'):
            error_type = error['exception_type']
        stats['error_types'][error_type] += 1

        # Count files
        if error.get('file'):
            # Extract just the filename, not the full path
            filename = os.path.basename(error['file'])
            stats['error_files'][filename] += 1

        # Count functions
        if error.get('function'):
            stats['error_functions'][error['function']] += 1

        # Track error timestamps
        if error.get('timestamp'):
            try:
                ts = datetime.datetime.strptime(
                    error['timestamp'].split(',')[0],
                    '%Y-%m-%d %H:%M:%S'
                )
                if stats['first_error_time'] is None or ts < stats['first_error_time']:
                    stats['first_error_time'] = ts
                if stats['last_error_time'] is None or ts > stats['last_error_time']:
                    stats['last_error_time'] = ts
            except:
                pass

    # Format timestamps
    if stats['first_error_time']:
        stats['first_error_time'] = stats['first_error_time'].strftime('%Y-%m-%d %H:%M:%S')
    if stats['last_error_time']:
        stats['last_error_time'] = stats['last_error_time'].strftime('%Y-%m-%d %H:%M:%S')

    # Convert counters to dict for JSON serialization
    stats['error_types'] = dict(stats['error_types'])
    stats['error_files'] = dict(stats['error_files'])
    stats['error_functions'] = dict(stats['error_functions'])

    print(f"Analysis complete: {stats['total_errors']} errors across {len(stats['error_files'])} files")
    return stats


def format_error_for_display(error: Dict[str, Any]) -> str:
    """
    Format an error for display.

    This function formats an error record as a human-readable string,
    including all available information about the error.

    Args:
        error: Error record

    Returns:
        Formatted error string
    """
    lines = []

    if error.get('timestamp'):
        lines.append(f"Time: {error['timestamp']}")

    if error.get('type') == 'exception':
        lines.append(f"Exception: {error.get('exception', 'Unknown')}")
        if error.get('exception_type'):
            lines.append(f"Type: {error['exception_type']}")
    else:
        lines.append(f"Error: {error.get('error', 'Unknown')}")

    if error.get('file'):
        lines.append(f"File: {error['file']}")

    if error.get('function'):
        lines.append(f"Function: {error['function']}")

    if error.get('line'):
        lines.append(f"Line: {error['line']}")

    if error.get('context') and error['context']:
        lines.append("Context:")
        for k, v in error['context'].items():
            lines.append(f"  {k}: {v}")

    if error.get('traceback'):
        lines.append("\nTraceback:")
        lines.append(error['traceback'])

    return '\n'.join(lines)


def main():
    """
    Main entry point for the error analyzer.

    This function parses command-line arguments, reads error logs,
    analyzes errors, and outputs the results in the requested format.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(description='Analyze AI-DnD error logs')
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Directory containing log files')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file for analysis (default: stdout)')
    parser.add_argument('--format', type=str, choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--detailed', action='store_true',
                        help='Show detailed error information')
    parser.add_argument('--most-recent', type=int, default=0,
                        help='Show only the N most recent errors')
    parser.add_argument('--error-type', type=str, default=None,
                        help='Filter by error type')
    parser.add_argument('--file-name', type=str, default=None,
                        help='Filter by file name')
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"AI-DnD Error Log Analyzer")
    print(f"{'='*60}\n")

    # Find error log files
    log_files = glob.glob(os.path.join(args.log_dir, 'ai_dnd_errors_*.log'))

    if not log_files:
        print(f"No error log files found in {args.log_dir}")
        return 1

    print(f"Found {len(log_files)} error log files in {args.log_dir}")

    # Parse all log files
    all_errors = []
    for log_file in log_files:
        all_errors.extend(parse_error_log(log_file))

    if not all_errors:
        print("No errors found in log files")
        return 0

    # Sort errors by timestamp (most recent last)
    all_errors.sort(key=lambda e: e.get('timestamp', ''))

    # Apply filters
    filtered_errors = all_errors

    if args.error_type:
        print(f"Filtering errors by type: {args.error_type}")
        filtered_errors = [
            e for e in filtered_errors
            if (e.get('type') == 'exception' and e.get('exception_type') == args.error_type) or
               (e.get('error') and args.error_type.lower() in e.get('error').lower())
        ]

    if args.file_name:
        print(f"Filtering errors by file name: {args.file_name}")
        filtered_errors = [
            e for e in filtered_errors
            if e.get('file') and args.file_name.lower() in e.get('file').lower()
        ]

    # Limit to most recent if requested
    if args.most_recent > 0:
        print(f"Limiting to {args.most_recent} most recent errors")
        filtered_errors = filtered_errors[-args.most_recent:]

    print(f"Analyzing {len(filtered_errors)} errors after filtering")

    # Group errors
    grouped_errors = group_errors(filtered_errors)

    # Analyze errors
    stats = analyze_errors(filtered_errors)

    # Prepare output
    output = ""

    if args.format == 'text':
        # Summary stats
        output += f"=== AI-DnD Error Analysis ===\n\n"
        output += f"Total Errors: {stats['total_errors']}\n"
        output += f"Time Range: {stats['first_error_time']} to {stats['last_error_time']}\n\n"

        output += "Error Types:\n"
        for t, count in sorted(stats['error_types'].items(), key=lambda x: x[1], reverse=True):
            output += f"  {t}: {count}\n"

        output += "\nFiles with Errors:\n"
        for f, count in sorted(stats['error_files'].items(), key=lambda x: x[1], reverse=True):
            output += f"  {f}: {count}\n"

        output += "\nFunctions with Errors:\n"
        for f, count in sorted(stats['error_functions'].items(), key=lambda x: x[1], reverse=True):
            output += f"  {f}: {count}\n"

        # Detailed error information if requested
        if args.detailed:
            output += "\n\n=== Detailed Error Information ===\n\n"

            for i, (error_type, errors) in enumerate(
                sorted(grouped_errors.items(), key=lambda x: len(x[1]), reverse=True)
            ):
                output += f"\n[Group {i+1}] {error_type} ({len(errors)} occurrences)\n"
                output += "-" * 50 + "\n"
                # Show the most recent error of this type
                output += format_error_for_display(errors[-1])
                output += "\n" + "=" * 50 + "\n"

    elif args.format == 'json':
        result = {
            'stats': stats,
            'errors': filtered_errors if args.detailed else [],
            'grouped': {k: len(v) for k, v in grouped_errors.items()}
        }
        output = json.dumps(result, indent=2)

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Analysis written to {args.output}")
    else:
        print(output)

    print(f"\n{'='*60}")
    print(f"Analysis complete")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
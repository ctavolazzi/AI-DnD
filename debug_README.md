# Debugging AI-DnD

This document provides comprehensive guidance on debugging issues in the AI-DnD codebase.

## Table of Contents

1. [Enhanced Error Logging](#enhanced-error-logging)
2. [Running with Enhanced Debugging](#running-with-enhanced-debugging)
3. [Analyzing Errors Manually](#analyzing-errors-manually)
4. [Common Issues and Solutions](#common-issues-and-solutions)
5. [Error Log Files](#error-log-files)
6. [Manually Adding Error Context](#manually-adding-error-context)
7. [Debugging Specific Components](#debugging-specific-components)
8. [Troubleshooting Guide](#troubleshooting-guide)

## Enhanced Error Logging

The codebase includes an enhanced error logging system that provides detailed information about errors, including:

- Exception types and messages
- File and line numbers where errors occurred
- Function names where errors were raised
- Contextual information about the error
- Full stack traces

This system is implemented in `error_logger.py` and provides both a class-based API and convenience functions for logging errors.

## Running with Enhanced Debugging

To run the game with enhanced debugging and error analysis:

```bash
./debug_run_game.sh
```

This script will:
1. Create a logs directory if it doesn't exist
2. Clear previous log files
3. Run the game with verbose output
4. Check for errors in the logs
5. Run the error analyzer if errors are found
6. Check for common issues related to locations and characters

### Additional Options

You can also run the game directly with various options:

```bash
# Run with verbose output
python3 main.py --verbose

# Force an error to test error logging
python3 main.py --force-error

# Run with a specific model and turn count
python3 main.py --model=mistral --turns=10 --verbose
```

## Analyzing Errors Manually

You can analyze error logs at any time using the `analyze_errors.py` script:

```bash
# Basic analysis
./analyze_errors.py --log-dir=logs

# Detailed analysis with full error information
./analyze_errors.py --log-dir=logs --detailed

# Show only the 5 most recent errors
./analyze_errors.py --log-dir=logs --most-recent=5

# Filter errors by type
./analyze_errors.py --log-dir=logs --error-type="AttributeError"

# Filter errors by file name
./analyze_errors.py --log-dir=logs --file-name="dungeon_master.py"

# Output analysis to a file
./analyze_errors.py --log-dir=logs --output=error_analysis.txt

# Output analysis as JSON
./analyze_errors.py --log-dir=logs --format=json --output=error_analysis.json
```

The analyzer provides several features:
- Parsing error logs to extract structured information
- Grouping similar errors to identify patterns
- Generating statistics about error frequency and distribution
- Formatting error details for easy reading
- Filtering errors by type, file, or recency

## Common Issues and Solutions

### Character Information Not Appearing in Location Files

If characters are not showing up in location files, check the following:

1. Make sure `handle_character_movement` is correctly updating the relationships between characters and locations.
2. Verify that the `log_location` method in `obsidian_logger.py` is including character information in the location file.
3. Ensure that `process_location_change` is updating both the old and new location files with correct character lists.

**Solution**: The `log_location` method has been updated to include a "characters" field in the location context, and `process_location_change` now updates both the old and new location files with the correct character lists.

### Game Errors at End of Run

If the game is completing with errors, check the logs directory for detailed error information:

```bash
./analyze_errors.py --log-dir=logs --detailed --most-recent=1
```

Common causes:
- Missing initialization of game objects
- Errors in narrative generation
- Issues with relationships between characters and locations

**Solution**: The error logging system now provides detailed information about errors, making it easier to diagnose and fix issues.

### Obsidian Vault Not Found

If you see an error about the Obsidian vault not being found, you can create it with:

```bash
python3 main.py --reset --vault=character-journal-test-vault
```

## Error Log Files

Error logs are stored in the `logs` directory:
- General logs: `logs/ai_dnd_YYYYMMDD.log`
- Error-specific logs: `logs/ai_dnd_errors_YYYYMMDD.log`

These files contain timestamped entries with detailed error information.

### Log Format

Error logs follow this format:

```
TIMESTAMP - LOGGER_NAME - ERROR - Exception: ERROR_MESSAGE
TIMESTAMP - LOGGER_NAME - ERROR - Exception Type: ERROR_TYPE
TIMESTAMP - LOGGER_NAME - ERROR - Raised in file: FILE_PATH
TIMESTAMP - LOGGER_NAME - ERROR - Raised in function: FUNCTION_NAME
TIMESTAMP - LOGGER_NAME - ERROR - Raised on line: LINE_NUMBER
TIMESTAMP - LOGGER_NAME - ERROR - Context: CONTEXT_DICT
TIMESTAMP - LOGGER_NAME - ERROR - Traceback:
TRACEBACK_TEXT
```

## Manually Adding Error Context

When debugging specific issues, you can use the `error_logger.py` module to add custom error handling:

```python
from error_logger import log_exception, log_error

try:
    # Your code here
except Exception as e:
    log_exception(e, {
        "context": "What was happening",
        "important_variable": some_var
    })
```

You can also log errors without exceptions:

```python
from error_logger import log_error

if some_condition_is_wrong:
    log_error("Something is wrong", {
        "condition": some_condition,
        "expected": expected_value,
        "actual": actual_value
    })
```

## Debugging Specific Components

### Dungeon Master

The `DungeonMaster` class is the central controller for the game. Common issues include:

- Initialization errors: Check that the vault path exists and is accessible
- Game loop errors: Check that the game is properly initialized before running
- Event handling errors: Check that events are properly formatted

### Obsidian Logger

The `ObsidianLogger` class handles writing game data to the Obsidian vault. Common issues include:

- File access errors: Check that the vault path exists and is writable
- Template rendering errors: Check that templates exist and are properly formatted
- Data format errors: Check that data passed to logging methods is properly structured

### Game Manager

The `GameManager` class manages game state and relationships. Common issues include:

- Relationship errors: Check that relationships between entities are properly defined
- Knowledge graph errors: Check that the knowledge graph is properly updated
- Event handling errors: Check that events are properly processed

## Troubleshooting Guide

### Step 1: Identify the Error

Run the game with the debug script:

```bash
./debug_run_game.sh
```

Look at the error analysis output to identify the error type, location, and context.

### Step 2: Examine the Code

Once you know where the error is occurring, examine the code in that file and function.

### Step 3: Check the Context

Look at the context information in the error log to understand what was happening when the error occurred.

### Step 4: Fix the Issue

Make the necessary changes to fix the issue.

### Step 5: Test the Fix

Run the game again to verify that the issue is fixed:

```bash
./debug_run_game.sh
```

### Step 6: Update Documentation

If you've fixed a common issue, update this document with information about the issue and its solution.
#!/usr/bin/env python3
"""
Error Logging Utilities for AI-DnD

This module provides enhanced error logging capabilities for the AI-DnD project.
It includes a class for logging detailed error information, including file and line
numbers, function names, contextual information, and stack traces.

The module is designed to make debugging easier by providing rich error context
and analysis tools. It creates dedicated log files for errors and provides
utility functions for logging exceptions and error messages.

Example usage:
    from error_logger import log_exception, log_error

    try:
        # Code that might raise an exception
        result = risky_operation()
    except Exception as e:
        log_exception(e, {"context": "Operation X", "input_data": input_value})
"""
import os
import sys
import logging
import traceback
import inspect
from typing import Dict, List, Any, Optional, Union
import datetime


class ErrorLogger:
    """
    Enhanced error logging utilities for the AI-DnD project.

    This class provides methods for logging detailed error information, including
    file and line numbers, function names, contextual information, and stack traces.
    It creates dedicated log files for errors and ensures that error information
    is consistently formatted and comprehensive.

    Attributes:
        logger (logging.Logger): The logger instance used for logging errors
    """

    def __init__(self, logger_name: str = "ai_dnd.error"):
        """
        Initialize the error logger.

        Args:
            logger_name: Name for the logger instance
        """
        self.logger = logging.getLogger(logger_name)

        # Set up logger if it hasn't been configured yet
        if not self.logger.handlers:
            self.setup_logging()

        self.logger.debug(f"ErrorLogger initialized with name '{logger_name}'")

    def setup_logging(self, log_dir: str = "logs"):
        """
        Set up logging configuration.

        This method configures the logging system to write logs to both console
        and files. It creates a general log file and a dedicated error log file.

        Args:
            log_dir: Directory to store log files
        """
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create a formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Set up console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        # Set up file handler for all logs
        log_file = os.path.join(
            log_dir, f"ai_dnd_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Set up file handler for errors only
        error_log_file = os.path.join(
            log_dir, f"ai_dnd_errors_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        )
        error_file_handler = logging.FileHandler(error_log_file)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_file_handler)
        self.logger.setLevel(logging.INFO)

        self.logger.debug(f"Logging configured: general log at {log_file}, error log at {error_log_file}")

    def log_exception(self, e: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log an exception with enhanced context.

        This method logs an exception with detailed information about where it occurred,
        including file and line numbers, function names, and contextual information.
        It also logs the full stack trace.

        Args:
            e: The exception to log
            context: Additional context to include in the log

        Returns:
            Dict containing detailed error information
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # Get exception traceback as a string
        traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # Get calling frame info
        caller_frame = inspect.currentframe().f_back
        caller_file = caller_frame.f_code.co_filename
        caller_function = caller_frame.f_code.co_name
        caller_line = caller_frame.f_lineno

        # Log detailed exception information
        self.logger.error(f"Exception: {e}")
        self.logger.error(f"Exception Type: {exc_type.__name__}")
        self.logger.error(f"Raised in file: {caller_file}")
        self.logger.error(f"Raised in function: {caller_function}")
        self.logger.error(f"Raised on line: {caller_line}")

        # Log additional context if provided
        if context:
            self.logger.error(f"Context: {context}")

        # Log traceback
        self.logger.error(f"Traceback:\n{traceback_str}")

        # Create error details dictionary
        error_details = {
            "error": str(e),
            "error_type": exc_type.__name__,
            "file": caller_file,
            "function": caller_function,
            "line": caller_line,
            "traceback": traceback_str,
            "context": context
        }

        self.logger.debug(f"Exception logged with details: {error_details['error_type']} in {error_details['file']}")
        return error_details

    def log_error(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log an error message with enhanced context.

        This method logs an error message with detailed information about where it was
        logged, including file and line numbers, function names, and contextual information.

        Args:
            message: Error message to log
            context: Additional context to include in the log

        Returns:
            Dict containing detailed error information
        """
        # Get calling frame info
        caller_frame = inspect.currentframe().f_back
        caller_file = caller_frame.f_code.co_filename
        caller_function = caller_frame.f_code.co_name
        caller_line = caller_frame.f_lineno

        # Log detailed error information
        self.logger.error(f"Error: {message}")
        self.logger.error(f"Raised in file: {caller_file}")
        self.logger.error(f"Raised in function: {caller_function}")
        self.logger.error(f"Raised on line: {caller_line}")

        # Log additional context if provided
        if context:
            self.logger.error(f"Context: {context}")

        # Create error details dictionary
        error_details = {
            "error": message,
            "file": caller_file,
            "function": caller_function,
            "line": caller_line,
            "context": context
        }

        self.logger.debug(f"Error logged: {message[:50]}...")
        return error_details


# Singleton instance for easy import
error_logger = ErrorLogger()


def log_exception(e: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to log an exception with enhanced context.

    This function forwards the call to the singleton ErrorLogger instance.
    It's provided for ease of use so that callers don't need to instantiate
    an ErrorLogger themselves.

    Args:
        e: The exception to log
        context: Additional context to include in the log

    Returns:
        Dict containing detailed error information
    """
    return error_logger.log_exception(e, context)


def log_error(message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to log an error message with enhanced context.

    This function forwards the call to the singleton ErrorLogger instance.
    It's provided for ease of use so that callers don't need to instantiate
    an ErrorLogger themselves.

    Args:
        message: Error message to log
        context: Additional context to include in the log

    Returns:
        Dict containing detailed error information
    """
    return error_logger.log_error(message, context)
"""
This module provides a summary of all classes and their purposes in the utils folder.

Classes:
    ENVParser: Parses environment variables and configuration settings for the application.
    _AnsiColorizer: A colorizer that wraps around a stream, allowing text to be written in a particular color.
    ColorHandler: A logging handler that outputs log messages to a stream with colorized text.

Functions:
    singleton: A decorator to implement the singleton pattern for a class.
    __delete_oldest_logs: Deletes the oldest log files in the specified folder, keeping only the most recent ones.
    initialize_logger: Initializes the logger with colorized console output and file logging.
"""
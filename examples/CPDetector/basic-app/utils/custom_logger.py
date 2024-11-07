import logging
import os
import sys
from datetime import datetime
from os.path import join

from utils.parser import ENVParser
from utils.singleton import singleton


@singleton
class _AnsiColorizer(object):
    """
    A colorizer is an object that loosely wraps around a stream, allowing
    callers to write text to the stream in a particular color.

    Colorizer classes must implement `supported()` and `write(text, color)`.

    Attributes:
        stream (io.TextIOWrapper): The stream to which the colorized text is written.
    """
    _colors = dict(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37)

    def __init__(self, stream):
        """
        Initializes the _AnsiColorizer with the given stream.

        Args:
            stream (io.TextIOWrapper): The stream to which the colorized text is written.
        """
        self.stream = stream

    @classmethod
    def supported(cls, stream=sys.stdout) -> bool:
        """
        Returns True if the current platform supports coloring terminal output using this method.

        Args:
            stream (io.TextIOWrapper): The stream to check for color support.

        Returns:
            bool: True if the platform supports coloring terminal output, False otherwise.
        """
        if not stream.isatty():
            return False  # auto color only on TTYs
        try:
            import curses
        except ImportError:
            return False
        else:
            try:
                try:
                    return curses.tigetnum("colors") > 2
                except curses.error:
                    curses.setupterm()
                    return curses.tigetnum("colors") > 2
            except:
                return False

    def write(self, text: str, color:str):
        """
        Write the given text to the stream in the given color.

        Args:
            text (str): Text to be written to the stream.
            color (str): A string label for a color. e.g. 'red', 'white'.
        """
        color = self._colors[color]
        self.stream.write('\x1b[%s;1m%s\x1b[0m' % (color, text))


class ColorHandler(logging.StreamHandler):
    """
    A logging handler that outputs log messages to a stream with colorized text.

    Attributes:
        stream (io.TextIOWrapper): The stream to which the colorized log messages are written.
    """
    def __init__(self, stream=sys.stderr):
        """
        Initializes the ColorHandler with the given stream.

        Args:
            stream (io.TextIOWrapper): The stream to which the colorized log messages are written.
        """
        super(ColorHandler, self).__init__(_AnsiColorizer(stream))

    def emit(self, record: logging.LogRecord):
        """
        Emit a record.

        Writes the log record to the stream with colorized text based on the log level.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        msg_colors = {
            logging.DEBUG: "green",
            logging.INFO: "blue",
            logging.WARNING: "yellow",
            logging.ERROR: "red"
        }

        timestamp = "{:%m/%d/%Y %H:%M:%S}".format(datetime.now())
        color = msg_colors.get(record.levelno, "blue")
        self.stream.write(
            "{} [{}] : {} ({}:{})\n".format(timestamp, record.levelname, record.msg, record.filename, record.lineno),
            color)


def __delete_oldest_logs(folder: str , logs_to_keep: int=10):
    """
    Delete the oldest log files in the specified folder, keeping only the most recent ones.

    Args:
        folder (str): The folder containing the log files.
        logs_to_keep (int): The number of most recent log files to keep.
    """
    files = sorted(os.listdir(folder), reverse=True)
    for file_name in files[logs_to_keep:]:
        file = join(folder, file_name)
        if os.path.isfile(file):
            logging.debug(f'Deleting file: {file}')
            os.remove(file)


def initialize_logger() -> str:
    """
    Initialize the logger with colorized console output and file logging.

    Sets the log level and handlers based on environment variables.

    Returns:
        str: The path to the log file.
    """
    env = ENVParser()
    logging.getLogger().setLevel(env.log_mode)
    logging.getLogger().addHandler(ColorHandler())

    folder = env.log_path
    os.makedirs(folder, exist_ok=True)
    log_path = join(folder, f"logfile-{datetime.today().strftime('%Y%m%d%H%M')}.log")
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s (%(filename)s:%(lineno)d)',
                                      datefmt='%m/%d/%Y %H:%M:%S')
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(file_handler)

    __delete_oldest_logs(folder=folder, logs_to_keep=20)

    return log_path


if __name__ == "__main__":
    logging.debug("Some debugging output")
    logging.info("Some info output")
    logging.error("Some error output")
    logging.warning("Some warning output")
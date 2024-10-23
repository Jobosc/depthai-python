import logging
import os
import sys
from datetime import datetime
from os.path import join

from utils.decorators import singleton


@singleton
class _AnsiColorizer(object):
    """
    A colorizer is an object that loosely wraps around a stream, allowing
    callers to write text to the stream in a particular color.

    Colorizer classes must implement C{supported()} and C{write(text, color)}.
    """
    _colors = dict(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37)

    def __init__(self, stream):
        self.stream = stream

    @classmethod
    def supported(cls, stream=sys.stdout):
        """
        A class method that returns True if the current platform supports
        coloring terminal output using this method. Returns False otherwise.
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
                raise
                # guess false in case of error
                return False

    def write(self, text, color):
        """
        Write the given text to the stream in the given color.

        @param text: Text to be written to the stream.

        @param color: A string label for a color. e.g. 'red', 'white'.
        """
        color = self._colors[color]
        self.stream.write('\x1b[%s;1m%s\x1b[0m' % (color, text))


class ColorHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stderr):
        super(ColorHandler, self).__init__(_AnsiColorizer(stream))

    def emit(self, record):
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


def __delete_oldest_logs(folder, logs_to_keep=10):
    files = sorted(os.listdir(folder), reverse=True)
    for file_name in files[logs_to_keep:]:
        file = join(folder, file_name)
        if os.path.isfile(file):
            logging.debug(f'Deleting file: {file}')
            os.remove(file)


def initialize_logger():
    logging.getLogger().setLevel("debug")
    logging.getLogger().addHandler(ColorHandler())

    folder = "logs"
    os.makedirs(folder, exist_ok=True)
    log_path = join(folder, f"logfile-{datetime.today().strftime('%Y%m%d%H%M')}.log")
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s (%(filename)s:%(lineno)d)',
                                     datefmt='%m/%d/%Y %H:%M:%S')
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(file_handler)

    __delete_oldest_logs(folder=folder)

    return log_path


if __name__ == "__main__":
    logging.debug("Some debugging output")
    logging.info("Some info output")
    logging.error("Some error output")
    logging.warning("Some warning output")

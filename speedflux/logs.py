import logging
import sys


class Log:
    def __init__(
            self,
            config,
            log_format="%(asctime)s [%(levelname)s] %(message)s"):
        self.log_format = log_format
        self.log_type = config.LOG_TYPE
        self._log_level = None
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging once at startup."""
        # Determine log level
        log_opt = {'info': logging.INFO, 'debug': logging.DEBUG, 'error': logging.ERROR}
        level = log_opt.get(self.log_type, logging.INFO)

        # Store internal level for compatibility
        level_map = {'info': 3, 'debug': 5, 'error': 1}
        self._log_level = level_map.get(self.log_type, 3)

        # Configure logging once
        logging.basicConfig(
            level=level,
            format=self.log_format,
            handlers=[logging.StreamHandler(sys.stdout)],
            force=True  # Override any existing config
        )

        # Announce logging level
        if self._log_level == 5:
            logging.info("Debug logging is enabled.")
        else:
            logging.info("Logging is set to info only. Set LOG_TYPE=debug for verbose output.")

    @property
    def log_level(self):
        return self._log_level

    def info(self, msg):
        if self.log_level >= 3:
            logging.info(msg)

    def debug(self, msg):
        if self.log_level >= 5:
            logging.debug(msg)

    def error(self, msg):
        if self.log_level >= 1:
            logging.error(msg)

    def warning(self, msg):
        if self.log_level >= 2:
            logging.warning(msg)

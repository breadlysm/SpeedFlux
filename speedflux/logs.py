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
        self.announce_logging()

    @property
    def log_level(self):
        if self._log_level is None:
            try:
                log_opt = {'info': 3, 'debug': 5, 'error': 1}
                self._log_level = log_opt[self.log_type]
            except KeyError:
                self.error(
                    "Value inputted as LOG_TYPE is not one of \
                        ['info', 'debug']. Setting to info only\
                        but, please fix your config.")
                self._log_level = 3
        return self._log_level

    def announce_logging(self):
        if self._log_level == 3:
            self.info(
                "Logging is set to info only. No debug logs will be recorded")
        elif self._log_level == 5:
            self.info("Debug logging is enabled.")

    def info(self, msg):
        logging.basicConfig(
            level=logging.INFO,
            format=self.log_format,
            handlers=[
                # logging.FileHandler("log.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        if self.log_level >= 3:
            logging.info(msg)

    def debug(self, msg):
        logging.basicConfig(
            level=logging.DEBUG,
            format=self.log_format,
            handlers=[
                # logging.FileHandler("debug.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        if self.log_level >= 5:
            logging.debug(msg)

    def error(self, msg):
        logging.basicConfig(
            level=logging.ERROR,
            format=self.log_format,
            handlers=[
                # logging.FileHandler("log.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        if self.log_level >= 1:
            logging.error(msg)

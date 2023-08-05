import inspect
import logging
import logging.handlers
import os
import platform
import sys
import traceback
import onesaitplatform.common.config as config

try:
    default_dir = ".onesaitplatform"
    if config.LOG_FOLDER:
        d = os.path.join(config.LOG_FOLDER, default_dir)
    else:
        d = os.path.join(os.path.expanduser("~"), default_dir)

    try:
        if not os.path.exists(d):
            os.mkdir(d)
    except:
        d = default_dir
        if not os.path.exists(d):
            os.mkdir(d)

finally:
    log_file_path = os.path.join(d, "onesaitplatform-python-client.log")


class log(object):

    handler = None
    plugin_id = "onesaitplatform-python-client"

    @staticmethod
    def error(text):
        logger = logging.getLogger(log.plugin_id)
        logger.error(text)

    @staticmethod
    def info(text):
        logger = logging.getLogger(log.plugin_id)
        logger.info(text)

    @staticmethod
    def warning(text):
        logger = logging.getLogger(log.plugin_id)
        logger.warning(text)

    @staticmethod
    def debug(text):
        logger = logging.getLogger(log.plugin_id)
        logger.debug(text)

    @staticmethod
    def set_level(level=logging.DEBUG):
        logger = logging.getLogger(log.plugin_id)
        logger.setLevel(level)

    @staticmethod
    def last_exception(msg):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log.error(
            msg + '\n  '.join(traceback.format_exception(exc_type,
                              exc_value, exc_traceback)))

    @staticmethod
    def init_logging():
        try:
            """ set up rotating log file handler with custom formatting """
            log.handler = logging.handlers.RotatingFileHandler(
                log_file_path, maxBytes=1024 * 10, backupCount=5)
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)-8s %(message)s")
            log.handler.setFormatter(formatter)
            logger = logging.getLogger(log.plugin_id)  # root logger
            logger.setLevel(logging.INFO)
            logger.addHandler(log.handler)
            log.info("----------------- Start Log -----------------")
        except Exception:
            pass

    @staticmethod
    def remove_logging():
        logger = logging.getLogger(log.plugin_id)
        logger.removeHandler(log.handler)
        del log.handler

    @staticmethod
    def log_Stack_trace():
        logger = logging.getLogger(log.plugin_id)
        logger.debug("log_Stack_trace")
        for x in inspect.stack():
            logger.debug(x)

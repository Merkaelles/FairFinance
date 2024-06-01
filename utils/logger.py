import os
import logging
import logging.handlers
from flask import request
from datetime import datetime


class FairFinanceRequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super().format(record)


def create_logger(app):
    logging_level = app.config['LOGGING_LEVEL']
    logging_file_dir = app.config['LOGGING_FILE_DIR']
    logging_file_max_bytes = app.config['LOGGING_FILE_MAX_BYTES']
    logging_file_backup = app.config['LOGGING_FILE_BACKUP']

    if not os.path.isdir(logging_file_dir):
        os.mkdir(logging_file_dir)

    request_formatter = FairFinanceRequestFormatter(
        '[%(asctime)s] %(remote_addr)s 请求 %(url)s \t %(levelname)s at %(module)s line %(lineno)d : %(message)s'
    )

    flask_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(logging_file_dir, f'{datetime.now().strftime("%m-%d")}.log'),
        when='D',  # 以天为单位创建log
        backupCount=logging_file_backup)
    flask_file_handler.setFormatter(request_formatter)
    flask_logger = logging.getLogger('resource')
    flask_logger.addHandler(flask_file_handler)
    flask_logger.setLevel(logging_level)
    flask_console_logger = logging.StreamHandler()
    flask_console_logger.setFormatter(
        logging.Formatter('[%(asctime)s] %(levelname)s at %(module)s line %(lineno)d : %(message)s')
    )
    if app.debug:
        flask_logger.addHandler(flask_console_logger)
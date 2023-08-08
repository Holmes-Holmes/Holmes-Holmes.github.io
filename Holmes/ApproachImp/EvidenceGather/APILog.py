import logging

class Logger:
    def __init__(self, filename, level=logging.DEBUG):
         
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

         
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setLevel(level)

         
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

         
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)
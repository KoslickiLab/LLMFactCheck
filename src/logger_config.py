
import logging

#Description: This class sets up the logging configuration for the application.

class Logger:  

    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s"
        )
        
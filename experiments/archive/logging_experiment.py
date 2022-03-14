import logging
import coloredlogs

my_logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',logger=my_logger)


def leggo_logging():
    # logging.critical("heya")
    # logging.error("oh no")
    # my_logger.error("holacola")
    my_logger.debug("This is debug")
    my_logger.info("This is info")
    my_logger.warning("This is warning")
    my_logger.error("This is an error")
    my_logger.critical("This is a critical message")


if __name__ == "__main__":
    leggo_logging()
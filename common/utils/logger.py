import logging
from rich.logging import RichHandler

formatter = logging.Formatter(
    "[bold cyan]%(asctime)s[/] - [bold %(levelname)s]%(levelname)s[/] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

rich_handler = RichHandler(markup=True)
rich_handler.setFormatter(formatter)

logger = logging.getLogger("colorful_logger")
logger.setLevel(logging.INFO)
logger.addHandler(rich_handler)


def log(msg):
    logger.info(msg)

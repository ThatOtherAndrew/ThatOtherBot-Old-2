import logging
from pathlib import Path

from bot.settings import settings


def init_logger(logging_level: int = logging.NOTSET) -> logging.Logger:
    """Initialise the logger and return an instance"""
    logger = logging.getLogger('discord')
    logger.setLevel(logging_level)
    logging_formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(name)s: %(message)s')
    handler = logging.FileHandler('logs/discord.log', 'w', 'utf-8')
    handler.setFormatter(logging_formatter)
    logger.addHandler(handler)
    if settings['logging_level'] == 0:
        logging.disable()
    return logger


log = init_logger((logging.WARNING, logging.INFO, logging.DEBUG)[settings['logging_level'] - 1])


def get_extensions(search_dir: str) -> list[str]:
    """Recursively gets the dot-separated import syntax of all Python files in a directory"""
    search_path = Path(search_dir)
    if not search_path.is_dir():
        raise FileNotFoundError(f'{search_dir} is not a valid directory.')

    return [path.parent.as_posix().lstrip('.').replace('/', '.') for path in search_path.glob('*/__init__.py')]

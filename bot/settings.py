from logging import getLogger
from pathlib import Path
from typing import Callable, Iterable

import tomlkit


_logger = getLogger('discord')


class Option:
    def __init__(self, key: str, value: object, *, enforce_type: bool = True,
                 is_in: Iterable = None, validator: Callable[[object], bool] = lambda _: True):
        self.key = key
        self.value = value
        self.enum = is_in
        self.type_accepts = lambda x: isinstance(x, type(value)) if enforce_type else lambda _: True
        self.enum_accepts = lambda x: x in is_in if is_in is not None else lambda _: True
        self.validator_accepts = validator


Comment = tomlkit.comment
Newline = tomlkit.nl

settings_template = list[Option | tomlkit.api.Comment | tomlkit.api.Whitespace]
document_or_table = tomlkit.TOMLDocument | tomlkit.api.Table

TEMPLATE = [
    Comment('Don\'t touch this setting unless you know what you\'re doing!'),
    Option('debug_mode', False),
    Option('debug_guild_id', 0),
    Newline(),
    Comment('Add your bot token into the below string - don\'t share this with anybody!'),
    Option('bot_token', ''),
    Newline(),
    Comment('0: Disable logging'),
    Comment('1: Log warnings and errors'),
    Comment('2: Log information in addition to warnings and errors'),
    Comment('3: Log everything, including debug messages'),
    Option('logging_level', 2, is_in=range(4))
]


def load(file_path: str | Path) -> tomlkit.TOMLDocument:
    """Loads TOML settings from a given path, or generates a new file if it doesn't exist"""
    settings_path = Path(file_path)
    if settings_path.is_file():
        _logger.info(f'Loaded configuration from {settings_path.name}')
        with settings_path.open('r') as f:
            document = tomlkit.load(f)
    else:
        _logger.info(f'Configuration file {settings_path.name} missing, generating from template')
        document = generate(TEMPLATE)
        save(document, settings_path)

    return validate(document, TEMPLATE)


def save(document: tomlkit.TOMLDocument, file_path: str | Path) -> None:
    """Save a TOML document to a given path"""
    settings_path = Path(file_path)
    with settings_path.open('w') as f:
        tomlkit.dump(document, f)


def generate(template: settings_template, *, table: bool = False) -> document_or_table:
    """Generates a TOML document or table from a provided settings template"""
    document = tomlkit.table() if table else tomlkit.TOMLDocument()
    for item in template:
        match item:
            case Option():
                document.add(item.key, item.value)
            case tomlkit.api.Comment() | tomlkit.api.Whitespace():
                document.add(item)
            case _:
                raise TypeError('Template can only contain Option, Comment and Whitespace items')

    return document


def validate(toml_document: document_or_table, template: settings_template) -> document_or_table:
    """Takes a TOML document and validates it against a provided settings template"""
    for item in template:
        match item:
            case Option():
                if item.key in toml_document:
                    if not item.type_accepts(toml_document[item.key]):
                        raise TypeError(f'{item.key} setting must be of type {type(item.value).__name__}, '
                                        f'but {type(toml_document[item.key]).__name__.lower()} was provided')
                    if not item.enum_accepts(toml_document[item.key]):
                        raise ValueError(f'{item.key} setting must be one of {item.enum}')
                    if not item.validator_accepts(toml_document[item.key]):
                        raise ValueError(f'{item.key} setting did not pass validation condition')
                else:
                    raise KeyError(f'{item.key} setting was not found')
                    # TODO: append setting to file if not there
            case tomlkit.api.Comment() | tomlkit.api.Whitespace():
                pass  # Ignore comments and whitespace during validation, otherwise things get very complicated
            case _:
                raise TypeError('Template can only contain Option, Comment and Whitespace items')

    return toml_document


def add_table(name: str, template: settings_template) -> None:
    if name in settings:
        table = settings[name]
    else:
        _logger.info(f'Table "{name}" in configuration file missing, generating from template')
        table = generate(template, table=True)

    settings[name] = validate(table, template)
    save(settings, 'settings.toml')


settings = load('settings.toml')

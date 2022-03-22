from pathlib import Path
from typing import Callable, Union, Iterable

import tomlkit

from bot.tools import log


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

settings_template = list[Union[Option, tomlkit.api.Comment, tomlkit.api.Whitespace]]
document_or_table = Union[tomlkit.TOMLDocument, tomlkit.api.Table]

TEMPLATE = [
    Comment('0: Disable logging'),
    Comment('1: Log warnings and errors'),
    Comment('2: Log information in addition to warnings and errors'),
    Comment('3: Log everything, including debug messages'),
    Option('logging_level', 2, is_in=range(4))
]


def load(file: str) -> tomlkit.TOMLDocument:
    """Loads TOML settings from a given path, or generates a new file if it doesn't exist"""
    settings_path = Path(file)
    if settings_path.is_file():
        log.info(f'Loaded configuration from {settings_path.name}')
        with settings_path.open('r') as f:
            settings = tomlkit.load(f)
    else:
        log.info(f'Configuration file {settings_path.name} missing, generating from template')
        settings = generate(TEMPLATE)
        with settings_path.open('w') as f:
            tomlkit.dump(settings, f)

    return validate(settings, TEMPLATE)


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


def validate(settings: document_or_table, template: settings_template) -> document_or_table:
    """Takes a TOML document and validates it against a provided settings template"""
    for item in template:
        match item:
            case Option():
                if item.key in settings:
                    if not item.type_accepts(settings[item.key]):
                        raise TypeError(f'{item.key} setting must be of type {type(item.value).__name__}, '
                                        f'but {type(settings[item.key]).__name__.lower()} was provided')
                    if not item.enum_accepts(settings[item.key]):
                        raise ValueError(f'{item.key} setting must be one of {item.enum}')
                    if not item.validator_accepts(settings[item.key]):
                        raise ValueError(f'{item.key} setting did not pass validation condition')
                else:
                    pass  # TODO: append setting to file if not there
            case tomlkit.api.Comment() | tomlkit.api.Whitespace():
                pass  # Ignore comments and whitespace during validation, otherwise things get very complicated
            case _:
                raise TypeError('Template can only contain Option, Comment and Whitespace items')

    return settings

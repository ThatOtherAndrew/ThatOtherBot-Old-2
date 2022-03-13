from pathlib import Path


def get_extensions(search_dir: str) -> list[str]:
    search_path = Path(search_dir)
    if not search_path.is_dir():
        raise FileNotFoundError(f'{search_dir} is not a valid directory.')

    return [(path.parent/path.stem).as_posix().lstrip('.').replace('/', '.') for path in search_path.rglob('*.py')]

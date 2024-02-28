""" Вспомогательные методы для работы с файлами. """
import datetime
import os
from pathlib import Path
from typing import Dict, Union


class FileInfo:
    """ Вспомогательный класс, содержащий информацию о файле. """
    name: str
    path: str
    modified_at: datetime.datetime

    def __init__(self, name: str, path: str, modified_at: datetime.datetime):
        self.name = name
        self.path = path
        self.modified_at = modified_at

    def __str__(self):
        return f'File {self.name}, modified at {self.modified_at}'

    def __repr__(self):
        return f'File {self.name}, modified at {self.modified_at}'


def check_if_exists(path: str) -> bool:
    """
    Проверка существования файла/директории.

    Args:
         path (str): путь к файлу/директории.
    Returns:
        bool
    """

    return os.path.exists(path)


def get_base_name(path: str) -> str:
    """
    Получение имени файла из заданного пути.

    Args:
        path (str): путь к файлу.
    Returns:
        str: Имя файла.
    """

    return os.path.basename(path)


def get_file_bytes(path: str) -> Union[bytes, None]:
    """
    Получение содержимого файла в байтовом виде.

    Args:
        path (str): путь к файлу.
    Returns:
        bytes: Содержимое файла. Или None, если файл не существует.
    """

    if not check_if_exists(path):
        return

    with open(path, 'rb') as f:
        return f.read()


def get_files_info(path: str) -> Union[Dict[str, FileInfo], None]:
    """
    Получение информации о файлах в директории.

    Args:
        path (str): путь к директории.
    Returns:
        Dict[str, FileInfo]: словарь с данными о файлах.
                             Или None, если директория не существует
    """

    if not check_if_exists(path):
        return

    return {
        f.name: FileInfo(
            name=f.name,
            path=f.path,
            modified_at=datetime.datetime.fromtimestamp(
                f.stat().st_mtime,
                tz=datetime.timezone.utc
            )
        )
        for f in os.scandir(path)
        if f.is_file()
    }


def get_abs_path(path: str) -> str:
    if os.path.isabs(path):
        return path

    return os.path.join(Path(__file__).parent.parent, path)

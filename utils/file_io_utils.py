""" Вспомогательные методы для работы с файлами. """

import os
from typing import Union


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

import sys

from dotenv import dotenv_values
from loguru import logger

from file_monitor.file_monitor import FileMonitor
from synchronizer.yandex_synchronizer import YandexSynchronizer
from utils import file_utils


def configure_logger(log_directory: str):
    log_format = '{time} | {level} | {message}'
    log_cong = {
        'handlers': [
            {'sink': sys.stdout, 'format': log_format},
            {'sink': log_directory + '/{time}.log', 'format': log_format},
        ]
    }
    logger.configure(**log_cong)


def main():
    config = dotenv_values(".env")

    oauth_token = config.get('oauth_token')
    local_folder_path = config.get('local_folder_path')
    remote_folder_name = config.get('remote_folder_name')
    synchronization_interval = config.get('synchronization_interval')
    log_directory = config.get('log_directory')

    try:
        synchronization_interval = int(synchronization_interval)
    except (TypeError, ValueError):
        print('Необходимо указать synchronization_interval в секундах в .env файле')
        return

    if not local_folder_path:
        print('Необходимо указать local_folder_path в .env файле')
        return

    local_folder_path = file_utils.get_abs_path(local_folder_path)
    if not file_utils.check_if_exists(local_folder_path):
        print('Необходимо указать существующую директорию в local_folder_path в .env файле')
        return

    if not remote_folder_name:
        print('Необходимо указать remote_folder_name в .env файле')
        return

    if not oauth_token:
        print('Необходимо указать oauth_token в .env файле')
        return

    if not log_directory:
        print('Необходимо указать log_directory в .env файле')
        return

    configure_logger(file_utils.get_abs_path(log_directory))

    ys = YandexSynchronizer(oauth_token, local_folder_path, remote_folder_name)
    fm = FileMonitor(local_folder_path, int(synchronization_interval), ys)
    fm.start()


if __name__ == '__main__':
    main()

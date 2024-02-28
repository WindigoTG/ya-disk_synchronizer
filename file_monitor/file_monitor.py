import time

from loguru import logger

from synchronizer.synchronizer import Synchronizer
from utils import file_utils


class FileMonitor:
    """ Класс, отслеживающий состояние файлов. """
    local_file_folder: str
    interval: int
    synchronizer: Synchronizer

    def __init__(
            self,
            local_file_folder: str,
            interval: int,
            synchronizer: Synchronizer,
    ):
        self.interval = interval
        self.local_file_folder = local_file_folder
        self.synchronizer = synchronizer

    def start(self):
        """ Запуск мониторинга. """
        logger.info(
            'Программа синхронизации файлов начинает работу с директорией {directory}'.format(
                directory=self.local_file_folder,
            ),
        )
        while True:
            self.perform_synchronization()
            time.sleep(self.interval)

    def perform_synchronization(self):
        """ Выполнить синхронизацию файлов. """
        remote_files = self.synchronizer.get_info()
        local_files = file_utils.get_files_info(self.local_file_folder)
        if remote_files is None or local_files is None:
            return

        for file in remote_files:
            if file not in local_files.keys():
                logger.info(
                    'Подлежащий удалению файл {file} обнаружен в удалённом хранилище'.format(
                        file=file
                    ),
                )
                self.synchronizer.delete(file)

        for file in local_files.keys():
            if file not in remote_files:
                logger.info(
                    'Файл {file} не найден в удалённом хранилище'.format(
                        file=file
                    ),
                )
                self.synchronizer.upload(local_files[file].path)
            elif local_files[file].modified_at > remote_files[file].modified_at:
                logger.info(
                    'Устаревший файл {file} обнаружен в удалённом хранилище'.format(
                        file=file
                    ),
                )
                self.synchronizer.update(local_files[file].path)

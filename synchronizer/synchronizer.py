from abc import ABC


class Synchronizer(ABC):
    """ Базовый класс-синхронизатор файлов в удалённом хранилище. """
    oauth_token: str
    local_folder_path: str
    remote_folder_name: str

    def __init__(
        self,
        oauth_token: str,
        local_folder_path: str,
        remote_folder_name: str,
    ):
        self.oauth_token = oauth_token
        self.local_folder_path = local_folder_path
        self.remote_folder_name = remote_folder_name

    def upload(self, path: str):
        """ Загрузить файл в хранилище. """

    def update(self, path: str):
        """ Обновить файл в хранилище. """

    def delete(self, filename: str):
        """ Удалить файл из хранилища. """

    def get_info(self):
        """ Получить информации о файлах в хранилище. """

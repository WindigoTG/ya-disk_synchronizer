import datetime
from typing import Dict, Union

import requests

from utils import file_utils
from synchronizer.synchronizer import Synchronizer


class YandexSynchronizer(Synchronizer):
    """ Класс, отвечающий за синхронизацию с Яндекс Диском. """
    BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
    BASE_ARGS = '?path=app:/'

    def __init__(
        self,
        oauth_token: str,
        local_folder_path: str,
        remote_folder_name: str,
        timeout: int = 10,
    ):
        super().__init__(oauth_token, local_folder_path, remote_folder_name)
        self.timeout = timeout

    def upload(self, path: str):
        """
        Загрузить файл в хранилище.

        Args:
            path (str): путь к файлу.
        """
        if not file_utils.check_if_exists(path):
            return

        filename = file_utils.get_base_name(path)

        upload_url = self.get_upload_url(filename)
        if not upload_url:
            return

        payload = file_utils.get_file_bytes(path)
        if not payload:
            return

        try:
            response = requests.put(
                upload_url,
                data=payload,
                timeout=self.timeout,
            )
        except ConnectionError:
            return
        except TimeoutError:
            return

    def update(self, path: str):
        """
        Обновить файл в хранилище.

        Args:
            path (str): путь к файлу.
        """
        if not file_utils.check_if_exists(path):
            return

        filename = file_utils.get_base_name(path)

        upload_url = self.get_upload_url(filename, True)
        if not upload_url:
            return

        payload = file_utils.get_file_bytes(path)
        if not payload:
            return

        try:
            response = requests.put(
                upload_url,
                data=payload,
                timeout=self.timeout,
            )
        except ConnectionError:
            return
        except TimeoutError:
            return

    def delete(self, filename: str):
        """ Удалить файл из хранилища. """
        url = '{base_url}{base_args}{folder}/{filename}'.format(
            base_url=self.BASE_URL,
            base_args=self.BASE_ARGS,
            folder=self.remote_folder_name,
            filename=filename,
        )

        try:
            response = requests.delete(
                url,
                headers={'Authorization': self.oauth_token},
                timeout=self.timeout,
            )
        except ConnectionError:
            return
        except TimeoutError:
            return

    def get_info(self) -> Union[Dict[str, file_utils.FileInfo], None]:
        """ Получить информации о файлах в хранилище. """
        url = '{base_url}{base_args}{folder}'.format(
            base_url=self.BASE_URL,
            base_args=self.BASE_ARGS,
            folder=self.remote_folder_name,
        )

        try:
            response = requests.get(
                url,
                headers={'Authorization': self.oauth_token},
                timeout=self.timeout,
            )
        except ConnectionError:
            return
        except TimeoutError:
            return

        if response.status_code == 404:
            if self.create_remote_folder():
                return self.get_info()

        if response.status_code == 200:
            return {
                f['name']: file_utils.FileInfo(
                    name=f['name'],
                    path=f['path'],
                    modified_at=datetime.datetime.fromisoformat(f['modified'])
                )
                for f in response.json()['_embedded']['items']
                if f['type'] == 'file'
            }

    def get_upload_url(
            self,
            filename: str,
            overwrite: bool = False,
    ) -> Union[str, None]:
        """ Получить ссылку для загрузки файла. """

        url = '{base_url}/upload{base_args}{folder}/{filename}'.format(
            base_url=self.BASE_URL,
            base_args=self.BASE_ARGS,
            folder=self.remote_folder_name,
            filename=filename,
        )
        if overwrite:
            url += '&overwrite=true'
        print(url)

        try:
            response = requests.get(
                url,
                headers={'Authorization': self.oauth_token},
                timeout=self.timeout,
            )
        except ConnectionError:
            return
        except TimeoutError:
            return

        # Согласно документации, при отсутствии указанной папки
        # должен возвращаться код 404, но на практике возвращается 409
        if response.status_code == 404 or (
            response.status_code == 409 and
            response.json()['error'] == 'DiskPathDoesntExistsError'
        ):
            if self.create_remote_folder():
                return self.get_upload_url(filename, overwrite)

        if response.status_code == 200:
            return response.json()['href']

    def create_remote_folder(self) -> bool:
        """ Создать папку в удалённом хранилище. """

        url = '{base_url}{base_args}{folder}'.format(
            base_url=self.BASE_URL,
            base_args=self.BASE_ARGS,
            folder=self.remote_folder_name,
        )

        try:
            response = requests.put(
                url,
                headers={'Authorization': self.oauth_token},
                timeout=self.timeout,
            )
        except ConnectionError:
            return False
        except TimeoutError:
            return False

        return response.status_code == 201


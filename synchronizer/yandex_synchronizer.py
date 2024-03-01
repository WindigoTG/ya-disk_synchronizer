import datetime
from typing import Dict, Union

import requests
from requests.exceptions import ConnectionError, Timeout
from loguru import logger

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
            )
        except ConnectionError:
            logger.error(
                'Файл {file} не загружен. Ошибка соединения.'.format(
                    file=filename,
                ),
            )
            return
        except Timeout:
            logger.error(
                'Файл {file} не загружен. Таймаут.'.format(
                    file=filename,
                ),
            )
            return

        if response.status_code == 201 or response.status_code == 202:
            logger.info(
                'Файл {file} успешно загружен.'.format(
                    file=filename,
                ),
            )
            return

        error = response.json().get('error')
        logger.error(
            'Файл {file} не загружен. Причина: {error}.'.format(
                file=filename,
                error=error
            ),
        )

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
            )
        except ConnectionError:
            logger.error(
                'Файл {file} не обновлён. Ошибка соединения.'.format(
                    file=filename,
                ),
            )
            return
        except Timeout:
            logger.error(
                'Файл {file} не обновлён. Таймаут.'.format(
                    file=filename,
                ),
            )
            return

        if response.status_code == 201 or response.status_code == 202:
            logger.info(
                'Файл {file} успешно обновлён.'.format(
                    file=filename,
                ),
            )
            return

        error = response.json().get('error')
        logger.error(
            'Файл {file} не обновлён. Причина: {error}.'.format(
                file=filename,
                error=error
            ),
        )

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
            logger.error(
                'Файл {file} не удалён. Ошибка соединения.'.format(
                    file=filename,
                ),
            )
            return
        except Timeout:
            logger.error(
                'Файл {file} не удалён. Таймаут.'.format(
                    file=filename,
                ),
            )
            return

        if response.status_code == 401:
            logger.error(
                'Файл {file} не удалён. Недействительный oauth token.',
            )
            return

        if response.status_code == 204 or response.status_code == 202:
            logger.info(
                'Файл {file} успешно удалён.'.format(
                    file=filename,
                ),
            )
            return

        error = response.json().get('error')
        logger.error(
            'Файл {file} не удалён. Причина: {error}.'.format(
                file=filename,
                error=error
            ),
        )

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
            logger.error(
                'Не удалось получить информацию об удалённом хранилище. Ошибка соединения.',
            )
            return
        except Timeout:
            logger.error(
                'Не удалось получить информацию об удалённом хранилище. Таймаут.',
            )
            return

        if response.status_code == 401:
            logger.error(
                'Не удалось получить информацию об удалённом хранилище. Недействительный oauth token.',
            )
            return

        if response.status_code == 404:
            if self.create_remote_folder():
                return self.get_info()

        if response.status_code == 200:
            return {
                f['name']: file_utils.FileInfo(
                    name=f['name'],
                    path=f['path'],
                    modified_at=datetime.datetime.fromisoformat(f['modified']),
                    size=f['size'],
                )
                for f in response.json()['_embedded']['items']
                if f['type'] == 'file'
            }

        error = response.json().get('error')
        logger.error(
            'Не удалось получить информацию об удалённом хранилище. Причина: {error}.'.format(
                error=error
            ),
        )

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

        try:
            response = requests.get(
                url,
                headers={'Authorization': self.oauth_token},
                timeout=self.timeout,
            )
        except ConnectionError:
            logger.error(
                'Не удалось получить ссылку для {action} файла {file}. Ошибка соединения.'.format(
                    action='обновления' if overwrite else 'загрузки',
                    file=filename,
                ),
            )
            return
        except Timeout:
            logger.error(
                'Не удалось получить ссылку для {action} файла {file}. Таймаут.'.format(
                    action='обновления' if overwrite else 'загрузки',
                    file=filename,
                ),
            )
            return

        if response.status_code == 401:
            logger.error(
                'Не удалось получить ссылку для {action} файла {file}. Недействительный oauth token.',
            )
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

        error = response.json().get('error')
        logger.error(
            'Не удалось получить ссылку для {action} файла {file}. Причина: {error}.'.format(
                action='обновления' if overwrite else 'загрузки',
                error=error,
                file=filename,
            ),
        )

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
            logger.error(
                'Не удалось создать папку {directory} в удалённом хранилище. Ошибка соединения.'.format(
                    directory=self.remote_folder_name,
                ),
            )
            return False
        except Timeout:
            logger.error(
                'Не удалось создать папку {directory} в удалённом хранилище. Таймаут.'.format(
                    directory=self.remote_folder_name,
                ),
            )
            return False

        if response.status_code == 401:
            logger.error(
                'Не удалось создать папку {directory} в удалённом хранилище. Недействительный oauth token.',
            )

        return response.status_code == 201


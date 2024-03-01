## Яндекс диск синхронизатор
Утилита, обеспечивающая синхронизацию содержимого локальной директории с содержимым директории на Яндекс Диске.

Осуществляет загрузку новых локальных файлов на Я.Диск, обновление изменённых локальных файлов на Я.Диске и удаление удаляемых локально файлов с Я.Диска.

Осуществляет логгирование процесса.

### Настройка и запуск
Для того чтобы воспользоваться утилитой, нужно:
1. Скачать [релиз](https://github.com/WindigoTG/ya-disk_synchronizer/releases) для интересующей платформы.
2. Распаковать архив.
3. Рядом с исполняемым файлом создать файл .env по подобию прилагающегося шаблона .env.template и указать в нём необходимые параметры.
   - **local_folder_path** - абсолютный путь к существующей локальной директории, содержимое которой нужно синхронизировать
   - **remote_folder_name** - имя папки на яндекс диске. Папка будет создана в директории "Приложения".
   - **synchronization_interval** - интервал проведения синхронизации, в секундах.
   - **log_directory** - абсолютный путь до директории, в которой приложение должно сохранять логи. 
   - **oauth_token** - токен аутентификации приложения на Яндекс. Диске
     - Получить токен можно воспользовавшись [инструкцией](https://yandex.ru/dev/disk-api/doc/ru/concepts/quickstart#oauth). 
     - При этом необходимо указать для приложения права доступа "**Доступ к папке приложения на Диске — cloud_api:disk.app_folder**"
4. Запустить приложение:
    - Windows: запустив исполняемый файл YaDisk_Synchronizer.exe
    - Ubuntu: выполнив команду ```./YaDisk_Synchronizer```
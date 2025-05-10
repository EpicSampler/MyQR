from segno import *
from PIL import Image
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import traceback

class QR:
    def __init__(self):
        self.qr = None
        self.drive_service = None
        self.last_error = None

    def _handle_error(self, error_msg, exception=None):
        """Обработка и сохранение ошибки"""
        if exception:
            error_msg += f"\n{str(exception)}\n{traceback.format_exc()}"
        self.last_error = error_msg
        print(f"Ошибка: {error_msg}")  # Логирование в консоль
        return [False, error_msg]

    def _authenticate_google_drive(self):
        """Аутентификация в Google Drive API"""
        try:
            creds = None
            token_path = "google api/token.json"
            creds_path = "google api/credentials.json"

            # Проверка существования файлов
            if not os.path.exists(creds_path):
                return self._handle_error("Файл credentials.json не найден")

            if os.path.exists(token_path):
                try:
                    creds = Credentials.from_authorized_user_file(
                        token_path, 
                        ["https://www.googleapis.com/auth/drive.file"]
                    )
                except Exception as e:
                    return self._handle_error("Ошибка чтения token.json", e)

            # Обновление или получение новых учетных данных
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        return self._handle_error("Ошибка обновления токена", e)
                else:
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            creds_path,
                            ["https://www.googleapis.com/auth/drive.file"]
                        )
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        return self._handle_error("Ошибка аутентификации", e)

                # Сохранение токена
                try:
                    os.makedirs("google api", exist_ok=True)
                    with open(token_path, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    return self._handle_error("Ошибка сохранения токена", e)

            self.drive_service = build("drive", "v3", credentials=creds)
            return [True, "Аутентификация успешна"]

        except Exception as e:
            return self._handle_error("Критическая ошибка аутентификации", e)

    def _upload_to_gdrive(self, file_path, file_name="uploaded_image.png"):
        """Загружает изображение на Google Drive и делает его публичным"""
        try:
            # Проверка файла
            if not os.path.exists(file_path):
                return self._handle_error(f"Файл {file_path} не найден")

            # Аутентификация
            auth_result = self._authenticate_google_drive()
            if not auth_result[0]:
                return auth_result

            # Загрузка файла
            try:
                file_metadata = {"name": file_name}
                media = MediaFileUpload(file_path, mimetype="image/png")
                
                file = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id"
                ).execute()

                # Настройка прав доступа
                self.drive_service.permissions().create(
                    fileId=file["id"],
                    body={"type": "anyone", "role": "reader"},
                ).execute()

                return [True, f"https://drive.google.com/uc?export=view&id={file['id']}"]
            
            except Exception as e:
                return self._handle_error("Ошибка загрузки на Google Drive", e)

        except Exception as e:
            return self._handle_error("Критическая ошибка при загрузке", e)

    def make(self, size: bool, data: any, is_image=False):
        """Создает QR-код с обработкой ошибок"""
        self.data = data
        try:
            # Проверка входных данных
            if not data:
                return self._handle_error("Не указаны данные для QR-кода")

            if is_image:
                if not isinstance(data, str) or not os.path.exists(data):
                    return self._handle_error("Неверный путь к изображению")
                
                # Загрузка на Google Drive
                upload_result = self._upload_to_gdrive(data)
                if not upload_result[0]:
                    return upload_result
                
                public_url = upload_result[1]
                self.qr = make(content=public_url, micro=size)
            else:
                self.qr = make(content=data, micro=size)

            # Сохранение QR-кода
            try:
                os.makedirs("qrs", exist_ok=True)
                self.qr.save(
                    'qrs/qr.png',
                    scale=20,
                    light='White',
                    dark='Black',
                    border=5
                )
                return [True, "QR-код успешно создан"]
            except Exception as e:
                return self._handle_error("Ошибка сохранения QR-кода", e)

        except Exception as e:
            return self._handle_error("Ошибка создания QR-кода", e)

    def save_with_style(self, 
                       background_color: str | tuple = (0, 0, 0),
                       color: str | tuple = (255, 255, 255),
                       size: bool = False,
                       border: int | float = 3,
                       scale: int | float = 20):
        """Сохраняет QR-код с кастомными стилями"""
        try:
            if not self.qr:
                return self._handle_error("Сначала создайте QR-код")

            # Проверка цветов
            if not background_color or not color:
                return self._handle_error("Не указаны цвета")

            try:
                self.qr = make(micro=size, content=self.data)
                self.qr.save(
                    'qrs/qr.png',
                    scale=scale,
                    light=color,
                    dark=background_color,
                    border=border
                )
                return [True, "Стиль QR-кода успешно применен"]
            except Exception as e:
                return self._handle_error("Ошибка сохранения стиля", e)

        except Exception as e:
            return self._handle_error("Ошибка применения стиля", e)

    def get_last_error(self):
        """Возвращает последнее сообщение об ошибке"""
        return self.last_error
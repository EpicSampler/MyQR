# Импорт необходимых модулей
import os  # Для работы с файловой системой
import rsa  # Для шифрования/дешифрования данных
from datetime import datetime
from PyQt5.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, 
                            QFrame, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt


class HistoryManager:
    def __init__(self):
        self.key_dir = "files/crypto_keys"
        self.history_file = "files/history/history.bin"  # Изменим расширение для бинарного файла
        os.makedirs(self.key_dir, exist_ok=True)
        
        self.public_key, self.private_key = self._init_verified_keys()
        print(f"Ключи инициализированы: Public - {bool(self.public_key)}, Private - {bool(self.private_key)}")

    def _init_verified_keys(self):
        """Инициализация ключей с проверкой"""
        pub_path = os.path.join(self.key_dir, "public.pem")
        priv_path = os.path.join(self.key_dir, "private.pem")

        # Проверяем существующие ключи
        if os.path.exists(pub_path) and os.path.exists(priv_path):
            try:
                with open(pub_path, "rb") as f:
                    pub_key = rsa.PublicKey.load_pkcs1(f.read())
                with open(priv_path, "rb") as f:
                    priv_key = rsa.PrivateKey.load_pkcs1(f.read())
                
                # Тест шифрования/дешифрования
                test_data = b"test_123"
                encrypted = rsa.encrypt(test_data, pub_key)
                decrypted = rsa.decrypt(encrypted, priv_key)
                
                if decrypted == test_data:
                    print("Ключи прошли проверку")
                    return pub_key, priv_key
                print("Ключи не прошли проверку - создаем новые")
            except Exception as e:
                print(f"Ошибка проверки ключей: {e}")

        # Создаем новые ключи
        print("Генерация новых ключей...")
        pub_key, priv_key = rsa.newkeys(2048)
        
        try:
            with open(pub_path, "wb") as f:
                f.write(pub_key.save_pkcs1())
            with open(priv_path, "wb") as f:
                f.write(priv_key.save_pkcs1())
            print("Новые ключи сохранены")
            return pub_key, priv_key
        except Exception as e:
            print(f"Ошибка сохранения ключей: {e}")
            return None, None

    def add_record(self, data):
        """Добавление записи в бинарном формате"""
        if not self.public_key:
            print("Ошибка: Нет публичного ключа")
            return False

        try:
            # Подготовка данных
            data_bytes = data[:50].encode('utf-8')  # Уменьшенный лимит
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()
            
            # Шифруем данные
            encrypted = rsa.encrypt(data_bytes, self.public_key)
            
            # Формируем запись: [длина метки][метка][длина данных][данные]
            record = (
                len(timestamp).to_bytes(2, 'big') +  # 2 байта для длины метки
                timestamp +
                len(encrypted).to_bytes(2, 'big') +  # 2 байта для длины данных
                encrypted
            )
            
            # Записываем в бинарный файл
            with open(self.history_file, "ab") as f:
                f.write(record)
            
            print(f"Запись добавлена: {data[:20]}...")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False

    def get_records(self):
        """Чтение записей из бинарного файла"""
        if not self.private_key:
            print("Ошибка: Нет приватного ключа")
            return []

        if not os.path.exists(self.history_file):
            return []

        records = []
        try:
            with open(self.history_file, "rb") as f:
                while True:
                    # Читаем длину метки времени
                    len_ts_bytes = f.read(2)
                    if not len_ts_bytes:
                        break
                    len_ts = int.from_bytes(len_ts_bytes, 'big')
                    
                    # Читаем метку времени
                    timestamp = f.read(len_ts).decode('utf-8')
                    
                    # Читаем длину данных
                    len_data_bytes = f.read(2)
                    if not len_data_bytes:
                        break
                    len_data = int.from_bytes(len_data_bytes, 'big')
                    
                    # Читаем зашифрованные данные
                    encrypted = f.read(len_data)
                    if not encrypted:
                        break
                    
                    # Дешифруем
                    try:
                        decrypted = rsa.decrypt(encrypted, self.private_key).decode('utf-8')
                        records.append((timestamp, decrypted))
                    except Exception as e:
                        print(f"Ошибка дешифрования записи: {e}")
                        continue
                        
        except Exception as e:
            print(f"Ошибка чтения файла истории: {e}")

        return records

    def clear_history(self):
        """Очищает файл истории"""
        try:
            if os.path.exists(self.history_file):
                # Открываем файл в режиме записи с очисткой содержимого
                with open(self.history_file, "wb") as f:
                    f.truncate(0)
                print("История успешно очищена")
                return True
            else:
                print("Файл истории не существует, очистка не требуется")
                return True
        except Exception as e:
            print(f"Ошибка при очистке истории: {e}")
            return False


class HistoryDialog(QDialog):
    def __init__(self, parent, history_manager):
        super().__init__(parent)
        self.history = history_manager
        self.setWindowTitle("История QR-кодов")
        self.setMinimumSize(500, 400)
        
        # Применяем стили
        self.setStyleSheet("""
            .history-item {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                margin: 5px;
                padding: 10px;
            }
            
            .timestamp-label {
                color: #4a5568;
                font-weight: bold;
                font-size: 13px;
            }
            
            .data-label {
                color: #2d3748;
                font-size: 14px;
            }
            
            .status-message {
                color: #64748b;
                font-size: 14px;
                font-style: italic;
                padding: 20px;
                text-align: center;
            }
        """)
        
        self.layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("История созданий QR-кодов")
        title_label.setProperty("class", "title-label")
        self.layout.addWidget(title_label)
        
        # Область с прокруткой
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setAlignment(Qt.AlignTop)
        
        # Инициализируем контейнер с записями
        self.update_history_display()
        
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Очистить историю")
        clear_btn.setProperty("class", "clear-button")
        clear_btn.clicked.connect(self.clear_history)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setProperty("class", "close-button")
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)
    
    def update_history_display(self):
        """Обновляет отображение истории"""
        # Очищаем контейнер
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Добавляем текущие записи или сообщение
        records = self.history.get_records()
        if not records:
            self.show_status_message("История пуста")
        else:
            for timestamp, data in records:
                self.add_history_item(timestamp, data)
    
    def add_history_item(self, timestamp, data):
        """Добавляет элемент истории в контейнер"""
        frame = QFrame()
        frame.setProperty("class", "history-item")
        
        item_layout = QVBoxLayout()
        
        time_label = QLabel(timestamp)
        time_label.setProperty("class", "timestamp-label")
        
        data_label = QLabel(data)
        data_label.setProperty("class", "data-label")
        data_label.setWordWrap(True)
        
        item_layout.addWidget(time_label)
        item_layout.addWidget(data_label)
        frame.setLayout(item_layout)
        
        self.container_layout.addWidget(frame)
    
    def show_status_message(self, message):
        """Показывает статусное сообщение"""
        status_label = QLabel(message)
        status_label.setProperty("class", "status-message")
        self.container_layout.addWidget(status_label)
    
    def clear_history(self):
        """Очищает историю и обновляет интерфейс"""
        try:
            # Очищаем файл истории
            success = self.history.clear_history()
            
            if success:
                # Обновляем отображение
                self.update_history_display()
                QMessageBox.information(self, "Успех", "История успешно очищена")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось очистить историю")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

# history.py
import os
import rsa
import json
from datetime import datetime
from PyQt5.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QLabel, 
                            QScrollArea, QWidget, QFrame, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

class HistoryManager:
    def __init__(self):
        self.key_dir = "files/crypto_keys"
        self.history_file = "files/history/history.bin"
        self.style_file = "files/history/styles.json"
        os.makedirs(self.key_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        self.public_key, self.private_key = self._init_verified_keys()
        print(f"Ключи инициализированы: Public - {bool(self.public_key)}, Private - {bool(self.private_key)}")

    def _init_verified_keys(self):
        """Инициализация ключей с проверкой"""
        # ... (ваш существующий метод без изменений)
        return self.public_key, self.private_key

    def add_record(self, data, style=None):
        """Добавляет запись с данными и стилем"""
        try:
            # Шифруем данные как раньше
            data_bytes = data[:50].encode('utf-8')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()
            encrypted = rsa.encrypt(data_bytes, self.public_key)
            
            record = (
                len(timestamp).to_bytes(2, 'big') +
                timestamp +
                len(encrypted).to_bytes(2, 'big') +
                encrypted
            )
            
            with open(self.history_file, "ab") as f:
                f.write(record)
            
            # Сохраняем стиль отдельно в JSON
            if style:
                styles = self._load_styles()
                styles[timestamp.decode()] = style
                with open(self.style_file, 'w') as f:
                    json.dump(styles, f)
            
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            return False

    def _load_styles(self):
        """Загружает стили из файла"""
        try:
            if os.path.exists(self.style_file):
                with open(self.style_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def get_records_with_styles(self):
        """Возвращает записи с соответствующими стилями"""
        records = self.get_records()  # Ваш существующий метод
        styles = self._load_styles()
        
        result = []
        for timestamp, data in records:
            style = styles.get(timestamp, {})
            result.append({
                "timestamp": timestamp,
                "data": data,
                "style": style
            })
        return result

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
    itemClicked = pyqtSignal(dict)  # Сигнал при клике на элемент
    
    def __init__(self, parent, history_manager):
        super().__init__(parent)
        self.history = history_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("История QR-кодов")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("История созданий QR-кодов")
        title_label.setProperty("class", "title-label")
        layout.addWidget(title_label)
        
        # Область с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setAlignment(Qt.AlignTop)
        
        self.load_history()
        
        self.container.setLayout(self.container_layout)
        scroll_area.setWidget(self.container)
        layout.addWidget(scroll_area)
        
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
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_history(self):
        """Загружает историю и создает элементы"""
        records = self.history.get_records_with_styles()
        if not records:
            self.show_status_message("История пуста")
        else:
            for item in reversed(records):  # Новые записи сверху
                self.add_history_item(item)
    
    def add_history_item(self, item):
        """Добавляет кликабельный элемент истории"""
        frame = QFrame()
        frame.setProperty("class", "history-item")
        frame.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Обработчик клика
        def handle_click(event):
            self.itemClicked.emit(item)
            self.close()
        
        frame.mousePressEvent = handle_click
        
        layout = QVBoxLayout()
        
        time_label = QLabel(item["timestamp"])
        time_label.setProperty("class", "timestamp-label")
        
        data_label = QLabel(item["data"])
        data_label.setProperty("class", "data-label")
        data_label.setWordWrap(True)
        
        layout.addWidget(time_label)
        layout.addWidget(data_label)
        frame.setLayout(layout)
        
        self.container_layout.addWidget(frame)
    
    def show_status_message(self, message):
        """Показывает статусное сообщение"""
        status_label = QLabel(message)
        status_label.setProperty("class", "status-message")
        self.container_layout.addWidget(status_label)
    
    def clear_history(self):
        """Очищает историю"""
        try:
            if self.history.clear_history():
                # Также очищаем стили
                if os.path.exists(self.history.style_file):
                    os.remove(self.history.style_file)
                self.container_layout.clear()
                self.show_status_message("История очищена")
                QMessageBox.information(self, "Успех", "История успешно очищена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось очистить: {e}")
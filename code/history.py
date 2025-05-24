# history.py
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QLabel, 
                            QScrollArea, QWidget, QFrame, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

class HistoryManager:
    def __init__(self):
        self.history_file = "files/history/history.json"
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
    def add_record(self, data, style=None):
        """Добавляет или обновляет запись в истории"""
        try:
            new_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": data,
                "style": style or {}
            }
            
            history = self.get_records()
            
            # Удаляем старые записи с такими же данными
            history = [r for r in history if r["data"] != data]
            
            # Добавляем новую запись
            history.append(new_record)
            
            # Сохраняем только последние 50 записей (чтобы история не разрасталась)
            history = history[-50:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=4)
            return True
        except Exception as e:
            print(f"Ошибка добавления записи: {e}")
            return False
    
    def get_records(self):
        """Возвращает все записи из истории"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def clear_history(self):
        """Очищает историю"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
                return True
        except Exception as e:
            print(f"Ошибка очистки истории: {e}")
        return False


class HistoryDialog(QDialog):
    itemClicked = pyqtSignal(dict)  # Сигнал при клике на элемент
    
    def __init__(self, parent, history_manager):
        super().__init__(parent)
        self.parent = parent
        self.history = history_manager
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("История QR-кодов")
        self.setMinimumSize(500, 400)
        
        # Стили для диалога
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            .title-label {
                font-size: 18px;
                font-weight: bold;
                color: #2d3748;
                padding-bottom: 10px;
                border-bottom: 1px solid #e2e8f0;
            }
            .history-item {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                margin: 5px;
                padding: 10px;
            }
            .history-item:hover {
                border: 1px solid #cbd5e1;
                background-color: #f1f5f9;
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
            .clear-button {
                background-color: #fee2e2;
                color: #b91c1c;
                border-radius: 4px;
                padding: 5px 10px;
            }
            .close-button {
                background-color: #e0e7ff;
                color: #4338ca;
                border-radius: 4px;
                padding: 5px 10px;
            }
        """)
        
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
        records = self.history.get_records()
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
        status_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 14px;
                font-style: italic;
                padding: 20px;
                text-align: center;
            }
        """)
        self.container_layout.addWidget(status_label)
    
    def clear_history(self):
        """Очищает историю"""
        if self.history.clear_history():
            self.container_layout.clear()
            manager = HistoryManager()
            manager.clear_history()
            self.show_status_message("История очищена")
            QMessageBox.information(self, "Успех", "История успешно очищена")
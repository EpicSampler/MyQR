from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QLineEdit, QComboBox, QApplication, 
                            QSpinBox, QMessageBox, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
import pandas as pd
import os
from create_qr import QR
import shutil
from PyQt5.QtWidgets import QProgressDialog 

class PackGenerate(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Массовое создание QR-кодов")
        self.setMinimumSize(600, 500)
        
        self.csv_data = None
        self.output_folder = None
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка ui"""
        main_layout = QVBoxLayout()
        
        import_layout = QHBoxLayout()
        self.import_btn = QPushButton("Импортировать CSV файл")
        self.import_btn.setProperty("class", "clear-button")
        self.import_btn.clicked.connect(self.import_csv)
        import_layout.addWidget(self.import_btn)
        
        main_layout.addLayout(import_layout)
        
        self.preview_label = QLabel("Данные для генерации:")
        self.preview_label.setProperty("class", "title-label")
        main_layout.addWidget(self.preview_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.preview_content = QLabel()
        self.preview_content.setAlignment(Qt.AlignLeft)
        self.preview_content.setWordWrap(True)
        scroll.setWidget(self.preview_content)
        main_layout.addWidget(scroll)
        
        style_label = QLabel("Настройки стиля:")
        style_label.setProperty("class", "title-label")
        main_layout.addWidget(style_label)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Фон:"))
        self.color_input = QLineEdit("White")
        self.color_input.setPlaceholderText("White")
        color_layout.addWidget(self.color_input)
        
        color_layout.addWidget(QLabel("Цвет:"))
        self.bg_color_input = QLineEdit("Black")
        self.bg_color_input.setPlaceholderText("Black")
        color_layout.addWidget(self.bg_color_input)
        
        main_layout.addLayout(color_layout)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Масштаб:"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(1, 100)
        self.scale_spin.setValue(20)
        size_layout.addWidget(self.scale_spin)
        
        size_layout.addWidget(QLabel("Границы:"))
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 20)
        self.border_spin.setValue(4)
        size_layout.addWidget(self.border_spin)
        
        main_layout.addLayout(size_layout)
        
        self.size_combo = QComboBox()
        self.size_combo.addItem("Обычный QR", False)
        self.size_combo.addItem("Micro-QR", True)
        main_layout.addWidget(self.size_combo)
        
        self.generate_btn = QPushButton("Начать пакетную генерацию")
        self.generate_btn.setProperty("class", "close-button")
        self.generate_btn.clicked.connect(self.start_generation)
        self.generate_btn.setEnabled(False)
        main_layout.addWidget(self.generate_btn)
        
        self.setLayout(main_layout)
        
        self.setStyleSheet(self.parent.styleSheet())
    
    def import_csv(self):
        """Импорт CSV файла с данными"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите CSV файл",
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return
                
            self.csv_data = pd.read_csv(file_path)
            
            if len(self.csv_data) == 0:
                QMessageBox.warning(self, "Ошибка", "CSV файл не содержит данных")
                return
                
            if 'data' not in self.csv_data.columns:
                QMessageBox.warning(self, "Ошибка", "CSV должен содержать колонку 'data'")
                return
                
            preview_text = "Будет создано QR-кодов: {}\n\nЗаписи:\n".format(len(self.csv_data))
            preview_text += "\n".join([f"{i+1}. {row['data']}" for i, row in self.csv_data.head(len(self.csv_data)).iterrows()])
                
            self.preview_content.setText(preview_text)
            self.generate_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить CSV файл:\n{str(e)}")

    def start_generation(self):
        """генерация qr кодов"""
        try:
            if self.csv_data is None or len(self.csv_data) == 0:
                QMessageBox.warning(self, "Ошибка", "Нет данных для генерации")
                return
                
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "Выберите папку для сохранения QR-кодов",
                "",
                QFileDialog.ShowDirsOnly
            )
            
            if not folder_path:
                return
                
            self.output_folder = folder_path
            
            params = {
                'color': self.color_input.text() or "Black",
                'bg_color': self.bg_color_input.text() or "White",
                'scale': self.scale_spin.value(),
                'border': self.border_spin.value(),
                'is_big': self.size_combo.currentData()
            }
            
            os.makedirs(self.output_folder, exist_ok=True)

            progress = QProgressDialog(
                "Создание QR-кодов...", 
                "Отмена", 
                0, 
                len(self.csv_data), 
                self
            )
            progress.setWindowTitle("Генерация QR-кодов")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            qr = QR()
            success_count = 0
            errors = []
            
            for i, row in self.csv_data.iterrows():
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                QApplication.processEvents()  
                
                try:
                    data = str(row['data'])
                    filename = f"{i+1}.png"
                    full_path = os.path.join(self.output_folder, filename)
                    
                    result = qr.make(
                        data=data,
                        is_image=False,
                        size=params['is_big'],
                        scale=params['scale'],
                        border=params['border'],
                        background_color=params['bg_color'],
                        color=params['color']
                    )
                    
                    if result[0]:
                        temp_path = "qrs/qr.png"
                        if os.path.exists(temp_path):
                            shutil.move(temp_path, full_path)
                            success_count += 1
                        else:
                            errors.append(f"Файл не создан для {data}")
                    else:
                        errors.append(f"Ошибка создания: {result[1]}")
                        
                except Exception as e:
                    errors.append(f"Ошибка в строке {i+1}: {str(e)}")
                    continue
                    
            progress.close()
            
            report = f"Успешно создано: {success_count}/{len(self.csv_data)}"
            if errors:
                report += "\n\nОшибки:\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    report += f"\n...и еще {len(errors)-10} ошибок"

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Результат")
            msg_box.setText(report + f"\n\nФайлы сохранены в:\n{self.output_folder}")
            msg_box.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{str(e)}")
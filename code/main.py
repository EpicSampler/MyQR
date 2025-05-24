try:
    import sys
    import os
    import shutil
    import traceback
    from ui import Ui_MainWindow
    from create_qr import QR
    from print_window import A4Editor
    from donate import DonationDialog
    import segno
    import rsa
    from history import HistoryManager, HistoryDialog

    from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog)
    from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
    from PyQt5.QtCore import Qt
    print("Все зависимости установлены")
except ImportError as e:
    print(f"Ошибка: {e}. Установите: pip install")
    exit(1)

class MyApp(QMainWindow):  
    def __init__(self):
        super().__init__()
        try:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)  
            self.ui.label_2.setText('')
            
            self.history = HistoryManager()

            self.data = None
            self.maked = False
            self.current_type = 0 
            self.is_image = None
            self.choosed_data = None
            self.is_big = False
            self.current_file = "qrs/qr.png"
            self.scale = 20
            self.borders = 5
            self.bg_color = 'Black'
            self.color = 'White'

            self.current_style = {
            "scale": self.scale,
            "borders": self.borders,
            "bg_color": self.bg_color,
            "color": self.color,
            "is_big": self.is_big
        }

            # Сброс параметров по умолчанию
            self.ui.spinBox.setValue(self.scale)
            self.ui.lineEdit_2.setText(self.bg_color)
            self.ui.lineEdit_3.setText(self.color)
            self.ui.spinBox_2.setValue(self.borders)
            if self.is_big:
                self.ui.radioButton_2.setChecked(True)
            else:
                self.ui.radioButton.setChecked(True)
            
            self.hist = HistoryManager()

            # Устанавливаем стили с классами
            self.setStyleSheet("""
                /* ===== Основные стили ===== */
                QMainWindow, QDialog {
                    background-color: #f8fafc;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #2d3748;
                }

                /* ===== Заголовки ===== */
                .title-label {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2d3748;
                    border-bottom: 1px solid #e2e8f0;
                }

                .subtitle {
                    font-size: 14px;
                    color: #4a5568;
                }

                /* ===== Кнопки ===== */
                QPushButton {
                    background-color: #e2e8f0;
                    color: #2d3748;
                    border: none;
                    border-radius: 6px;
                    font-weight: 500;
                    min-width: 100px;
                }

                QPushButton:hover {
                    background-color: #cbd5e1;
                }

                QPushButton:pressed {
                    background-color: #94a3b8;
                }

                .clear-button {
                    background-color: #fee2e2;
                    color: #b91c1c;
                    min-height: 30px;
                    min-width: 100px;
                }

                .frame {
                    border: 1px solid black;
                    border-radius: 6px;
                }

                .clear-button:hover {
                    background-color: #fecaca;
                    min-height: 30px;
                    min-width: 100px;
                }

                .close-button {
                    background-color: #e0e7ff;
                    color: #4338ca;
                    min-height: 30px;
                    min-width: 100px;
                }

                .close-button:hover {
                    background-color: #c7d2fe;
                    min-height: 30px;
                    min-width: 100px;
                }

                /* ===== Поля ввода ===== */
                QLineEdit, QTextEdit, QComboBox {
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    background: white;
                }

                QLineEdit:focus, QTextEdit:focus {
                    border: 1px solid #93c5fd;
                }

                /* ===== Спинбоксы ===== */
                QSpinBox {
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    background: white;
                }

                /* ===== Радиокнопки ===== */
                QRadioButton {
                    spacing: 4px;
                    color: #2d3748;
                    font-size: 12px;
                }
                QRadioButton {
                    spacing: 4px;
                    color: #2d3748;
                    font-size: 12px;
                    margin: 0;
                }
                
                QRadioButton::indicator {
                    width: 14px;
                    height: 14px;
                    border: 1px solid #cbd5e1;
                    border-radius: 7px;
                    background: white;
                }
                
                QRadioButton::indicator:hover {
                    border: 1px solid #93c5fd;
                }
                
                QRadioButton::indicator:checked {
                    border: 1px solid #2563eb;
                    background: qradialgradient(
                        cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5,
                        stop:0.6 white,
                        stop:0.65 #2563eb,
                        stop:1 #2563eb
                    );
                }
                
                QRadioButton::indicator:checked:hover {
                    border: 1px solid #3b82f6;
                    background: qradialgradient(
                        cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5,
                        stop:0.6 white,
                        stop:0.65 #3b82f6,
                        stop:1 #3b82f6
                    );
                }
                
                QRadioButton::indicator:checked:pressed {
                    border: 1px solid #1d4ed8;
                    background: qradialgradient(
                        cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5,
                        stop:0.6 white,
                        stop:0.65 #1d4ed8,
                        stop:1 #1d4ed8
                    );
                }
                /* ===== Область с прокруткой ===== */
                QScrollArea {
                    border: none;
                    background: transparent;
                }

                QScrollBar:vertical {
                    border: none;
                    background: #e2e8f0;
                    width: 10px;
                    margin: 0px;
                }

                QScrollBar::handle:vertical {
                    background: #cbd5e1;
                    min-height: 20px;
                    border-radius: 4px;
                }

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }

                /* ===== Сообщения ===== */
                .empty-message {
                    color: #64748b;
                    font-size: 14px;
                    padding: 20px;
                    text-align: center;
                }

                /* ===== Меню ===== */
                QMenuBar {
                    background-color: #ffffff;
                }

                QMenuBar::item {
                    background: transparent;
                }

                QMenuBar::item:selected {
                    background: #e2e8f0;
                    border-radius: 4px;
                }

                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                }

                QMenu::item:selected {
                    background-color: #e2e8f0;
                }
            """)

            # Применяем классы к элементам
            self.ui.label_8.setProperty('class', 'title-label')
            self.ui.labelText_or_ss.setProperty('class', 'title-label')
            self.ui.label_2.setProperty('class', 'frame')
            self.ui.frame.setProperty('class', 'frame')
            
            # Устанавливаем иконки с проверкой
            icon_path = "files/logo.png"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                QApplication.setWindowIcon(QIcon(icon_path))
            else:
                QMessageBox.warning(self, "Предупреждение", "Файл иконки не найден")

            self.setup_connections()
        except Exception as e:
            self.show_error("Ошибка инициализации", str(e))
            sys.exit(1)

    # def test_history_system(self):
    #     """Тестирование системы истории"""
    #     print("\n=== ТЕСТИРОВАНИЕ ИСТОРИИ ===")
        
    #     # Тестовая запись
    #     test_data = "test_" + str(datetime.now().timestamp())
    #     print(f"Добавляем тестовую запись: {test_data}")
    #     self.history.add_record(test_data)
        
    #     # Чтение записей
    #     records = self.history.get_records()
    #     print(f"Найдено записей: {len(records)}")
        
    #     if records:
    #         print("Последняя запись:", records[-1][1])
    #         if records[-1][1] != test_data:
    #             print("ОШИБКА: Данные не совпадают!")
    #         else:
    #             print("Тест пройден успешно!")
    #     else:
    #         print("ОШИБКА: Записи не найдены!")
        
    #     print("=======================\n")

    def show_error(self, title, message):
        """Показывает сообщение об ошибке и логирует её"""
        error_msg = f"{title}\n{message}\n\n{traceback.format_exc()}"
        print(error_msg)  # Логирование в консоль
        QMessageBox.critical(self, title, message)
        return [False, message]

    def show_success(self, message):
        """Показывает сообщение об успехе"""
        QMessageBox.information(self, "Успех", message)
        return [True, message]

    def setup_connections(self):
        """Безопасное подключение сигналов"""
        try:
            self.ui.action_2.triggered.connect(self.save_as)
            self.ui.action_2.setShortcut(QKeySequence("Ctrl+S"))
            self.ui.pushButton_2.clicked.connect(self.save_as)
            self.ui.comboBox.currentIndexChanged.connect(self.__upd_list__)
            self.ui.pushButton.clicked.connect(self.make_qr)  # кнопка создать
            self.ui.pushButton_3.clicked.connect(self.set_style)  # кнопка установить стиль
            self.ui.spinBox.valueChanged.connect(self.__upd_spinboxes__)  # спинбокс масштаб
            self.ui.spinBox_2.valueChanged.connect(self.__upd_spinboxes__)  # спинбокс размер границы
            self.ui.lineEdit_2.textEdited.connect(self.__upd_line_edits__)  # поле ввода заднего цвета
            self.ui.lineEdit_3.textEdited.connect(self.__upd_line_edits__)  # поле ввода переднего цвета
            self.ui.lineEdit_2.textChanged.connect(self.__upd_line_edits__)  # поле ввода заднего текста
            self.ui.lineEdit_3.textChanged.connect(self.__upd_line_edits__)  # поле ввода переднего текста
            self.ui.action_6.triggered.connect(self.printer)
            self.ui.action_6.setShortcut(QKeySequence("Ctrl+P"))
            self.ui.pushButton_4.clicked.connect(self.printer)
            self.ui.radioButton.clicked.connect(self.__upd_radio__)
            self.ui.radioButton_2.clicked.connect(self.__upd_radio__)
            self.ui.action_7.triggered.connect(self.show_donation_dialog)
            self.ui.action_8.triggered.connect(self.show_history)
                
            
        except Exception as e:
            self.show_error("Ошибка подключения сигналов", str(e))

    def __upd_spinboxes__(self):
        """Обновляет параметры стиля при изменении спинбоксов"""
        try:
            self.current_style["scale"] = self.ui.spinBox.value()
            self.current_style["borders"] = self.ui.spinBox_2.value()
            return [True, "Параметры масштабирования обновлены"]
        except Exception as e:
            return self.show_error("Ошибка обновления спинбоксов", str(e))

    def __upd_line_edits__(self):
        """Обновляет параметры стиля при изменении цветов"""
        try:
            self.current_style["bg_color"] = self.ui.lineEdit_2.text()
            self.current_style["color"] = self.ui.lineEdit_3.text()
            return [True, "Цвета обновлены"]
        except Exception as e:
            return self.show_error("Ошибка обновления цветов", str(e))

    def __upd_radio__(self):
        """Обновляет параметр размера при изменении радиокнопок"""
        radio_check_1 = self.ui.radioButton.isChecked()
        radio_check_2 = self.ui.radioButton_2.isChecked()
        self.current_style["is_big"] = not (radio_check_1 and not radio_check_2)
    
    def __change_line_edit__(self, to_do: bool = False):
        if to_do:
            self.ui.lineEdit.hide()
        else:
            self.ui.lineEdit.show()

    
    def __upd_list__(self):
        try:
            self.current_type = self.ui.comboBox.currentIndex()
            
            # Сбрасываем флаг maked перед обновлением данных
            self.maked = False
            
            if self.current_type == 0:  # Текст/ссылка
                self.is_image = False
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Вставьте текст или ссылку')
                
            elif self.current_type == 1:  # Изображение
                self.is_image = True
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Вставьте расположение файла')
                
            elif self.current_type == 2:  # Email
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Введите адрес почты и тему письма')
                
            elif self.current_type == 3:  # SMS
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Введите номер телефона и текст сообщения')
                
            elif self.current_type == 4:  # Телефон
                self.is_image = False
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Введите номер телефона')
                
            elif self.current_type == 5:  # Контакт
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Введите номер телефона и имя')
                
            elif self.current_type == 6:  # Геолокация
                self.is_image = False
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Введите географические координаты')
                
            elif self.current_type == 7:  # WiFi
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                self.ui.labelText_or_ss.setText('Введите SSID сети и пароль')
            #elif check == 8:
            #     self.is_image = False
            #     self.__change_line_edit__(True)
            #     self.choosed_data = self.ui.comboBox.currentText()
            #     print(self.choosed_data)
            #     self.ui.labelText_or_ss.setText('Введите начало и окончание события в формате (ГГГГММДД ЧЧММСС) и название события')
            #     name = self.ui.lineEdit_4.text()
            #     if self.maked:
            #         self.data = f''
            #     print(self.data)    
            return [True, "Тип ввода обновлен"]
        except Exception as e:
            return self.show_error("Ошибка обновления метки", str(e))

    def __prepare_data(self):
        """Подготавливает данные в зависимости от выбранного типа"""
        try:
            if self.current_type == 0:  # Текст/ссылка
                self.data = self.ui.lineEdit.text()
                
            elif self.current_type == 1:  # Изображение
                self.data = self.ui.lineEdit.text()
                
            elif self.current_type == 2:  # Email
                mail = self.ui.lineEdit_4.text()
                text = self.ui.lineEdit_5.text()
                if mail and text:
                    self.data = f'mailto:{mail}?body={text}&subject=Тема'
                    
            elif self.current_type == 3:  # SMS
                phone = self.ui.lineEdit_4.text()
                text = self.ui.lineEdit_5.text()
                if phone and text:
                    self.data = f'smsto:{phone}?body={text}'
                    
            elif self.current_type == 4:  # Телефон
                phone = self.ui.lineEdit.text()
                if phone:
                    self.data = f'tel:{phone}'
                    
            elif self.current_type == 5:  # Контакт
                phone = self.ui.lineEdit_4.text()
                name = self.ui.lineEdit_5.text()
                if phone and name:
                    self.data = f'BEGIN:VCARD\nVERSION:3.0\nN:{name};;;\nTEL:{phone}\nEND:VCARD'
                    
            elif self.current_type == 6:  # Геолокация
                text = self.ui.lineEdit.text()
                if text:
                    self.data = f'geo:{text}'
                    
            elif self.current_type == 7:  # WiFi
                ssid = self.ui.lineEdit_4.text()
                password = self.ui.lineEdit_5.text()
                if ssid and password:
                    self.data = f'WIFI:T:WPA;S:{ssid};P:{password};;'
                    
            if not self.data:
                return [False, "Введите данные для QR-кода"]
                
            return [True, "Данные подготовлены"]
            
        except Exception as e:
            return [False, f"Ошибка подготовки данных: {str(e)}"]            
    
    def show_history(self):
        """Показывает окно истории"""
        dialog = HistoryDialog(self, self.history)
        dialog.itemClicked.connect(self.apply_history_item)
        dialog.exec_()
    
    def apply_history_item(self, item):
        """Применяет данные и стиль из истории"""
        try:
            # Устанавливаем данные
            self.ui.lineEdit.setText(item["data"])
            self.data = item["data"]
            
            # Применяем сохраненный стиль
            if "style" in item:
                style = item["style"]
                self.ui.spinBox.setValue(style.get("scale", 20))
                self.ui.spinBox_2.setValue(style.get("borders", 5))
                self.ui.lineEdit_2.setText(style.get("bg_color", "Black"))
                self.ui.lineEdit_3.setText(style.get("color", "White"))
                self.ui.radioButton.setChecked(not style.get("is_big", False))
                self.ui.radioButton_2.setChecked(style.get("is_big", False))
                
                # Обновляем внутренние переменные
                self.scale = style.get("scale", 20)
                self.borders = style.get("borders", 5)
                self.bg_color = style.get("bg_color", "Black")
                self.color = style.get("color", "White")
                self.is_big = style.get("is_big", False)
            
            # Создаем QR-код
            self.make_qr()
            
        except Exception as e:
            self.show_error("Ошибка применения истории", str(e))

    def make_qr(self):
        """Создает QR-код с текущими параметрами стиля"""
        try:
            # Подготавливаем данные
            result = self.__prepare_data()
            if not result[0]:
                return self.show_error("Ошибка", result[1])
            
            # Применяем текущий стиль перед созданием
            self.scale = self.current_style["scale"]
            self.borders = self.current_style["borders"]
            self.bg_color = self.current_style["bg_color"]
            self.color = self.current_style["color"]
            self.is_big = self.current_style["is_big"]
            
            # Создаем QR-код с текущим стилем
            result = create.make(
                data=self.data, 
                is_image=self.is_image, 
                size=self.is_big,
                scale=self.scale,
                border=self.borders,
                background_color=self.bg_color,
                color=self.color
            )
            
            if not result[0]:
                return result

            # Показываем QR-код
            pixmap = QPixmap("qrs/qr.png")
            if pixmap.isNull():
                return self.show_error("Ошибка", "Не удалось загрузить изображение QR-кода")
                
            pixmap = pixmap.scaled(
                self.ui.label_2.width(), 
                self.ui.label_2.height(),
                Qt.KeepAspectRatio,  
                Qt.SmoothTransformation  
            )
            self.ui.label_2.setPixmap(pixmap)
            
            # Сохраняем в историю с текущим стилем и типом
            record = {
                "data": self.data,
                "style": self.current_style.copy(),
                "type": self.current_type
            }
            self.history.add_record(record)
            
            self.maked = True
            return self.show_success("QR-код успешно создан")
            
        except Exception as e:
            return self.show_error("Ошибка создания QR-кода", str(e))

    def set_style(self):
        """Применяет стиль к уже созданному QR-коду"""
        try:
            if not os.path.exists("qrs/qr.png"):
                return self.show_error("Ошибка", "Сначала создайте QR-код")

            # Обновляем текущий стиль из полей ввода
            self.current_style = {
                "scale": self.ui.spinBox.value(),
                "borders": self.ui.spinBox_2.value(),
                "bg_color": self.ui.lineEdit_2.text(),
                "color": self.ui.lineEdit_3.text(),
                "is_big": self.ui.radioButton_2.isChecked()
            }

            result = create.save_with_style(
                background_color=self.current_style["bg_color"],
                color=self.current_style["color"],
                border=self.current_style["borders"],
                scale=self.current_style["scale"],
                size=self.current_style["is_big"]
            )
            
            if not result[0]:
                return result

            # Обновляем отображение
            pixmap = QPixmap("qrs/qr.png")
            pixmap = pixmap.scaled(
                self.ui.label_2.width(), 
                self.ui.label_2.height(),
                Qt.KeepAspectRatio,  
                Qt.SmoothTransformation  
            )
            self.ui.label_2.setPixmap(pixmap)
            
            return self.show_success("Стиль QR-кода успешно применен")
        except Exception as e:
            return self.show_error("Ошибка применения стиля", str(e))

    def save_as(self):
        try:
            if not os.path.exists(self.current_file):
                return self.show_error("Ошибка", "Сначала создайте QR-код")

            user = os.getlogin()
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,                  
                "Сохранить QR код",       
                f"C:\\Users\\{user}\\Documents\\MyQR.png",                     
                "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;ICO Image (*.ico);;Все файлы (*)"  
            )
            
            if not file_path:
                return [True, "Сохранение отменено"]

            # Автоматическое добавление расширения
            if selected_filter == "PNG Image (*.png)" and not file_path.lower().endswith('.png'):
                file_path += '.png'
            elif selected_filter == "JPEG Image (*.jpg *.jpeg)":
                if not any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg']):
                    file_path += '.jpg'
            elif selected_filter == "ICO Image (*.ico)" and not file_path.lower().endswith('.ico'):
                file_path += '.ico'
            
            try:
                shutil.copy2(self.current_file, file_path)
                self.ui.label.setText('✅Файл успешно сохранен')
                return self.show_success(f"QR-код успешно сохранен:\n{file_path}")
            except Exception as e:
                self.ui.label.setText('❌Не удалось сохранить файл')
                return self.show_error("Ошибка сохранения файла", str(e))
        except Exception as e:
            self.ui.label.setText('❌Не удалось сохранить файл')
            return self.show_error("Ошибка при сохранении", str(e))
    
    def printer(self):
        try:
            if not os.path.exists("qrs/qr.png"):
                return self.show_error("Ошибка", "Сначала создайте QR-код")
            
            # Создаем и настраиваем редактор
            editor = A4Editor(self)
            editor.setWindowTitle("Печать QR-кода")
            
            # Загружаем изображение
            if not editor.load_image("qrs/qr.png"):
                return self.show_error("Ошибка", "Не удалось загрузить QR-код")
            
            # Показываем как модальное окно
            if editor.exec_() == QDialog.Accepted:
                self.ui.label.setText("✅ QR-код подготовлен к печати")
            else:
                self.ui.label.setText("Печать отменена")
                
        except Exception as e:
            return self.show_error("Ошибка печати", str(e))


    def show_donation_dialog(self):
        dialog = DonationDialog(self)
        dialog.exec_()

# Проверка папок
for folder in ["qrs", "files", "files/crypto_keys"]:
    os.makedirs(folder, exist_ok=True)
    print(f"Папка {folder}: {os.path.abspath(folder)}")

if __name__ == "__main__":
    try:
        create = QR()
        app = QApplication(sys.argv)
        window = MyApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Критическая ошибка", 
                           f"Приложение не может быть запущено:\n{str(e)}\n\n{traceback.format_exc()}")
        sys.exit(1)


#Красивый QR код
#DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDdDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
#Pochep 52.912193,33.470974

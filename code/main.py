try:
    import sys
    import os
    import shutil
    import traceback
    from ui import Ui_MainWindow
    from create_qr import QR
    from print_window import A4Editor
    from donate import DonationDialog
    import resources
    import segno
    import rsa
    from history import HistoryManager, HistoryDialog

    # import sip
    # sip.setapi('QVariant', 2)
    # sip.setapi('QString', 2)

    from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog)
    from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
    # from PyQt5.QtWidgets import QLabel
    from PyQt5.QtCore import Qt #, QFile, QTextStream
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
            # self.test_history_system()

            self.data = None
            self.maked = False

            self.is_image = None
            self.choosed_data = None
            self.is_big = False
            self.current_file = "qrs/qr.png"
            self.scale = 20
            self.borders = 5
            self.bg_color = 'Black'
            self.color = 'White'

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

    def __upd_radio__(self):
        radio_check_1 = self.ui.radioButton.isChecked()
        radio_check_2 = self.ui.radioButton_2.isChecked()
        self.is_big = False if radio_check_1 and not radio_check_2 else True
    
    def __change_line_edit__(self, to_do: bool = False):
        if to_do:
            self.ui.lineEdit.hide()
        else:
            self.ui.lineEdit.show()

    
    def __upd_list__(self):
        try:
            check = self.ui.comboBox.currentIndex()
            if check == 0:
                self.is_image = False
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                self.data = self.ui.lineEdit.text()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Вставьте текст или ссылку')
            elif check == 1:
                self.is_image = True
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                self.data = self.ui.lineEdit.text()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Вставьте расположение файла')
            elif check == 2:
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Введите адрес почты и тему письма')
                mail = self.ui.lineEdit_4.text()
                text = self.ui.lineEdit_5.text()
                if self.maked and mail != '' and text != '':
                    self.data = f'mailto:{mail}?body={text}&subject=Тема'
                print(self.data)
            elif check == 3:
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Введите номер телефона и текст сообщения')
                phone = self.ui.lineEdit_4.text()
                text = self.ui.lineEdit_5.text()
                if self.maked and phone != '' and text != '':
                    self.data = f'smsto:{phone}?body={text}'
            elif check == 4:
                self.is_image = False
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Введите номер телефона')
                phone = self.ui.lineEdit.text()
                if self.maked and phone != '':
                    self.data = f'tel:{phone}'
                print(self.data)
            elif check == 5:
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Введите номер телефона и имя')
                phone = self.ui.lineEdit_4.text()
                name = self.ui.lineEdit_5.text()
                if self.maked and phone != '' and name != '':
                    self.data = f'BEGIN:VCARD\nVERSION:3.0\nN:{name};;;\nTEL:{phone}\nEND:VCARD'
                print(self.data)
            elif check == 6:
                self.is_image = False
                self.__change_line_edit__()
                self.choosed_data = self.ui.comboBox.currentText()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Введите географические координаты (Пример: 52.912193,33.470974)')
                text = self.ui.lineEdit.text()
                if self.maked and text != '':
                    self.data = f'geo:{text}'
                print(self.data)
            elif check == 7:
                self.is_image = False
                self.__change_line_edit__(True)
                self.choosed_data = self.ui.comboBox.currentText()
                print(self.choosed_data)
                self.ui.labelText_or_ss.setText('Введите SSID сети и пароль')
                Password = self.ui.lineEdit_5.text()
                SSID = self.ui.lineEdit_4.text()
                print(Password, ' - ', SSID)
                if self.maked and Password != '' and SSID != '':
                    self.data = f'WIFI:T:WPA;S:{SSID};P:{Password};;'
                print(self.data)
            # elif check == 8:
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
    
    def show_history(self):
        """Показывает окно истории"""
        HistoryDialog(self, self.history).exec_()

    def __upd_spinboxes__(self):
        try:
            self.scale = self.ui.spinBox.value()
            self.borders = self.ui.spinBox_2.value()
            return [True, "Параметры масштабирования обновлены"]
        except Exception as e:
            return self.show_error("Ошибка обновления спинбоксов", str(e))

    def __upd_line_edits__(self):
        try:
            self.bg_color = self.ui.lineEdit_2.text()
            self.color = self.ui.lineEdit_3.text()
            return [True, "Цвета обновлены"]
        except Exception as e:
            return self.show_error("Ошибка обновления цветов", str(e))

    def make_qr(self):
        self.maked = True
        try:
            self.__upd_list__()
            if not self.data:
                return self.show_error("Ошибка", "Введите данные для QR-кода")

            # 1. Проверьте, что данные корректно передаются
            print(f"Данные для QR: {self.data}")  # Добавьте эту строку для отладки

            # 2. Проверьте работу create.make()
            result = create.make(data=self.data, is_image=self.is_image, size=self.is_big)
            if not result[0]:
                return result
            
            # 3. Проверьте существование файла
            print(f"Файл существует: {os.path.exists('qrs/qr.png')}")  # Отладочная строка
            
            if not os.path.exists("qrs/qr.png"):
                return self.show_error("Ошибка", "QR-код не был создан")

            # 4. Проверьте загрузку изображения
            pixmap = QPixmap("qrs/qr.png")
            print(f"Изображение загружено: {not pixmap.isNull()}")  # Отладочная строка
            self.history.add_record(self.data)
            
            if pixmap.isNull():
                return self.show_error("Ошибка", "Не удалось загрузить изображение QR-кода")

            # 5. Проверьте размеры label_2
            print(f"Размер label_2: {self.ui.label_2.width()}x{self.ui.label_2.height()}")  # Отладочная строка
            
            pixmap = pixmap.scaled(
                self.ui.label_2.width(), 
                self.ui.label_2.height(),
                Qt.KeepAspectRatio,  
                Qt.SmoothTransformation  
            )
            
            # 6. Убедитесь, что изображение устанавливается
            self.ui.label_2.setPixmap(pixmap)
            print("Изображение установлено в label_2")  # Отладочная строка


            # Сброс параметров
            self.ui.spinBox.setValue(20)
            self.ui.lineEdit_2.setText('Black')
            self.ui.lineEdit_3.setText('White')
            self.ui.spinBox_2.setValue(5)
            self.ui.radioButton_2.setChecked(self.is_big)

            self.maked = False
            return self.show_success("QR-код успешно создан")
        except Exception as e:
            return self.show_error("Ошибка создания QR-кода", str(e))

    def set_style(self):
        try:
            if not os.path.exists("qrs/qr.png"):
                return self.show_error("Ошибка", "Сначала создайте QR-код")

            result = create.save_with_style(
                background_color=self.bg_color,
                color=self.color,
                border=self.borders,
                scale=self.scale,
                size=self.is_big
            )
            if not result[0]:
                return result

            pixmap = QPixmap("qrs/qr.png")
            if pixmap.isNull():
                return self.show_error("Ошибка", "Не удалось загрузить стилизованное изображение")

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

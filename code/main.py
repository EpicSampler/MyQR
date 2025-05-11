import sys
import os
import shutil
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog)
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from ui import *
from create_qr import *
from print_window import *
from donate import DonationDialog

class MyApp(QMainWindow):  
    def __init__(self):
        super().__init__()
        try:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)  
            self.ui.label_2.setText('')


            self.is_image = None
            self.is_big = False
            self.current_file = "qrs/qr.png"
            self.scale = 20
            self.borders = 5
            self.bg_color = "Black"
            self.color = "White"

            # Устанавливаем иконки с проверкой
            icon_path = "files/logo.png"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                QApplication.setWindowIcon(QIcon(icon_path))
            else:
                QMessageBox.warning(self, "Предупреждение", "Файл иконки не найден")

            # Подключение слотов с обработкой ошибок
            self.setup_connections()
            
        except Exception as e:
            self.show_error("Ошибка инициализации", str(e))
            sys.exit(1)

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
            self.ui.comboBox.currentIndexChanged.connect(self.__upd_label__)
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
                
            
        except Exception as e:
            self.show_error("Ошибка подключения сигналов", str(e))

    def __upd_radio__(self):
        radio_check_1 = self.ui.radioButton.isChecked()
        radio_check_2 = self.ui.radioButton_2.isChecked()
        self.is_big = False if radio_check_1 and not radio_check_2 else True
    
    def __upd_label__(self):
        try:
            is_image_check = self.ui.comboBox.currentIndex()
            if is_image_check == 0:
                self.is_image = False
                self.ui.labelText_or_ss.setText('Вставьте текст или ссылку')
            elif is_image_check == 1:
                self.is_image = True
                self.ui.labelText_or_ss.setText('Вставьте расположение файла')
                self.ui.labelText_or_ss.setFixedWidth(500)
            return [True, "Тип ввода обновлен"]
        except Exception as e:
            return self.show_error("Ошибка обновления метки", str(e))

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
        try:
            data = self.ui.lineEdit.text()
            if not data:
                return self.show_error("Ошибка", "Введите данные для QR-кода")

            if self.is_image:
                if '\\' in data:
                    data = data.replace('\\', '/')
            
            result = create.make(data=data, is_image=self.is_image, size=self.is_big)
            if not result[0]:
                return result
            
            if not os.path.exists("qrs/qr.png"):
                return self.show_error("Ошибка", "QR-код не был создан")

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

            # Сброс параметров по умолчанию
            self.ui.spinBox.setValue(20)
            self.ui.lineEdit_2.setText('Black')
            self.ui.lineEdit_3.setText('White')
            self.ui.spinBox_2.setValue(5)
            self.ui.radioButton_2.setChecked(self.is_big)
            
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
        #     glorbo = printer.print_image('qrs/qr.png', scale_to_fit=False, dpi=1000)
        #     print(glorbo)
        #     if glorbo[0]:
        #         self.ui.label.setText(glorbo[1])
        #     if not glorbo[0]:
        #         self.ui.label.setText(glorbo[1])
        # except Exception as e:
        #     return self.show_error('Ошибка печати', str(e))
    

    def show_donation_dialog(self):
        dialog = DonationDialog(self)
        dialog.exec_()

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

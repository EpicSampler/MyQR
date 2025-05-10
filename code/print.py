# Импорт необходимых модулей
import win32print  # Для работы с принтерами Windows
import win32ui  # Для создания контекста устройства
import win32con  # Константы Windows API
import win32gui  # Функции GUI Windows
from PIL import Image  # Для работы с изображениями
import ctypes  # Для работы с низкоуровневыми структурами
from ctypes import wintypes  # Windows-специфичные типы данных

class ImagePrinter:
    def __init__(self):
        # Инициализация переменной для хранения контекста устройства печати
        self.hdc = None

    def print_image(self, image_path, printer_name=None, scale_to_fit=True, dpi=300):
        """Печатает изображение с настройками масштабирования и DPI"""
        try:
            # 1. Открытие и подготовка изображения
            img = Image.open(image_path)  # Открываем изображение
            if img.mode != 'RGB':  # Если изображение не в RGB формате
                img = img.convert('RGB')  # Конвертируем в RGB
            
            # 2. Настройка DPI изображения
            if dpi:  # Если указано значение DPI
                img = self._convert_dpi(img, dpi)  # Конвертируем DPI
            
            # Получаем размеры изображения и его бинарные данные
            width, height = img.size  # Ширина и высота изображения
            img_data = img.tobytes()  # Получаем байтовое представление изображения

            # 3. Настройка принтера
            # Используем принтер по умолчанию, если не указан конкретный
            printer_name = printer_name or win32print.GetDefaultPrinter()
            # Создаем контекст устройства (Device Context)
            self.hdc = win32ui.CreateDC()
            # Связываем контекст с конкретным принтером
            self.hdc.CreatePrinterDC(printer_name)
            
            # 4. Расчет размеров для печати
            if scale_to_fit:  # Если нужно масштабировать под размер страницы
                # Получаем физические размеры области печати
                printable_width = self.hdc.GetDeviceCaps(win32con.HORZRES)
                printable_height = self.hdc.GetDeviceCaps(win32con.VERTRES)
                # Вычисляем коэффициент масштабирования
                ratio = min(printable_width / width, printable_height / height)
                # Новые размеры с учетом масштабирования
                new_width, new_height = int(width * ratio), int(height * ratio)
            else:  # Если печатаем в оригинальном размере
                new_width, new_height = width, height

            # 5. Создание структуры BITMAPINFO для передачи данных изображения
            bmi = self._create_bitmapinfo(width, height, len(img_data))
            
            # 6. Процесс печати
            self.hdc.StartDoc(image_path)  # Начинаем документ
            self.hdc.StartPage()  # Начинаем страницу
            
            # Передаем данные изображения на печать с помощью Windows API
            ctypes.windll.gdi32.StretchDIBits(
                self.hdc.GetHandleOutput(),  # Контекст устройства вывода
                0, 0, new_width, new_height,  # Координаты и размер на странице
                0, 0, width, height,  # Область изображения для печати
                img_data,  # Байтовые данные изображения
                ctypes.byref(bmi),  # Ссылка на структуру BITMAPINFO
                win32con.DIB_RGB_COLORS,  # Используем RGB цвета
                win32con.SRCCOPY  # Копируем пиксели напрямую
            )
            
            # Завершаем страницу и документ
            self.hdc.EndPage()
            self.hdc.EndDoc()
            text = f"✅ Изображение отправлено на {printer_name}"
            print(text)
            return (True, text)

        except Exception as e:
            text = f"❌ Ошибка: {e}"
            print(text)
            return (False, text)
        finally:
            self._cleanup()  # Очищаем ресурсы

    def _convert_dpi(self, img, target_dpi):
        """Конвертирует изображение в указанный DPI"""
        img = img.copy()  # Создаем копию изображения
        img.info['dpi'] = (target_dpi, target_dpi)  # Устанавливаем DPI
        return img

    def _create_bitmapinfo(self, width, height, data_size):
        """Создаёт структуру BITMAPINFO для передачи изображения в Windows API"""
        # Определяем структуру BITMAPINFOHEADER
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [  # Поля структуры:
                ('biSize', wintypes.DWORD),  # Размер структуры
                ('biWidth', wintypes.LONG),  # Ширина изображения
                ('biHeight', wintypes.LONG),  # Высота изображения (отрицательная = top-down)
                ('biPlanes', wintypes.WORD),  # Количество цветовых плоскостей (1)
                ('biBitCount', wintypes.WORD),  # Бит на пиксель (24 для RGB)
                ('biCompression', wintypes.DWORD),  # Тип компрессии (BI_RGB)
                ('biSizeImage', wintypes.DWORD),  # Размер данных изображения
                ('biXPelsPerMeter', wintypes.LONG),  # Горизонтальное разрешение
                ('biYPelsPerMeter', wintypes.LONG),  # Вертикальное разрешение
                ('biClrUsed', wintypes.DWORD),  # Используемые цвета
                ('biClrImportant', wintypes.DWORD)  # Важные цвета
            ]

        # Создаем буфер для структуры
        bmi = ctypes.create_string_buffer(ctypes.sizeof(BITMAPINFOHEADER))
        # Заполняем поля структуры
        header = BITMAPINFOHEADER.from_buffer(bmi)
        header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        header.biWidth = width
        header.biHeight = -height  # Отрицательная высота = top-down изображение
        header.biPlanes = 1
        header.biBitCount = 24  # 24 бита на пиксель (RGB)
        header.biCompression = win32con.BI_RGB  # Без сжатия
        header.biSizeImage = data_size  # Размер данных изображения
        return header

    def _cleanup(self):
        """Очистка ресурсов - освобождает контекст устройства"""
        if self.hdc:  # Если контекст устройства существует
            self.hdc.DeleteDC()  # Удаляем контекст
            self.hdc = None  # Обнуляем ссылку

# Пример использования
    #printer = ImagePrinter()  # Создаем экземпляр принтера
    
    # # Варианты использования:
    # # 1. Печать с масштабированием под страницу (по умолчанию)
    # # printer.print_image("qrs/qr.png") 
    
    # # 2. Печать в оригинальном размере (300 DPI)
    # printer.print_image("qrs/qr.png", scale_to_fit=False, dpi=300)
    
    # # 3. Печать на конкретном принтере
    # # printer.print_image("label.png", printer_name="Brother QL-720NW")
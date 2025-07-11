
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene, 
                            QGraphicsPixmapItem, QToolBar, QAction, QDialogButtonBox,
                            QSpinBox, QLabel, QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPixmap, QPainter, QPageSize, QImage, QTransform
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

class A4Editor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактор для печати на А4")
        self.setMinimumSize(500, 700)
        
        # Инициализация атрибутов
        self.image_item = None
        self.current_scale = 1.0
        self.current_rotation = 0
        self.dpi = 300  # Разрешение для печати
        
        # Настройка графической сцены
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Настройка страницы А4
        self.page_size = QPageSize(QPageSize.A4)
        self.page_rect = self.calculate_page_rect()
        
        # Настройка инструментов
        self.setup_toolbar()
        
        # Основная компоновка
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.view)
        
        # Кнопки диалога
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setProperty("class", "close-button")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.init_scene()

    def calculate_page_rect(self):
        """Вычисление размеров страницы в пикселях"""
        size_mm = self.page_size.size(QPageSize.Millimeter)
        width_px = (size_mm.width() / 25.4) * self.dpi
        height_px = (size_mm.height() / 25.4) * self.dpi
        return QRectF(0, 0, width_px, height_px)

    def setup_toolbar(self):
        """Настройка панели инструментов"""
        self.toolbar = QToolBar()
        
        # Масштабирование
        self.toolbar.addWidget(QLabel("Масштаб:"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(10, 500)
        self.scale_spin.setValue(100)
        self.scale_spin.setSuffix("%")
        self.scale_spin.valueChanged.connect(self.scale_image)
        self.toolbar.addWidget(self.scale_spin)
        
        # Поворот
        rotate_left = QAction("↺", self)
        rotate_left.triggered.connect(lambda: self.rotate_image(-90))
        self.toolbar.addAction(rotate_left)
        
        rotate_right = QAction("↻", self)
        rotate_right.triggered.connect(lambda: self.rotate_image(90))
        self.toolbar.addAction(rotate_right)
        
        # Печать
        print_action = QAction("Печать", self)
        print_action.triggered.connect(self.print_image)
        self.toolbar.addAction(print_action)

    def init_scene(self):
        """Инициализация сцены с фоном А4"""
        self.scene.clear()
        # Серый фон для страницы А4 (только для предпросмотра)
        self.scene.addRect(self.page_rect, Qt.black, Qt.lightGray)
        self.scene.setSceneRect(self.page_rect)
        self.view.fitInView(self.page_rect, Qt.KeepAspectRatio)

    def load_image(self, file_path):
        """Загрузка изображения на сцену"""
        self.init_scene()  # Очищаем сцену перед загрузкой
        
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return False
            
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.image_item.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        self.image_item.setFlag(QGraphicsPixmapItem.ItemIsSelectable)
        self.image_item.setTransformationMode(Qt.SmoothTransformation)
        
        self.scene.addItem(self.image_item)
        self.center_image()
        self.scale_spin.setValue(100)
        self.current_rotation = 0
        return True

    def center_image(self):
        """Центрирование изображения на странице"""
        if self.image_item:
            img_rect = self.image_item.boundingRect()
            page_center = self.page_rect.center()
            img_center = img_rect.center()
            self.image_item.setPos(page_center - img_center)

    def scale_image(self, value):
        """Масштабирование изображения"""
        if self.image_item:
            scale_factor = value / 100.0
            transform = QTransform()
            transform.scale(scale_factor, scale_factor)
            transform.rotate(self.current_rotation)
            self.image_item.setTransform(transform)
            self.current_scale = scale_factor

    def rotate_image(self, angle):
        """Поворот изображения"""
        if self.image_item:
            self.current_rotation += angle
            transform = QTransform()
            transform.scale(self.current_scale, self.current_scale)
            transform.rotate(self.current_rotation)
            self.image_item.setTransform(transform)

    def print_image(self):
        """Печать с точным сохранением масштаба и позиции"""
        if not self.image_item:
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setFullPage(True)
        printer.setResolution(self.dpi)  # Устанавливаем DPI

        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # Получаем оригинальный pixmap
            original_pixmap = self.image_item.pixmap()
            
            # Получаем позицию и размеры изображения на сцене
            scene_pos = self.image_item.pos()
            scaled_width = original_pixmap.width() * self.current_scale
            scaled_height = original_pixmap.height() * self.current_scale
            
            # Вычисляем соотношение между виртуальной страницей и реальной
            page_rect = printer.pageRect(QPrinter.DevicePixel)
            scale_x = page_rect.width() / self.page_rect.width()
            scale_y = page_rect.height() / self.page_rect.height()
            
            # Масштабируем позицию и размеры
            print_x = scene_pos.x() * scale_x
            print_y = scene_pos.y() * scale_y
            print_width = scaled_width * scale_x
            print_height = scaled_height * scale_y
            
            # Создаем целевую область для печати
            target_rect = QRectF(print_x, print_y, print_width, print_height)
            
            # Рисуем изображение с учетом поворота
            painter.save()
            painter.translate(target_rect.center())
            painter.rotate(self.current_rotation)
            painter.translate(-target_rect.width()/2, -target_rect.height()/2)
            
            # Масштабируем изображение
            transform = QTransform()
            transform.scale(self.current_scale * scale_x, self.current_scale * scale_y)
            painter.setTransform(transform, True)
            
            # Рисуем оригинальное изображение
            painter.drawPixmap(0, 0, original_pixmap)
            painter.restore()
            
            painter.end()

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        self.view.fitInView(self.page_rect, Qt.KeepAspectRatio)
        super().resizeEvent(event)

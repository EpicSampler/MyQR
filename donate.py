
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                            QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont

class DonationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поддержать разработчика")
        self.setFixedSize(350, 180)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Текст с заголовком
        title = QLabel("Поддержать проект")
        title.setFont(QFont('Arial', 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Основной текст
        info_text = QLabel(
            "Если вам нравится приложение, вы можете\n"
            "поддержать его развитие финансово:"
        )
        info_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_text)
        
        # Ссылка (отдельный лейбл с подчеркиванием)
        self.link_label = QLabel(
            '<a href="https://www.donationalerts.com/r/epicsempler" '
            'style="text-decoration: underline; color: #0066cc;">'
            'DonationAlerts</a>'
        )
        self.link_label.setAlignment(Qt.AlignCenter)
        self.link_label.setOpenExternalLinks(False)
        self.link_label.linkActivated.connect(self.open_link)
        layout.addWidget(self.link_label)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setProperty("class", "close-button")
        buttons_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("Перейти")
        ok_button.setProperty("class", "close-button")
        ok_button.clicked.connect(self.open_donation_page)
        ok_button.setDefault(True)
        buttons_layout.addWidget(ok_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def open_link(self, url):
        QDesktopServices.openUrl(QUrl(url))
    
    def open_donation_page(self):
        self.open_link("https://www.donationalerts.com/r/epicsempler")
        self.accept()


import sys
import PySide6
from PySide6 import QtGui

from PySide6.QtWidgets import QTreeView, QApplication, QHeaderView, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTabWidget, QFileDialog, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


from qt_material import apply_stylesheet

import json
import gzip

from parse import *
class DisplayTab(QWidget):

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 480

        self.cur_frame = 0
        self.scale = (1, 1)

        self.parse_image(filename)
        self.initUI()
        self.update_canvas()

    def parse_image(self, filename: str):
        img = GifReader(filename)
        self.parsed_img = img.parse()

    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.save_button = QPushButton()
        self.save_button.setText("Save")
        self.save_button.clicked.connect(lambda _: self.save_tab())

        self.label = QLabel()
        canvas = QPixmap(self.parsed_img.width, self.parsed_img.height)
        canvas.fill(Qt.black)
        self.label.setPixmap(canvas)
        windowLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        hboxLayout.addWidget(self.label)
        # windowLayout.addWidget(self.save_button)

        windowLayout.addLayout(hboxLayout)
        self.setLayout(windowLayout)
        
        self.show()
    def update_canvas(self):
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QtGui.QPen()
        pen.setWidth(1)
        for y in range(self.parsed_img.height):
            for x in range(self.parsed_img.width):
                first_frame = self.parsed_img.frames[0]
                rgb = first_frame.frame_img_data.rgb_lst[y * self.parsed_img.width + x]
                pen.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
                # pen.setColor(QtGui.QColor('red'))
                painter.setPen(pen)
                painter.drawPoint(x, y)
        painter.end()
        canvas = canvas.scaled(self.parsed_img.width*self.scale[0], 
                               self.parsed_img.width*self.scale[1])
        self.label.setPixmap(canvas)

if __name__ == '__main__':
    def add_tabs(tabs):
        tabs.clear()
        my_file  = QFileDialog.getOpenFileName(None, "Select GIF file", "", "Images (*.gif)")
        my_file = my_file[0]
        tabs.resize(800, 1000)
        tabs.addTab(DisplayTab(my_file), "Display")



    app = QApplication(sys.argv)
    
    apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

    w = QWidget()
    w.resize(800, 500)
    vbox = QVBoxLayout()

    open_folder = QPushButton()
    open_folder.setText("Open GIF file")

    pull_savegames= QPushButton()
    pull_savegames.setText("Pull Savegames")

    push_savegames= QPushButton()
    push_savegames.setText("Push Savegames")
    tabs = QTabWidget()
    open_folder.clicked.connect(lambda: add_tabs(tabs))

    vbox.addWidget(tabs)
    vbox.addWidget(open_folder)
    w.setLayout(vbox)
    w.show()
    # ex = App()
    sys.exit(app.exec())


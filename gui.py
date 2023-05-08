
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
    
    def advance_frame(self, offset=1):
        if self.cur_frame+offset < len(self.parsed_img.frames) and\
            self.cur_frame+offset >= 0:
            self.cur_frame += offset
            self.update_canvas()
            self.frame_label.setText(f"Cur Frame: {self.cur_frame}")
    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.frame_label = QLabel("Cur Frame: 0")

        self.next_frame_button = QPushButton()
        self.next_frame_button.setText("Next Frame")
        self.next_frame_button.clicked.connect(lambda _: self.advance_frame())
        
        self.prev_frame_button = QPushButton()
        self.prev_frame_button.setText("Prev Frame")
        self.prev_frame_button.clicked.connect(lambda _: self.advance_frame(-1))
        
        # change the scale of the image
        self.zoomin_btn = QPushButton()
        self.zoomin_btn.setText("Zoom In")
        self.zoomin_btn.clicked.connect(lambda _: self.change_scale("incr"))
        
        self.zoomout_btn = QPushButton()
        self.zoomout_btn.setText("Zoom Out")
        self.zoomout_btn.clicked.connect(lambda _: self.change_scale("decr"))

        self.label = QLabel()
        canvas = QPixmap(self.parsed_img.width, self.parsed_img.height)
        canvas.fill(Qt.black)
        
        self.label.setPixmap(canvas)
        windowLayout = QVBoxLayout()
        
        hboxLayout1 = QHBoxLayout()
        hboxLayout1.addWidget(self.label)
        
        hboxLayout2 = QHBoxLayout()
        hboxLayout2.addWidget(self.zoomin_btn)
        hboxLayout2.addWidget(self.zoomout_btn)

        hboxLayout3 = QHBoxLayout()
        hboxLayout3.addWidget(self.next_frame_button)
        hboxLayout3.addWidget(self.prev_frame_button)

        windowLayout.addWidget(self.frame_label)

        windowLayout.addLayout(hboxLayout1)
        windowLayout.addLayout(hboxLayout2)
        windowLayout.addLayout(hboxLayout3)
        self.setLayout(windowLayout)
        
        self.show()
        
    def update_canvas(self):
        # canvas = self.label.pixmap()
        canvas = QPixmap(self.parsed_img.width, self.parsed_img.height)
        canvas.fill(Qt.cyan)
        painter = QtGui.QPainter(canvas)
        pen = QtGui.QPen()
        pen.setWidth(1)
        drawn_frame = self.parsed_img.frames[self.cur_frame]
        for y in range(drawn_frame.img_descriptor.height):
            for x in range(drawn_frame.img_descriptor.width):
                rgb = drawn_frame.frame_img_data.rgb_lst[y * drawn_frame.img_descriptor.width + x]
                global_x = x + drawn_frame.img_descriptor.left
                global_y = y + drawn_frame.img_descriptor.top
                pen.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
                # pen.setColor(QtGui.QColor('red'))
                painter.setPen(pen)
                painter.drawPoint(global_x, global_y)
        painter.end()
        canvas = canvas.scaled(self.parsed_img.width*self.scale[0], 
                               self.parsed_img.width*self.scale[1])
        self.label.setPixmap(canvas)

    def change_scale(self, incr_or_decr, offset = 0.1):
        # NOTE: each click gives a 10% change in size
        if incr_or_decr == "incr":
            self.scale = (self.scale[0] + 0.1, self.scale[1] + 0.1)
        elif incr_or_decr == "decr":
            self.scale = (self.scale[0] - 0.1, self.scale[1] - 0.1)
        else:
            raise Exception("Invalid incr_or_decr value")
        # update canvas with new scale
        self.update_canvas()

if __name__ == '__main__':
    def add_tabs(tabs):
        tabs.clear()
        w.resize(800, 500)
        my_file  = QFileDialog.getOpenFileName(None, "Select GIF file", "", "Images (*.gif)")
        my_file = my_file[0]
        tabs.resize(800, 1000)
        tabs.addTab(DisplayTab(my_file), "Display")


    app = QApplication(sys.argv)
    
    apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

    w = QWidget()
    w.resize(800, 100)
    vbox = QVBoxLayout()

    open_file = QPushButton()
    open_file.setText("Open GIF file")

    tabs = QTabWidget()
    tabs.resize(0, 0)
    open_file.clicked.connect(lambda: add_tabs(tabs))

    vbox.addWidget(tabs)
    vbox.addWidget(open_file)
    w.setLayout(vbox)
    w.show()
    # ex = App()
    sys.exit(app.exec())



import sys

from PySide6 import QtGui
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QBrush, QPen, QPixmap
from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)
from qt_material import apply_stylesheet

from data import GifData
from parse import GifReader


class FrameRef(QObject):
    changed_signal = Signal()
    def __init__(self, current = 0):
        super().__init__()
        self.cur_frame = current

class DisplayTab(QWidget):
    def __init__(self, gif:GifData, frame_ref:FrameRef):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 480
        self.parsed_gif = gif

        self.cur_frame = frame_ref
        self.scale = (1, 1)
        self.init()
        self.update_canvas()
    
    def advance_frame(self, offset=1):
        if self.cur_frame.cur_frame+offset < len(self.parsed_gif.frames) and\
            self.cur_frame.cur_frame+offset >= 0:
            self.cur_frame.cur_frame += offset
            self.frame_label.setText(f"Cur Frame: {self.cur_frame.cur_frame}")
    
    def init(self):
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.frame_label = QLabel("Cur Frame: 0")

        self.next_frame_button = QPushButton()
        self.next_frame_button.setText("Next Frame")
        self.next_frame_button.clicked.connect(lambda _: self.advance_frame())
        self.next_frame_button.clicked.connect(self.cur_frame.changed_signal)
        
        self.prev_frame_button = QPushButton()
        self.prev_frame_button.setText("Prev Frame")
        self.prev_frame_button.clicked.connect(lambda _: self.advance_frame(-1))
        self.prev_frame_button.clicked.connect(self.cur_frame.changed_signal)
        
        # change the scale of the image
        self.zoomin_btn = QPushButton()
        self.zoomin_btn.setText("Zoom In")
        self.zoomin_btn.clicked.connect(lambda _: self.change_scale("incr"))
        
        self.zoomout_btn = QPushButton()
        self.zoomout_btn.setText("Zoom Out")
        self.zoomout_btn.clicked.connect(lambda _: self.change_scale("decr"))

        self.label = QLabel()
        canvas = QPixmap(self.parsed_gif.width, self.parsed_gif.height)
        canvas.fill(Qt.black)
        
        self.label.setPixmap(canvas)
        windowLayout = QVBoxLayout()
        
        hboxLayout1 = QHBoxLayout()
        hboxLayout1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        hboxLayout1.addWidget(self.label)
        
        hboxLayout2 = QHBoxLayout()
        hboxLayout2.addWidget(self.zoomout_btn)
        hboxLayout2.addWidget(self.zoomin_btn)

        hboxLayout3 = QHBoxLayout()
        hboxLayout3.addWidget(self.prev_frame_button)
        hboxLayout3.addWidget(self.next_frame_button)

        windowLayout.addWidget(self.frame_label)

        windowLayout.addLayout(hboxLayout1)
        windowLayout.addLayout(hboxLayout2)
        windowLayout.addLayout(hboxLayout3)
        self.setLayout(windowLayout)
        
        self.show()
        
    def update_canvas(self):
        canvas = QPixmap(self.parsed_gif.width, self.parsed_gif.height)
        canvas.fill(Qt.cyan)
        painter = QtGui.QPainter(canvas)
        pen = QPen()
        pen.setWidth(1)
        drawn_frame = self.parsed_gif.frames[self.cur_frame.cur_frame]
        gct = self.parsed_gif.gct
        for y in range(drawn_frame.img_descriptor.height):
            for x in range(drawn_frame.img_descriptor.width):
                bound_ct = gct
                if drawn_frame.img_descriptor.lct_flag:
                    bound_ct = drawn_frame.img_descriptor.lct
                index = drawn_frame.frame_img_data[y * drawn_frame.img_descriptor.width + x]
                rgb = bound_ct[index]
                global_x = x + drawn_frame.img_descriptor.left
                global_y = y + drawn_frame.img_descriptor.top
                pen.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
                painter.setPen(pen)
                painter.drawPoint(global_x, global_y)
        painter.end()
        canvas = canvas.scaled(self.parsed_gif.width*self.scale[0], 
                               self.parsed_gif.width*self.scale[1])
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

class DetailsTab(QWidget):
    def __init__(self, gif:GifData, frame_ref:FrameRef, file_name:str):
        super().__init__()
        self.parsed_gif = gif
        self.cur_frame = frame_ref
        self.file_name = file_name
        self.init()
        self.update_canvas()

    def init(self):
        self.filename_label = QLabel(f'Filename : {self.file_name}')
        self.frame_label = QLabel("Cur Frame: 0")
        img_desc = self.parsed_gif.frames[0].img_descriptor
        self.frame_dim_label = QLabel(f"Width:Height : {img_desc.width, img_desc.height}")
        gce = self.parsed_gif.frames[0].graphic_control
        self.frame_delay = QLabel(f"Delay : {gce.delay_time if gce is not None and gce.delay_time > 0 else '100(default)'}")
        gct = self.parsed_gif.gct
        
        windowLayout = QHBoxLayout()
        vboxLayout1 = QVBoxLayout()
        vboxLayout1.setAlignment(Qt.AlignmentFlag.AlignTop)
        vboxLayout1.addWidget(self.filename_label)
        vboxLayout1.addWidget(self.frame_label)
        vboxLayout1.addWidget(self.frame_dim_label)
        vboxLayout1.addWidget(self.frame_delay)

        vboxLayout2 = QVBoxLayout()

        windowLayout.addLayout(vboxLayout1)
        windowLayout.addLayout(vboxLayout2)
        self.setLayout(windowLayout)

    def update_canvas(self):
        self.frame_label.setText(f'Cur Frame: {self.cur_frame.cur_frame}')
        img_desc = self.parsed_gif.frames[self.cur_frame.cur_frame].img_descriptor
        self.frame_dim_label.setText(f"Width:Height : {img_desc.width, img_desc.height}")
        gce = self.parsed_gif.frames[self.cur_frame.cur_frame].graphic_control
        self.frame_delay.setText(f"Delay : {gce.delay_time if gce is not None and gce.delay_time > 0 else '100(default)'}")


    



if __name__ == '__main__':
    def add_tabs(tabs:QTabWidget):
        tabs.clear()
        w.resize(800, 500)
        file_name  = QFileDialog.getOpenFileName(None, "Select GIF file", "", "Images (*.gif)")
        file_name = file_name[0]
        tabs.resize(800, 1000)
        # Parse image
        frame_ref = FrameRef()
        img = GifReader(file_name).parse()
        display = DisplayTab(img, frame_ref)
        details = DetailsTab(img, frame_ref, file_name)
        tabs.addTab(display, "Display")
        tabs.addTab(details, "Details")
        frame_ref.changed_signal.connect(display.update_canvas)
        frame_ref.changed_signal.connect(details.update_canvas)


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


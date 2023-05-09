import sys

from PySide6 import QtGui
from PySide6.QtCore import QObject, Qt, Signal, QRect
from PySide6.QtGui import QBrush, QPen, QPixmap, QPainter
from PySide6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                               QPushButton, QTabWidget, QVBoxLayout, QGridLayout, QWidget, QTextEdit)
from qt_material import apply_stylesheet

import math

from data import GifData
from parse import GifReader
from encrypt import encrypt
from encode import GifEncoder
from lzw_gif import compress

# TODO: Separate out the different tabs into different places and each component to their own function
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
        self.initUI()
        self.update_canvas()
    
    def advance_frame(self, offset=1):
        if self.cur_frame.cur_frame+offset < len(self.parsed_gif.frames) and\
            self.cur_frame.cur_frame+offset >= 0:
            self.cur_frame.cur_frame += offset
            self.frame_label.setText(f"Cur Frame: {self.cur_frame.cur_frame}")
    
    def initUI(self):
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
        
    def update_canvas(self):
        canvas = QPixmap(self.parsed_gif.width, self.parsed_gif.height)
        canvas.fill(Qt.cyan)
        painter = QtGui.QPainter(canvas)
        pen = QPen()
        pen.setWidth(1)
        drawn_frame = self.parsed_gif.frames[self.cur_frame.cur_frame]
        gct = self.parsed_gif.gct
        bound_ct = gct
        if drawn_frame.img_descriptor.lct_flag:
            bound_ct = drawn_frame.img_descriptor.lct
        for y in range(drawn_frame.img_descriptor.height):
            for x in range(drawn_frame.img_descriptor.width):
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
    RECT_SIZE = 16
    def __init__(self, gif:GifData, frame_ref:FrameRef, file_name:str):
        super().__init__()
        self.parsed_gif = gif
        self.cur_frame = frame_ref
        self.file_name = file_name
        self.initUI()
        self.update_canvas()

    def initUI(self):
        self.filename_label = QLabel(f'Filename : {self.file_name}')
        self.filename_label.setWordWrap(True)
        self.frame_label = QLabel("Cur Frame: 0")
        img_desc = self.parsed_gif.frames[0].img_descriptor
        self.frame_dim_label = QLabel(f"Width:Height : {img_desc.width, img_desc.height}")
        gce = self.parsed_gif.frames[0].graphic_control
        self.frame_delay = QLabel(f"Delay : {gce.delay_time if gce is not None and gce.delay_time > 0 else '100(default)'}")
        self.transparency_index = QLabel(f"Transparent Index : {gce.transparent_color_index if gce is not None and gce.transparent_color_flag else 'None'}")

        gct = self.parsed_gif.gct
        gct_size = 2 ** (self.parsed_gif.gct_size+1)
        gct_normalised_dim = math.ceil(math.sqrt(gct_size))

        # Draw GCT
        self.gct_title = QLabel('Global Color Table')
        self.gct_label = QLabel()
        gct_canvas = QPixmap(gct_normalised_dim*DetailsTab.RECT_SIZE, gct_normalised_dim*DetailsTab.RECT_SIZE)
        gct_canvas.fill(Qt.black)
        painter = QPainter(gct_canvas)
        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor("#FFFFFF"))
        brush = QBrush(Qt.BrushStyle.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)
        for index, rgb in enumerate(gct):
            x = index % gct_normalised_dim
            y = index // gct_normalised_dim
            brush.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
            painter.setBrush(brush)
            painter.drawRect(QRect(x*DetailsTab.RECT_SIZE,y*DetailsTab.RECT_SIZE,DetailsTab.RECT_SIZE, DetailsTab.RECT_SIZE))
        painter.end()
        self.gct_label.setPixmap(gct_canvas)

        # Draw LCT
        self.lct_title = QLabel('Local Color Table')
        self.lct_label = QLabel()
        if self.parsed_gif.frames[0].img_descriptor.lct_flag:
            lct = self.parsed_gif.frames[0].img_descriptor.lct
            lct_size = 2 ** (self.parsed_gif.frames[0].img_descriptor.lct_size+1)
            lct_normalised_dim = math.ceil(math.sqrt(lct_size))
            lct_canvas = QPixmap(lct_normalised_dim*DetailsTab.RECT_SIZE, lct_normalised_dim*DetailsTab.RECT_SIZE)
            lct_canvas.fill(Qt.black)
            painter = QPainter(lct_canvas)
            pen = QPen()
            pen.setWidth(1)
            pen.setColor(QtGui.QColor("#FFFFFF"))
            brush = QBrush(Qt.BrushStyle.SolidPattern)
            painter.setPen(pen)
            painter.setBrush(brush)
            for index, rgb in enumerate(lct):
                x = index % lct_normalised_dim
                y = index // lct_normalised_dim
                brush.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
                painter.setBrush(brush)
                painter.drawRect(QRect(x*DetailsTab.RECT_SIZE,y*DetailsTab.RECT_SIZE,DetailsTab.RECT_SIZE, DetailsTab.RECT_SIZE))
            painter.end()
            self.lct_label.setPixmap(lct_canvas)
        else:
            self.lct_label.setText("No Local Color Table")
        
        windowLayout = QHBoxLayout()
        vboxLayout1 = QVBoxLayout()
        vboxLayout1.setAlignment(Qt.AlignmentFlag.AlignTop)
        vboxLayout1.addWidget(self.filename_label)
        vboxLayout1.addWidget(self.frame_label)
        vboxLayout1.addWidget(self.frame_dim_label)
        vboxLayout1.addWidget(self.frame_delay)
        vboxLayout1.addWidget(self.transparency_index)

        vboxLayout2 = QVBoxLayout()
        vboxLayout2.setAlignment(Qt.AlignmentFlag.AlignTop)
        vboxLayout2.addWidget(self.gct_title)
        vboxLayout2.addWidget(self.gct_label)
        vboxLayout2.addWidget(self.lct_title)
        vboxLayout2.addWidget(self.lct_label)

        windowLayout.addLayout(vboxLayout1)
        windowLayout.addLayout(vboxLayout2)
        self.setLayout(windowLayout)

    def update_canvas(self):
        cur_frame = self.cur_frame.cur_frame

        self.frame_label.setText(f'Cur Frame: {cur_frame}')
        img_desc = self.parsed_gif.frames[cur_frame].img_descriptor
        self.frame_dim_label.setText(f"Width:Height : {img_desc.width, img_desc.height}")
        gce = self.parsed_gif.frames[cur_frame].graphic_control
        self.frame_delay.setText(f"Delay : {gce.delay_time if gce is not None and gce.delay_time > 0 else '100(default)'}")
        self.transparency_index.setText(f"Transparent Index : {gce.transparent_color_index if gce is not None and gce.transparent_color_flag else 'None'}")

        # LCT
        if self.parsed_gif.frames[cur_frame].img_descriptor.lct_flag:
            lct = self.parsed_gif.frames[cur_frame].img_descriptor.lct
            lct_size = 2 ** (self.parsed_gif.frames[cur_frame].img_descriptor.lct_size+1)
            lct_normalised_dim = math.ceil(math.sqrt(lct_size))
            lct_canvas = QPixmap(lct_normalised_dim*DetailsTab.RECT_SIZE, lct_normalised_dim*DetailsTab.RECT_SIZE)
            lct_canvas.fill(Qt.black)
            painter = QPainter(lct_canvas)
            pen = QPen()
            pen.setWidth(1)
            pen.setColor(QtGui.QColor("#FFFFFF"))
            brush = QBrush(Qt.BrushStyle.SolidPattern)
            painter.setPen(pen)
            painter.setBrush(brush)
            for index, rgb in enumerate(lct):
                x = index % lct_normalised_dim
                y = index // lct_normalised_dim
                brush.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
                painter.setBrush(brush)
                painter.drawRect(QRect(x*DetailsTab.RECT_SIZE,y*DetailsTab.RECT_SIZE,DetailsTab.RECT_SIZE, DetailsTab.RECT_SIZE))
            painter.end()
            self.lct_label.setPixmap(lct_canvas)
        else:
            self.lct_label.setText("No Local Color Table")


class EncryptTab(QWidget):
    def __init__(self, gif:GifData):
        super().__init__()
        self.parsed_gif = gif
        self.encrypted_gif = gif
        self.cur_frame = 0
        self.n = 0
        self.pw = None
        self.scale = (1,1)
        self.initUI()
    
    def advance_frame(self, offset=1):
        if self.cur_frame+offset < len(self.encrypted_gif.frames) and\
            self.cur_frame+offset >= 0:
            self.cur_frame += offset
            self.frame_label.setText(f"Cur Frame: {self.cur_frame}")
            self.update_canvas()
  
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
    
    def encrypt(self):
        self.n = int(self.n_textedit.toPlainText())
        self.pw = self.pw_textedit.toPlainText()
        self.encrypted_gif = encrypt(self.parsed_gif, self.pw, self.n)
        self.update_canvas()

    def save(self):
        file_name = QFileDialog.getSaveFileName(None, "Save Encrypted GIF file", "", "Image (*.gif)")[0]
        encoder = GifEncoder(file_name)
        encoder.encode(self.encrypted_gif, compress)
        encoder.to_file()

    def initUI(self):
        # Info pane Widgets
        self.frame_label = QLabel("Cur Frame: 0")
        self.n_label = QLabel('N : 0')
        self.pw_label = QLabel('Passphrase : ')

        # Preview Pane Widgets
        self.preview_label = QLabel()
        canvas = QPixmap(self.encrypted_gif.width, self.encrypted_gif.height)
        canvas.fill(Qt.cyan)
        painter = QtGui.QPainter(canvas)
        pen = QPen()
        pen.setWidth(1)
        drawn_frame = self.encrypted_gif.frames[self.cur_frame]
        gct = self.encrypted_gif.gct
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
        canvas = canvas.scaled(self.encrypted_gif.width*self.scale[0], 
                               self.encrypted_gif.width*self.scale[1])
        self.preview_label.setPixmap(canvas)

        self.next_frame_button = QPushButton("Next Frame")
        self.next_frame_button.clicked.connect(lambda _: self.advance_frame())
        
        self.prev_frame_button = QPushButton("Prev Frame")
        self.prev_frame_button.clicked.connect(lambda _: self.advance_frame(-1))
        
        # change the scale of the image
        self.zoomin_btn = QPushButton("Zoom In")
        self.zoomin_btn.clicked.connect(lambda _: self.change_scale("incr"))
        
        self.zoomout_btn = QPushButton("Zoom Out")
        self.zoomout_btn.clicked.connect(lambda _: self.change_scale("decr"))

        # user_input layout widgets
        self.pw_title = QLabel('Password')
        self.pw_textedit = QTextEdit()
        self.pw_textedit.setToolTip("Password")
        self.n_title = QLabel('N')
        self.n_textedit = QTextEdit()
        self.n_textedit.setToolTip("N")
        self.encrypt_btn = QPushButton("Encrypt")
        self.encrypt_btn.clicked.connect(lambda _: self.encrypt())
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(lambda _: self.save())

        info_pane_layout = QVBoxLayout()
        info_pane_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_pane_layout.addWidget(self.frame_label)
        info_pane_layout.addWidget(self.n_label)
        info_pane_layout.addWidget(self.pw_label)

        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.preview_label)
        preview_buttons_layout = QGridLayout()
        preview_buttons_layout.addWidget(self.prev_frame_button, 0, 0)
        preview_buttons_layout.addWidget(self.next_frame_button, 0, 1)
        preview_buttons_layout.addWidget(self.zoomout_btn, 1, 0)
        preview_buttons_layout.addWidget(self.zoomin_btn, 1, 1)
        preview_layout.addItem(preview_buttons_layout)

        user_input_layout = QVBoxLayout()
        user_input_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        user_input_layout.addWidget(self.pw_title)
        user_input_layout.addWidget(self.pw_textedit)
        user_input_layout.addWidget(self.n_title)
        user_input_layout.addWidget(self.n_textedit)
        user_input_layout.addWidget(self.encrypt_btn)
        user_input_layout.addWidget(self.save_btn)

        window_layout = QHBoxLayout()
        window_layout.addLayout(info_pane_layout)
        window_layout.addLayout(preview_layout)
        window_layout.addLayout(user_input_layout)
        self.setLayout(window_layout)

    
    def update_canvas(self):
        self.n_label.setText(f'N : {self.n}')
        self.frame_label.setText(f'Cur Frame : {self.cur_frame}')
        self.pw_label.setText(f'Passphrase : {self.pw}')
        canvas = QPixmap(self.encrypted_gif.width, self.encrypted_gif.height)
        canvas.fill(Qt.cyan)
        painter = QtGui.QPainter(canvas)
        pen = QPen()
        pen.setWidth(1)
        drawn_frame = self.encrypted_gif.frames[self.cur_frame]
        gct = self.encrypted_gif.gct
        bound_ct = gct
        if drawn_frame.img_descriptor.lct_flag:
            bound_ct = drawn_frame.img_descriptor.lct
        for y in range(drawn_frame.img_descriptor.height):
            for x in range(drawn_frame.img_descriptor.width):
                index = drawn_frame.frame_img_data[y * drawn_frame.img_descriptor.width + x]
                rgb = bound_ct[index]
                global_x = x + drawn_frame.img_descriptor.left
                global_y = y + drawn_frame.img_descriptor.top
                pen.setColor(QtGui.QColor(rgb.r, rgb.g, rgb.b))
                painter.setPen(pen)
                painter.drawPoint(global_x, global_y)
        painter.end()
        canvas = canvas.scaled(self.encrypted_gif.width*self.scale[0], 
                               self.encrypted_gif.width*self.scale[1])
        self.preview_label.setPixmap(canvas)

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
        encrypt = EncryptTab(img)
        tabs.addTab(display, "Display")
        tabs.addTab(details, "Details")
        tabs.addTab(encrypt, "Encrypt")
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


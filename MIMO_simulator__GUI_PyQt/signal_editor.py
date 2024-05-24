import sys
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from numpy import sin,cos,exp,power,pi
import globals

selected_wave = globals.R[0]

class SignalEditor(QDockWidget):
    def __init__(self, parent = None):
        super(SignalEditor, self).__init__(parent)
        self.setMinimumHeight(250)
        self.main_scroll = QScrollArea()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.editor = QVBoxLayout()
        self.preview = QVBoxLayout()
        if globals.darkTheme:
            plt.style.use('dark_background')
        # editor
        self.editorIcon =QLabel("")
        # self.pixmap = QPixmap('res/wave.png')
        # self.pixmap.scaled(10,10,Qt.KeepAspectRatio)
        # self.editorIcon.setPixmap(self.pixmap)
        self.selectionLabel = QLabel("R1")
        self.editor.addWidget(self.selectionLabel)
        self.editor.addWidget(self.editorIcon)
        self.scrollableArea = QScrollArea()
        self.scrollableArea.setWidgetResizable(True)
        self.waveformWidget = QWidget()
        self.wavesLayout = QVBoxLayout()

        self.waveformWidget.setLayout(self.wavesLayout)
        self.scrollableArea.setWidget(self.waveformWidget)
        self.resetbtn = QPushButton("  Reset Signal")
        self.resetbtn.setToolTip("Resets signal to 0")
        self.resetbtn.setIcon(QIcon('res/reset.png'))
        self.resetbtn.clicked.connect(self.reset_signal)
        self.btnsContainer = QHBoxLayout()
        self.addStepBtn = QPushButton("")
        self.addStepBtn.setIcon(QIcon('res/step.png'))
        self.addStepBtn.setToolTip("Step Change Block")
        self.addStepBtn.clicked.connect(lambda: self.addFunc("Step"))
        self.btnsContainer.addWidget(self.addStepBtn)
        self.addRampBtn = QPushButton("")
        self.addRampBtn.setToolTip("Ramp block")
        self.addRampBtn.setIcon(QIcon('res/line.png'))
        self.addRampBtn.clicked.connect(lambda: self.addFunc("Ramp"))
        self.btnsContainer.addWidget(self.addRampBtn)
        
        self.addSqrBtn = QPushButton("")
        self.addSqrBtn.setToolTip("Square wave block")
        self.addSqrBtn.setIcon(QIcon('res/wave-square.png'))
        self.addSqrBtn.clicked.connect(lambda: self.addFunc("SquareWave"))
        self.btnsContainer.addWidget(self.addSqrBtn)

        self.addFuncBtn = QPushButton("")
        self.addFuncBtn.setToolTip("Custom function block")
        self.addFuncBtn.setIcon(QIcon('res/function.png'))
        self.addFuncBtn.clicked.connect(lambda: self.addFunc("Func"))
        self.btnsContainer.addWidget(self.addFuncBtn)

        self.editor.addWidget(self.resetbtn)
        self.editor.addSpacing(20)
        self.editor.addLayout(self.btnsContainer)
        self.editor.addWidget(self.scrollableArea)

        self.applybtn = QPushButton("  Apply Changes")
        self.applybtn.setIcon(QIcon('res/tick.png'))
        self.applybtn.clicked.connect(self.apply_changes)
        # preview
        self.preview.addWidget(QLabel("Preview"))
        self.plot_canvas = MplCanvas(self.preview)
        self.update_preview()
        self.preview.addWidget(self.plot_canvas)

        self.main_layout.addLayout(self.editor,3)
        self.main_layout.addWidget(self.applybtn)
        self.main_layout.addLayout(self.preview,2)
        self.main_layout.addStretch()
        self.main_scroll.setWidget(self.main_widget)
        self.setWidget(self.main_widget)
        self.main_widget.setLayout(self.main_layout)

    def on_signal_select(self,type,i):
        global selected_wave
        selected_wave = globals.R[i-1] if type=="R" else globals.U[i-1]
        # update UI
        self.selectionLabel.setText("R{}".format(i) if type=="R" else "U{}".format(i))
        self.update_preview()

    def addFunc(self,type):
        if type=="Step":
            widget = stepBlock(self.wavesLayout)
        elif type=="Ramp":
            widget = rampBlock(self.wavesLayout)
        elif type =="Func":
            widget = customFunc(self.wavesLayout)
        elif type=="SquareWave":
            widget = squareWaveBlock(self.wavesLayout)
        # widget.setMinimumHeight(150)
        self.wavesLayout.addWidget(widget)
        widget.show()
        # self.waveformWidget.resize(300,self.wavesLayout.count()*150)
    
    def apply_changes(self):
        for i in range(self.wavesLayout.count()):
            self.wavesLayout.itemAt(i).widget().apply()
        self.update_preview()

    def reset_signal(self):
        global selected_wave
        selected_wave[0:] = 0
        self.update_preview()

    def update_preview(self):
        self.plot_canvas.axes.cla()
        global selected_wave
        self.plot_canvas.axes.grid(linestyle='--',linewidth=0.2)
        self.plot_canvas.axes.plot(globals.t,selected_wave)
        self.plot_canvas.draw()
        self.plot_canvas.flush_events()

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        super(MplCanvas, self).__init__(fig)

class rampBlock(QWidget):
    def __init__(self, layout, parent = None):
        super(rampBlock, self).__init__(parent)
        self.layout = layout
        # self.setMaximumHeight(120)
        self.main_layout = QVBoxLayout()
        self.ribbon = QHBoxLayout()
        self.ribbon.addWidget(QLabel("Ramp Signal"))
        self.removeBtn = QPushButton("")
        self.removeBtn.setIcon(QIcon('res/bin.png'))
        self.removeBtn.setMaximumSize(40,40)
        self.removeBtn.clicked.connect(self.remove_self)
        self.ribbon.addWidget(self.removeBtn)

        self.main_layout.addLayout(self.ribbon)
        self.setLayout(self.main_layout)

        self.vLayout = QVBoxLayout()
        self.p1Layout = QHBoxLayout()
        self.p1 = QLineEdit()
        self.p1Layout.addWidget(self.p1)
        self.v1 = QLineEdit()
        self.p1Layout.addWidget(self.v1)
        self.vLayout.addLayout(self.p1Layout)
        self.p2Layout = QHBoxLayout()
        self.p2 = QLineEdit()
        self.p2Layout.addWidget(self.p2)
        self.v2 = QLineEdit()
        self.p2Layout.addWidget(self.v2)
        self.vLayout.addLayout(self.p2Layout)

        self.main_layout.addLayout(self.vLayout)
    
    def apply(self):
        global selected_wave
        try:
            p1,p2,v1,v2 = int(self.p1.text()),int(self.p2.text()),int(self.v1.text()),int(self.v2.text())
            m = (v2-v1)/(p2-p1)
            for p in range(p1,p2):
                selected_wave[p] = v1 + m*(p-p1)
        except:
            print("Invalid values")

    def remove_self(self):
        # Remove this widget from the layout
        self.layout.removeWidget(self)
        self.setParent(None)
        self.deleteLater() 

class stepBlock(QWidget):
    def __init__(self, layout,parent = None):
        super(stepBlock, self).__init__(parent)
        self.setMaximumHeight(120)
        self.layout = layout
        self.main_layout = QVBoxLayout()
        self.ribbon = QHBoxLayout()
        self.ribbon.addWidget(QLabel("Step Change"))
        self.removeBtn = QPushButton("")
        self.removeBtn.setIcon(QIcon('res/bin.png'))
        self.removeBtn.setMaximumSize(40,40)
        self.removeBtn.clicked.connect(self.remove_self)
        self.ribbon.addWidget(self.removeBtn)
        self.main_layout.addLayout(self.ribbon)

        self.entry = QHBoxLayout()
        self.timeStamp = QLineEdit()
        self.value = QLineEdit()
        self.entry.addWidget(self.timeStamp)
        self.entry.addWidget(self.value)
        self.main_layout.addLayout(self.entry)
        self.setLayout(self.main_layout)

    def apply(self):
        global selected_wave
        try:
            selected_wave[int(self.timeStamp.text()):] = float(self.value.text())
            print(int(self.timeStamp.text()),float(self.value.text()))
        except:
            print("Invalid values")

    def remove_self(self):
        # Remove this widget from the layout
        self.layout.removeWidget(self)
        self.setParent(None)  # 
        self.deleteLater()  # 

class squareWaveBlock(QWidget):
    def __init__(self, layout, parent = None):
        super(squareWaveBlock, self).__init__(parent)
        self.layout = layout
        # self.setMaximumHeight(120)
        self.main_layout = QVBoxLayout()
        self.ribbon = QHBoxLayout()
        self.ribbon.addWidget(QLabel("Square Wave"))
        self.removeBtn = QPushButton("")
        self.removeBtn.setIcon(QIcon('res/bin.png'))
        self.removeBtn.setMaximumSize(40,40)
        self.removeBtn.clicked.connect(self.remove_self)
        self.ribbon.addWidget(self.removeBtn)

        self.main_layout.addLayout(self.ribbon)
        self.setLayout(self.main_layout)

        self.vLayout = QVBoxLayout()

        self.tLayout = QHBoxLayout()
        self.tLayout.addWidget(QLabel("Start Time"))
        self.ti = QLineEdit("0")
        self.tLayout.addWidget(self.ti)
        self.tLayout.addWidget(QLabel("End Time"))
        self.tf = QLineEdit(str(globals.tf))
        self.tLayout.addWidget(self.tf)
        self.vLayout.addLayout(self.tLayout)

        self.p1Layout = QHBoxLayout()
        self.mean = QLineEdit("0")
        self.p1Layout.addWidget(QLabel("Mean: "))
        self.p1Layout.addWidget(self.mean)
        self.amplitude = QLineEdit("1")
        self.p1Layout.addWidget(QLabel("Amplitude: "))
        self.p1Layout.addWidget(self.amplitude)
        self.vLayout.addLayout(self.p1Layout)
        self.p2Layout = QHBoxLayout()
        self.freq = QLineEdit("0.01")
        self.p2Layout.addWidget(QLabel("Frequency: "))
        self.p2Layout.addWidget(self.freq)
        self.offset = QLineEdit("0")
        self.p2Layout.addWidget(QLabel("Offset: "))
        self.p2Layout.addWidget(self.offset)
        self.vLayout.addLayout(self.p2Layout)

        self.main_layout.addLayout(self.vLayout)
    
    def apply(self):
        global selected_wave
        try:
            m,A,f,o = float(self.mean.text()),float(self.amplitude.text()),float(self.freq.text()),float(self.offset.text())
            ti,tf = int(self.ti.text()),int(self.tf.text())
            # selected_wave[ti:tf] = m+ A*sin(2*pi*f*(globals.t[ti:tf]-o))
            selected_wave[ti:tf] = [m+A if sin(2*pi*f*(t-o))>0 else m-A for t in globals.t[ti:tf]]
        except:
            print("Invalid values")

    def remove_self(self):
        # Remove this widget from the layout
        self.layout.removeWidget(self)
        self.setParent(None)
        self.deleteLater() 

class customFunc(QWidget):
    def __init__(self, layout, parent = None):
        super(customFunc, self).__init__(parent)
        self.l1 = layout
        # self.setMaximumHeight(120)
        self.main_layout = QVBoxLayout()
        
        self.setLayout(self.main_layout)
        self.ribbon = QHBoxLayout()
        self.ribbon.addWidget(QLabel("Custom Function"))
        self.removeBtn = QPushButton("")
        self.removeBtn.setIcon(QIcon('res/bin.png'))
        self.removeBtn.setMaximumSize(40,40)
        self.removeBtn.clicked.connect(self.remove_self)
        self.ribbon.addWidget(self.removeBtn)

        self.main_layout.addLayout(self.ribbon)

        self.tLayout = QHBoxLayout()
        self.tLayout.addWidget(QLabel("Start Time"))
        self.ti = QLineEdit("0")
        self.tLayout.addWidget(self.ti)
        self.tLayout.addWidget(QLabel("End Time"))
        self.tf = QLineEdit(str(globals.tf))
        self.tLayout.addWidget(self.tf)
        self.main_layout.addLayout(self.tLayout)

        self.expression = QLineEdit()
        self.main_layout.addWidget(self.expression)

    def apply(self):
        global selected_wave
        try:
            ti,tf = int(self.ti.text()),int(self.tf.text())
            t = globals.t[ti:tf]
            # print(len(t))
            selected_wave[ti:tf]= eval(self.expression.text())
        except:
            print("Invalid Expression")

    def remove_self(self):
        # Remove this widget from the layout
        self.l1.removeWidget(self)
        self.setParent(None)  # 
        self.deleteLater()  # 

        
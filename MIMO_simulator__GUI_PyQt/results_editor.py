from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import globals

class ResultsEditor(QDockWidget):
    def __init__(self, parent = None):
        super(ResultsEditor, self).__init__(parent)
        self.setMinimumHeight(250)
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.mainVertLayout = QVBoxLayout()
        self.main_widget.setLayout(self.mainVertLayout)
        self.ribbon = QHBoxLayout()
        self.ribbon.addWidget(QLabel("Results"))
        self.saveFig = QPushButton("Save Fig.")
        self.saveFig.clicked.connect(self.on_clicked_save_fig)
        self.saveData = QPushButton("Export Data")
        self.ribbon.addStretch()
        self.ribbon.addWidget(self.saveFig)
        self.ribbon.addWidget(self.saveData)
        # self.ribbon.setMaximumHeight(40)
        self.mainVertLayout.addLayout(self.ribbon)
        self.main_editor = QHBoxLayout()
        self.mainVertLayout.addLayout(self.main_editor)

        self.spScrollArea = QScrollArea()
        self.spScrollArea.setMaximumWidth(100)
        self.main_editor.addWidget(self.spScrollArea)
        self.spScrollWidget = QWidget()
        self.spVertLayout = QVBoxLayout()
        for i in range(2):
            self.spVertLayout.addWidget(checkBlock("Y",i,self))
        self.spScrollWidget.setLayout(self.spVertLayout)
        self.spScrollArea.setWidget(self.spScrollWidget)
        self.spScrollArea.setWidgetResizable(True)

        self.cvScrollArea = QScrollArea()
        self.cvScrollArea.setMaximumWidth(100)
        self.main_editor.addWidget(self.cvScrollArea)
        self.cvScrollWidget = QWidget()
        self.cvVertLayout = QVBoxLayout()
        for i in range(2):
            self.cvVertLayout.addWidget(checkBlock("U",i,self))
        self.cvScrollWidget.setLayout(self.cvVertLayout)
       
        self.cvScrollArea.setWidget(self.cvScrollWidget)
        self.cvScrollArea.setWidgetResizable(True)

        self.previewLayout = QVBoxLayout()
        # self.previewLayout.addWidget(QLabel("Preview"))
        self.plotWidget = QWidget()
        self.plot_canvas = MplCanvas(self.plotWidget)
        self.update_plot()
        self.previewLayout.addWidget(self.plot_canvas)
        self.main_editor.addLayout(self.previewLayout)

    def on_clicked_save_fig(self):
        dlg = QFileDialog()
        path = dlg.getSaveFileName(filter="Image Files (*.png)")[0]
        self.plot_canvas.save_fig(path)

    def update_UI(self):
        # remove existing
        while self.spVertLayout.count():
            child = self.spVertLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.cvVertLayout.count():
            child = self.cvVertLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # add new widgets
        for i in range(globals.m):
            self.spVertLayout.addWidget(checkBlock("Y",i,self))
        self.spVertLayout.addStretch()
        for i in range(globals.n):
            self.cvVertLayout.addWidget(checkBlock("U",i,self))
        self.cvVertLayout.addStretch()

    def update_plot(self):
        self.plot_canvas.axes1.cla()
        self.plot_canvas.axes2.cla()
        self.plot_canvas.axes1.grid(linestyle='--',linewidth=0.2)
        self.plot_canvas.axes2.grid(linestyle='--',linewidth=0.2)
        colors = cm.rainbow(np.linspace(0, 1, max(len(globals.Y),len(globals.U))))
        for i in range(self.spVertLayout.count()):
            try:
                state = self.spVertLayout.itemAt(i).widget().get_state()
            except:
                continue
            if state:
                self.plot_canvas.axes1.plot(globals.t,globals.Y[i],color=colors[i],label='Y{} model'.format(i+1))
                self.plot_canvas.axes1.plot(globals.t,globals.R[i],color=colors[i],linestyle='dashed',label='Y{} set point'.format(i+1))
        for i in range(self.cvVertLayout.count()):
            try:
                state = self.cvVertLayout.itemAt(i).widget().get_state()
            except:
                continue
            if state:
                self.plot_canvas.axes2.plot(globals.t,globals.U[i],color=colors[i],label='U{}'.format(i+1))
        self.plot_canvas.axes1.legend()
        self.plot_canvas.axes2.legend()
        self.plot_canvas.draw()
        self.plot_canvas.flush_events()

    def on_check_change(self):
        self.update_plot()

    def on_results_calculated(self):
        self.update_plot()

class checkBlock(QWidget):
    def __init__(self, type,i,results_editor,parent = None):
        super(checkBlock, self).__init__(parent)
        self.results_editor = results_editor
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(QLabel(type + str(i+1)))
        self.checkBox = QCheckBox()
        self.checkBox.stateChanged.connect(self.on_state_changed)
        self.main_layout.addWidget(self.checkBox)
        self.setLayout(self.main_layout)

    def on_state_changed(self):
        self.results_editor.on_check_change()

    def get_state(self):
        return self.checkBox.isChecked()

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = self.fig.add_subplot(211)
        self.axes1.spines['top'].set_visible(False)
        self.axes1.spines['right'].set_visible(False)
        self.axes1.grid(linestyle='--',linewidth=0.2)

        self.axes2 = self.fig.add_subplot(212)
        self.axes2.spines['top'].set_visible(False)
        self.axes2.spines['right'].set_visible(False)
        self.axes2.grid(linestyle='--',linewidth=0.2)
        super(MplCanvas, self).__init__(self.fig)

    def save_fig(self,path):
        self.fig.savefig(path)
        print("Figure saved to: ",path)

        
        
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

class OptimizerEditor(QDockWidget):
    def __init__(self, parent = None):
        super(OptimizerEditor, self).__init__(parent)
        self.setMinimumHeight(250)
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.mainVertLayout = QVBoxLayout()
        self.main_widget.setLayout(self.mainVertLayout)
        self.ribbon = QHBoxLayout()
        self.ribbon.addWidget(QLabel("Results"))
        self.saveFig = QPushButton("Save Fig.")
        # self.saveFig.clicked.connect(self.on_clicked_save_fig)
        self.saveData = QPushButton("Export Data")
        self.ribbon.addStretch()
        self.ribbon.addWidget(self.saveFig)
        self.ribbon.addWidget(self.saveData)
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
        self.plotWidget = QWidget()
        # self.plot_canvas = MplCanvas(self.plotWidget)
        # self.update_plot()
        # self.previewLayout.addWidget(self.plot_canvas)
        self.main_editor.addLayout(self.previewLayout)


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
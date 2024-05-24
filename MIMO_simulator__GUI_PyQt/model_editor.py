import sys
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from CustomUtilities import FOPDT
import globals

selected_model = (0,0)

class ModelEditor(QDockWidget):
    def __init__(self, parent = None):
        super(ModelEditor, self).__init__(parent)
        self.setMinimumWidth(200)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.model_selector = QHBoxLayout()
        self.model_selector.addWidget(QLabel("Model: "))
        self.dropdown = QComboBox()
        self.dropdown.addItem("FOPDT")
        self.dropdown.addItem("SOPDT")
        self.model_selector.addWidget(self.dropdown)
        self.selection_label = QLabel("Y1 - U1")
        self.selection_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.selection_label)
        self.main_layout.addLayout(self.model_selector)
        self.stackedLayout = QStackedLayout()
        self.fopdtForm = fopdt_form(self.update_UI)

        self.stackedLayout.addWidget(self.fopdtForm)
        self.stackedLayout.addWidget(QLabel("SOPDT"))
        # connect dropdown to stacked layout
        self.dropdown.editTextChanged.connect(self.stackedLayout.setCurrentIndex)

        self.main_layout.addLayout(self.stackedLayout)
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.setWidget(self.main_widget)

    def on_model_select(self,i,j):
        global selected_model
        selected_model = (i,j)
        #update model GUI
        self.selection_label.setText("Y{} - U{}".format(i+1,j+1))
        if type(globals.models[i][j]) is FOPDT:
            self.dropdown.setCurrentIndex(0)
            self.fopdtForm.set_values(globals.models[i][j])

    def update_UI(self):
        global selected_model
        print(selected_model)
        i,j = selected_model
        print(i,j)
        if True: # check for model type
            globals.models[i][j].K = self.fopdtForm.get_k()
            globals.models[i][j].tau = self.fopdtForm.get_tau()
            globals.models[i][j].theta = self.fopdtForm.get_theta()

class fopdt_form(QWidget):
    def __init__(self,update_model,parent=None):
        super(fopdt_form, self).__init__(parent)
        self.form = QFormLayout()
        self.k_input = QLineEdit("0")
        self.tau_input = QLineEdit("1")
        self.theta_input = QLineEdit("0")

        self.k_input.textEdited.connect(update_model)
        self.tau_input.textEdited.connect(update_model)
        self.theta_input.textEdited.connect(update_model)

        self.form.addRow(QLabel("Gain: "),self.k_input)
        self.form.addRow(QLabel("Time constant: "),self.tau_input)
        self.form.addRow(QLabel("Dead Time: "),self.theta_input)
        self.setLayout(self.form)

    def get_k(self):
        try:
            return float(self.k_input.text())
        except:
            print("invalid input!")
            return 0
    
    def get_tau(self):
        try:
            return float(self.tau_input.text())
        except:
            print("invalid input!")
            return 1

    def get_theta(self):
        try:
            return float(self.theta_input.text())
        except:
            print("invalid input!")
            return 0

    def set_values(self,model):
        self.k_input.setText(str(model.K))
        self.tau_input.setText(str(model.tau))
        self.theta_input.setText(str(model.theta))

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
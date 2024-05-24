import sys
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from CustomUtilities import FOPDT,PID_Controller,Centralized_PI
from numpy import inf
import globals

contInd = 0

class ControlEditor(QDockWidget):
    def __init__(self, parent = None):
        super(ControlEditor, self).__init__(parent)
        self.setMinimumWidth(200)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.addControl = QHBoxLayout()
        self.nameLabel = QLineEdit()
        self.nameLabel.textEdited.connect(self.on_name_changed)
        self.contComboBox = QComboBox()
        self.contComboBox.activated.connect(self.on_controller_changed)
        self.contComboBox.setMinimumWidth(120)
        self.addBtn = QPushButton("")
        self.addBtn.setMinimumSize(40,40)
        self.addBtn.setToolTip("Add new controller")
        self.addBtn.setIcon(QIcon('res/addModel.png'))
        self.addBtn.clicked.connect(self.on_add_new_controller)
        self.removeBtn = QPushButton("")
        self.removeBtn.setMinimumSize(40,40)
        self.removeBtn.setIcon(QIcon('res/bin.png'))
        self.removeBtn.setToolTip("Delete controller")
        self.removeBtn.clicked.connect(self.on_remove_controller)
        self.addControl.addWidget(self.nameLabel)
        self.addControl.addWidget(self.contComboBox)
        self.addControl.addWidget(self.addBtn)
        self.addControl.addStretch()
        self.addControl.addWidget(self.removeBtn)
        self.main_layout.addLayout(self.addControl)
        self.model_selector = QHBoxLayout()
        self.model_selector.addWidget(QLabel("Control Method: "))
        self.dropdown = QComboBox()
        self.dropdown.addItem("PID")
        self.dropdown.addItem("Centralized PI")
        # self.dropdown.addItem("SOPDT")
        self.model_selector.addWidget(self.dropdown)
        self.selection_label = QLabel("None")
        self.selection_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.selection_label)
        self.main_layout.addLayout(self.model_selector)
        self.stackedLayout = QStackedLayout()
        self.pidLayout = pid_layout()
        self.refresh_dropdown()
        self.stackedLayout.addWidget(self.pidLayout)
        self.stackedLayout.addWidget(QLabel("Centralized PI"))
        # connect dropdown to stacked layout
        self.dropdown.editTextChanged.connect(self.stackedLayout.setCurrentIndex)

        self.main_layout.addLayout(self.stackedLayout)
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.setWidget(self.main_widget)

    def on_controller_changed(self):
        i = self.contComboBox.currentIndex()
        name = globals.controller_list[i].name
        self.selection_label.setText(name)
        self.nameLabel.setText(name)
        global contInd
        contInd = i
        try:
            self.stackedLayout.itemAt(0).widget().refresh_UI()
        except:
            print("no refresh method found")

    def on_add_new_controller(self):
        name = "Controller{}".format(len(globals.controller_list)+1)
        globals.controller_list.append(PID_Controller(5.5,0.03,15,name))
        global contInd
        contInd = len(globals.controller_list)-1
        self.nameLabel.setText(name)
        self.nameLabel.selectAll()
        self.selection_label.setText(name)
        self.refresh_dropdown()
        self.contComboBox.setCurrentIndex(contInd)
        self.nameLabel.setFocus()

    def on_remove_controller(self):
        print(self.contComboBox.currentIndex())
        try:
            del globals.controller_list[self.contComboBox.currentIndex()]
        except:
            print("failed to remove controller")
        self.refresh_dropdown()

    def refresh_dropdown(self):
        if len(globals.controller_list)<1:
            self.nameLabel.setDisabled(True)
            self.contComboBox.setDisabled(True)
        else:
            self.nameLabel.setDisabled(False)
            self.contComboBox.setDisabled(False)
        self.contComboBox.clear()
        for cont in globals.controller_list:
            self.contComboBox.addItem(cont.name)

        try:
            self.stackedLayout.itemAt(0).widget().refresh_UI()
        except:
            print("no refresh method found")

    def on_name_changed(self):
        name = self.nameLabel.text()
        i = self.contComboBox.currentIndex()
        globals.controller_list[i].name = name
        self.contComboBox.setItemText(i,name)
        self.selection_label.setText(name)

class pid_layout(QWidget):
    def __init__(self,parent=None):
        super(pid_layout, self).__init__(parent)
        self.main_layout = QVBoxLayout()
        self.kpLayout = QHBoxLayout()
        self.kpLayout.addWidget(QLabel("Kp"))
        self.kpEdit = QLineEdit("0.1")
        self.kpEdit.textEdited.connect(self.update_model)
        self.kpTunable = QCheckBox()
        self.kpTunable.stateChanged.connect(self.on_setting_change)
        self.kpTunable.setToolTip("Tunable parameter")
        self.kpLower = QLineEdit("-inf")
        self.kpUpper = QLineEdit("inf")
        self.kpLower.textEdited.connect(self.update_model)
        self.kpUpper.textEdited.connect(self.update_model)
        self.kpLayout.addWidget(self.kpEdit)
        self.kpLayout.addWidget(self.kpTunable)
        self.kpLayout.addWidget(QLabel("Bounds: "))
        self.kpLayout.addWidget(self.kpLower)
        self.kpLayout.addWidget(self.kpUpper)
        self.main_layout.addLayout(self.kpLayout)

        self.kiLayout = QHBoxLayout()
        self.kiLayout.addWidget(QLabel("Ki"))
        self.kiEdit = QLineEdit("0.1")
        self.kiEdit.textEdited.connect(self.update_model)
        self.kiTunable = QCheckBox()
        self.kiTunable.stateChanged.connect(self.on_setting_change)
        self.kiTunable.setToolTip("Tunable parameter")
        self.kiLower = QLineEdit("-inf")
        self.kiUpper = QLineEdit("inf")
        self.kiLower.textEdited.connect(self.update_model)
        self.kiUpper.textEdited.connect(self.update_model)
        self.kiLayout.addWidget(self.kiEdit)
        self.kiLayout.addWidget(self.kiTunable)
        self.kiLayout.addWidget(QLabel("Bounds: "))
        self.kiLayout.addWidget(self.kiLower)
        self.kiLayout.addWidget(self.kiUpper)
        self.main_layout.addLayout(self.kiLayout)

        self.kdLayout = QHBoxLayout()
        self.kdLayout.addWidget(QLabel("Kd"))
        self.kdEdit = QLineEdit("0.1")
        self.kdEdit.textEdited.connect(self.update_model)
        self.kdTunable = QCheckBox()
        self.kdTunable.stateChanged.connect(self.on_setting_change)
        self.kdTunable.setToolTip("Tunable parameter")
        self.kdLower = QLineEdit("-inf")
        self.kdUpper = QLineEdit("inf")
        self.kdLower.textEdited.connect(self.update_model)
        self.kdUpper.textEdited.connect(self.update_model)
        self.kdLayout.addWidget(self.kdEdit)
        self.kdLayout.addWidget(self.kdTunable)
        self.kdLayout.addWidget(QLabel("Bounds: "))
        self.kdLayout.addWidget(self.kdLower)
        self.kdLayout.addWidget(self.kdUpper)
        self.main_layout.addLayout(self.kdLayout)
        self.on_setting_change()

        self.io_layout = QHBoxLayout()
        self.outComboBox = QComboBox()
        self.outComboBox.activated.connect(self.on_value_change)
        self.refresh_dropdowns()
        self.io_layout.addWidget(QLabel("Controlled Variable: "))
        self.io_layout.addWidget(self.outComboBox)
        self.main_layout.addLayout(self.io_layout)

        self.setLayout(self.main_layout)

    def refresh_dropdowns(self):
        self.outComboBox.clear()
        self.outComboBox.addItem("None")
        for i in range(1,globals.n+1):
            self.outComboBox.addItem("U{}".format(i))

    def on_value_change(self):
        try:
            globals.controller_list[contInd].contVarInd = self.outComboBox.currentIndex()
            self.update_model()
        except: pass

    def on_setting_change(self):
        self.kpLower.setDisabled(not self.kpTunable.isChecked())
        self.kpUpper.setDisabled(not self.kpTunable.isChecked())
        self.kiLower.setDisabled(not self.kiTunable.isChecked())
        self.kiUpper.setDisabled(not self.kiTunable.isChecked())
        self.kdLower.setDisabled(not self.kdTunable.isChecked())
        self.kdUpper.setDisabled(not self.kdTunable.isChecked())
        self.update_model()

    def update_model(self):
        global contInd
        try:
            globals.controller_list[contInd].Kp = float(self.kpEdit.text())
            globals.controller_list[contInd].Ki = float(self.kiEdit.text())
            globals.controller_list[contInd].Kd = float(self.kdEdit.text())
            globals.controller_list[contInd].kpTunable = self.kpTunable.isChecked()
            globals.controller_list[contInd].kiTunable = self.kiTunable.isChecked()
            globals.controller_list[contInd].kdTunable = self.kdTunable.isChecked()
            globals.controller_list[contInd].kpUpper = eval(self.kpUpper.text())
            globals.controller_list[contInd].kpUpper = eval(self.kpUpper.text())
            globals.controller_list[contInd].kiUpper = eval(self.kiUpper.text())
            globals.controller_list[contInd].kiUpper = eval(self.kiUpper.text())
            globals.controller_list[contInd].kdUpper = eval(self.kdUpper.text())
            globals.controller_list[contInd].kdUpper = eval(self.kdUpper.text())
            # globals.controller_list[contInd][2] = self.outComboBox.currentIndex()
        except:
            print("invalid values")

    def refresh_UI(self):
        global contInd
        print("updating ui",contInd)
        print([cont.kpTunable for cont in globals.controller_list])
        print([cont.kiTunable for cont in globals.controller_list])
        print([cont.kdTunable for cont in globals.controller_list])
        self.refresh_dropdowns()
        try:
            self.kpEdit.setText(str(globals.controller_list[contInd].Kp))
            self.kiEdit.setText(str(globals.controller_list[contInd].Ki))
            self.kdEdit.setText(str(globals.controller_list[contInd].Kd))
            self.kpTunable.setChecked(globals.controller_list[contInd].kpTunable)
            self.kiTunable.setChecked(globals.controller_list[contInd].kiTunable)
            self.kdTunable.setChecked(globals.controller_list[contInd].kdTunable)
            self.kpUpper.setText(str(globals.controller_list[contInd].kpUpper))
            self.kpLower.setText(str(globals.controller_list[contInd].kpLower))
            self.kiUpper.setText(str(globals.controller_list[contInd].kiUpper))
            self.kiLower.setText(str(globals.controller_list[contInd].kiLower))
            self.kdUpper.setText(str(globals.controller_list[contInd].kdUpper))
            self.kdLower.setText(str(globals.controller_list[contInd].kdLower))
            self.outComboBox.setCurrentIndex(globals.controller_list[contInd].contVarInd)
        except:
            print("error refreshing UI")
        

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
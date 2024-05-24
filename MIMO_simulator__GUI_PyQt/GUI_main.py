import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from model_editor import ModelEditor
from signal_editor import SignalEditor
from results_editor import ResultsEditor
from control_editor import ControlEditor
from optimizer_editor import OptimizerEditor
from CustomUtilities import FOPDT
from CustomUtilities import MIMO_Model
import numpy as np
import pickle
import globals

selected_model = (0,0)
selected_signal = ("R",0)
results_window = None
signals_window = None
model_window = None
central_window = None
control_window = None
optimizer_window = None

class window(QWidget):
    def __init__(self, on_model_select,on_signal_select,parent = None):
        super(window, self).__init__(parent)
        self.setWindowTitle("MIMO Control Modeller")
        self.setMinimumSize(500,200)
        self.mainLayout = QVBoxLayout()
        self.on_model_select = on_model_select
        self.on_signal_select = on_signal_select

        self.dimForm = QFormLayout()
        self.m_sens = QSpinBox()
        self.m_sens.setValue(2)
        self.n_sens = QSpinBox()
        self.n_sens.setValue(2)
        self.n_sens.valueChanged.connect(lambda: self.updateDimensions(False))
        self.m_sens.valueChanged.connect(lambda: self.updateDimensions(False))
        self.dimForm.addRow(QLabel("No. of sensors: "),self.m_sens)
        self.dimForm.addRow(QLabel("No. of actuators: "),self.n_sens)
        self.mainLayout.addLayout(self.dimForm)
        
        self.display_model = QVBoxLayout()
        self.display_model.addWidget(QLabel("Interaction Models: "))
        self.display_model.addSpacing(20)
        self.grid = QGridLayout()
        
        self.on_model_select(0,0)
        self.on_signal_select("R",0)
                
        # self.display_model.addLayout(self.grid)

        self.mainLayout.addSpacing(20)
        self.modelScrollArea = QScrollArea()
        self.gridContainer = QWidget()
        self.modelScrollArea.setWidget(self.gridContainer)
        self.gridContainer.setLayout(self.grid)
        self.mainLayout.addLayout(self.display_model)
        self.modelScrollArea.setWidgetResizable(True)
        self.display_model.addWidget(self.modelScrollArea)
        self.ff_panel = QHBoxLayout()
        self.ff_panel.addWidget(QLabel("Enable Feedforward Compensation: "))
        self.enable_ff = QCheckBox()
        self.enable_ff.stateChanged.connect(self.on_config_change)
        self.ff_panel.addWidget(self.enable_ff)
        self.display_model.addLayout(self.ff_panel)
        self.display_model.addStretch()
        self.setLayout(self.mainLayout)
        self.updateDimensions()

    def on_config_change(self):
        globals.use_FF_gains=self.enable_ff.isChecked()

    def updateDimensions(self,onLoad = False):
        if not onLoad:
            globals.models = []
            globals.m,globals.n = self.m_sens.value(),self.n_sens.value()
            globals.R = np.zeros((globals.m,globals.tf))
            globals.U = np.zeros((globals.n,globals.tf))
            globals.Y = np.zeros((globals.m,globals.tf))
            globals.models = [[FOPDT(0,1,0) for j in range(globals.n)] for i in range(globals.m)]
            print("dimension changed to: ",(globals.m,globals.n))
        m,n = globals.m,globals.n
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # self.grid = QGridLayout()
        self.grid.addWidget(QLabel("Set Point"),0,0)
        for i in range(1,m+1):
            self.grid.addWidget(signal_display("R",i,self.on_signal_select),i,0)
        for j in range(1,n+1):
            self.grid.addWidget(signal_display("U",j,self.on_signal_select),0,j)
        for i in range(m):
            for j in range(n):
                self.grid.addWidget(model_display(i,j,self.on_model_select),i+1,j+1)
        # self.modelScrollArea.setLayout(self.grid)
        self.modelScrollArea.setWidgetResizable(True)
        global results_window,model_window,signals_window
        model_window.on_model_select(0,0)
        signals_window.on_signal_select("R",1)
        results_window.update_UI()
        control_window.refresh_dropdown()
        
class model_display(QWidget):
    def __init__(self, i,j,on_selection_change,parent = None):
        super(model_display, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.on_selection_change = on_selection_change
        self.editBtn = QPushButton("  Y{} - U{}".format(i+1,j+1))
        self.editBtn.setIcon(QIcon('res/block.png'))
        self.editBtn.setContentsMargins(5,5,5,5)
        self.editBtn.setToolTip("Edit in Model Editor")
        self.editBtn.setMinimumHeight(60)
        # self.editBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editBtn.clicked.connect(lambda:self.select_model(i,j))
        self.layout.addWidget(self.editBtn)
        self.setMouseTracking(True)
        self.setLayout(self.layout)
    
    def select_model(self,i,j):
        global selected_model,model_window
        model_window.setVisible(True)
        selected_model = (i,j)
        self.on_selection_change(i,j)

class signal_display(QWidget):
    def __init__(self,type, i,on_signal_select,parent = None):
        super(signal_display, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.type = type
        self.on_signal_select = on_signal_select
        self.editBtn = QPushButton("  R{}".format(i) if type=="R" else " U{}".format(i),self)
        self.editBtn.setIcon(QIcon("res/wave.png"))
        self.editBtn.setContentsMargins(5,5,5,5)
        self.editBtn.setToolTip("Edit in Signal Editor")
        # self.editBtn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.editBtn.setMinimumSize(60,60)
        self.editBtn.clicked.connect(lambda:self.select_signal(i))
        # self.layout.addWidget(self.label)
        self.layout.addWidget(self.editBtn)
        # self.layout.addStretch()
        self.setMouseTracking(True)
        self.setLayout(self.layout)
    
    def select_signal(self,i):
        global selected_signal
        selected_signal = (self.type,i)
        self.on_signal_select(self.type,i)

class ribbon(QDockWidget):
    def __init__(self,parent=None):
        super(ribbon, self).__init__(parent)
        self.setMaximumHeight(120)
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.center_container = QWidget()
        self.center_layout = QHBoxLayout()
        self.center_container.setMinimumWidth(500)
        self.main_layout.addStretch()
        self.runBtn = QPushButton("")
        self.runBtn.setIcon(QIcon('res/play-button.png'))
        self.runBtn.setFixedSize(40,40)
        self.runBtn.setToolTip("Run")
        self.runBtn.clicked.connect(self.run_model)
        self.runBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.center_layout.addWidget(QLabel("Duration: "))
        self.duration = QLineEdit(str(globals.tf))
        self.duration.editingFinished.connect(self.on_duration_changed)
        self.center_layout.addWidget(self.duration)
        self.center_layout.addWidget(self.runBtn)
        self.center_container.setLayout(self.center_layout)
        self.main_layout.addWidget(self.center_container)
        self.main_layout.addStretch()
        self.main_widget.setLayout(self.main_layout)
        self.setWidget(self.main_widget)
    
    def on_duration_changed(self):
        try:
            new_tf = int(self.duration.text())
            if new_tf<globals.tf:
                globals.R = globals.R[:,:new_tf]
                globals.U = globals.U[:,:new_tf]
                globals.Y = globals.Y[:,:new_tf]
            if new_tf>=globals.tf:
                globals.R = np.append(globals.R,np.zeros((globals.m,new_tf-globals.tf)),1)
                globals.U = np.append(globals.U,np.zeros((globals.n,new_tf-globals.tf)),1)
                globals.Y = np.append(globals.Y,np.zeros((globals.m,new_tf-globals.tf)),1)
            globals.tf = new_tf
            globals.t = np.array(range(globals.tf))
        except:
            print("Enter valid duration")

    def run_response_test(self):
        print("Running response test...")
        global results_window
        # globals.update_process_model()
        globals.process_model = MIMO_Model((globals.Y.shape[0],globals.U.shape[0]),[0 for i in range(globals.Y.shape[0])],globals.models)
        globals.run_response_test(results_window.on_results_calculated)
        print("Evaluated responses.")

    def run_model(self):
        print("Running")
        global results_window
        globals.process_model = MIMO_Model((globals.Y.shape[0],globals.U.shape[0]),[30 for i in range(globals.Y.shape[0])],globals.models)
        globals.run_model(self.on_complete)
        print("Evaluated responses.")

    def on_complete(self):
        results_window.on_results_calculated()
        signals_window.update_preview()
      
def save():
    dlg = QFileDialog()
    path = dlg.getSaveFileName()[0]
    dim = np.array([globals.m,globals.n])
    model_arr = np.zeros((dim[0],dim[1],5))
    for i in range(dim[0]):
        for j in range(dim[1]):
            model_arr[i,j] = globals.models[i][j].encode()
    data = [dim,globals.R,globals.U,globals.Y,model_arr,globals.controller_list]

    with open(path,'wb') as outfile:
        pickle.dump(data,outfile,pickle.HIGHEST_PROTOCOL)
    print("Saved")

def load(on_load_complete):
    try:
        path = QFileDialog().getOpenFileName()[0]
        with open(path,'rb') as infile:
            data = pickle.load(infile)
        [dim,globals.R,globals.U,globals.Y,model_arr,globals.controller_list] = data
        globals.m,globals.n = dim[0],dim[1]
        globals.models = [[FOPDT(0,1,0) for j in range(dim[1])] for i in range(dim[0])]
        for i in range(dim[0]):
            for j in range(dim[1]):
                # TO: DO determine model type
                globals.models[i][j].decode(model_arr[i,j])
        print("Loaded")
        on_load_complete(True)
    except:
        print("Error loading file")

def main():
    style = """
    QWidget {
        background-color: #2b2b2b;
        color: #b1b1b1;
        border: 1px solid #3a3a3a;
    }
    QPushButton {
        background-color: #505050;
        border: none;
        color: #b1b1b1;
    }
    QPushButton:hover {
        background-color: #707070;
    }
    QPushButton:pressed {
        background-color: #303030;
    }
    QLabel {
        color: #b1b1b1;
        border-width: 0;
    }
    QDockWidget {
        border: 1px solid black;
    }
    QLineEdit:disabled {
        
        color: #404040;
    }
    QComboBox:disabled {
        color: #808080;
    }
    QCheckBox {
        color: #111111;
        padding: 0px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
"""
    app = QApplication(sys.argv)
    if globals.darkTheme:
        app.setStyleSheet(style)
    primary_window = QMainWindow()
    primary_window.setWindowIcon(QIcon('res/MIMO.png'))

    model_editor = ModelEditor("Model Editor")
    signal_editor = SignalEditor("Signal Editor")
    results_editor = ResultsEditor("Results ")
    control_editor = ControlEditor("Control Editor")
    optimizer_editor = OptimizerEditor("Optimizer")
    global results_window,signals_window,model_window,control_window,optimizer_window
    results_window,signals_window,model_window = results_editor,signal_editor,model_editor
    control_window,optimizer_window = control_editor,optimizer_editor
    main_ribbon = ribbon()

    model_editor.setFeatures(QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
    signal_editor.setFeatures(QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
    main_ribbon.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    results_editor.setFeatures(QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
    control_editor.setFeatures(QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
    optimizer_editor.setFeatures(QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
    primary_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,model_editor)
    primary_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,signal_editor)
    primary_window.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,main_ribbon)
    primary_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,control_editor)
    primary_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,results_editor)
    # primary_window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea,optimizer_editor)
    center_window = window(model_editor.on_model_select,signal_editor.on_signal_select)
    primary_window.setCentralWidget(center_window)

    menubar = primary_window.menuBar()
    file_menu = menubar.addMenu("&File")
    edit_menu = menubar.addMenu("&Edit")
    window_menu = menubar.addMenu("&Window")
    exit_action = QAction("Exit", primary_window)
    save_action = QAction("Save",primary_window)
    load_action = QAction("Load",primary_window)
    exit_action.triggered.connect(primary_window.close)
    save_action.triggered.connect(save)
    load_action.triggered.connect(lambda: load(center_window.updateDimensions))
    file_menu.addAction(save_action)
    file_menu.addAction(load_action)
    file_menu.addAction(exit_action)
    primary_window.setWindowTitle("MIMO Control Simulator")
    primary_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

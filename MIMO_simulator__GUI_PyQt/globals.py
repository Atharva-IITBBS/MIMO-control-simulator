import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
# from scipy.integrate import odeint
from CustomUtilities import FOPDT,waveform,MIMO_Model,PID_Controller   # custom library

darkTheme = False

m = 2 # no. of sensors
n = 2 # no. of controller/actuators

use_FF_gains = True

models = [[FOPDT(0,1,0)for i in range(n)] for j in range(m)]

# models[0][0] = FOPDT(2,10,15)
# models[0][1] = FOPDT(0.2,20,0)
# models[0][3] = FOPDT(-10,20,0)

# models[1][0] = FOPDT(0.5,25,0)
# models[1][1] = FOPDT(2,20,8)
# models[1][2] = FOPDT(0.3,30,0)
# models[1][3] = FOPDT(-7.5,20,0)

# models[2][1] = FOPDT(0.5,30,0)
# models[2][2] = FOPDT(2,30,5)
# models[2][3] = FOPDT(-5,20,0)

Y_init = np.ones(m)*30      # initial process variable values
tf = 2400                   # run time in seconds
t = np.array(range(tf))     # time array
U = np.zeros((n,tf))        # Control array
Y = np.ones((m,tf))*30      # ProcessVariable array
R = np.ones((m,tf))*30      # Set point array

controller_list = [] #--> U[contVarInd-1]

process_model = MIMO_Model((m,n),Y_init)
process_model.model = models

def update_process_model():
    print(Y.shape[0],U.shape[0])
    process_model = MIMO_Model((Y.shape[0],U.shape[0]),np.ones(Y.shape[0])*0)
    process_model.model = models
    
pid1 = PID_Controller(0.4,0.01,0.02)
pid2 = PID_Controller(0.4,0.01,0.02)
pid3 = PID_Controller(0.4,0.01,0.02)
pid4 = PID_Controller(0.001,0.005,0.02)

Kfs = []

def evaluate_model():
    for cont in controller_list:
        cont.reset()
    global Kfs
    IAE = 0
    for ti in range(len(t)-1):
        Error = R[:,ti] - Y[:,ti]
        IAE+=sum(np.abs(Error))
        # U[3,ti] = min([10,max([0,pid4.Output(-0.5*Error[0]-0.25*Error[1]-0.25*Error[2])[0]])])
        m,n = len(Y),len(U)
        O = U[:,ti]
        for cont in controller_list:
            i = cont.contVarInd-1 # variable of controlled index -> U[i]
            if i==-1:continue
            if i>=n:
                print("Invalid control varialbe: ", "U{}".format(i))
                break
            O[i] = cont.Output(Error[i])[0]

        # apply FF compensation
        if use_FF_gains:
            for i in range(m):
                U[i,ti] = O[i]
                for j in range(n):
                    if i!=j:
                        U[i,ti] -= Kfs[i][j]*O[j]

        # apply controller bounds
        for i in range(n):
            U[i,ti] = np.clip(O[i],0,100)

        Y[:,ti+1] = process_model.getResponse(U,[t[ti],t[ti+1]])[:,-1]
        
    return IAE

def run_model(on_complete = None):

    if use_FF_gains:
        A = process_model.getGainMatrix()
        # construct default FF gain matrix --> Kd/Kp for all cross interactions
        global Kfs
        Kfs = np.ones((m,n))
        for i in range(m):
            for j in range(n):
                if i!=j:
                    Kfs[i][j] = A[i][j]/A[i][i]

    evaluate_model()
    if on_complete is not None:
        on_complete()

def run_response_test(on_complete = None):
    print(Y.shape,U.shape)
    for ti in range(len(t)-1):
        Y[:,ti+1] = process_model.getResponse(U,[t[ti],t[ti+1]])[:,-1]
    if on_complete is not None:
        on_complete()

def objective_func(X): 
    IAE = evaluate_model()
    return IAE

def run_optimizer(tune_ff_gains = True, on_complete = None):
    global controller_list
    # get initial values
    X0 = []
    for cont in controller_list:
        if cont.kpTunable: X0.append(cont.kp)

    res = minimize(objective_func,X0)

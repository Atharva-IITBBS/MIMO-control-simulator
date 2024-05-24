from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt

class FOPDT():
    def __init__(self,K,tau,theta):
        self.K = K
        self.tau = tau
        self.theta = theta

    def fopdt(self,y,t,U,K,tau,theta):
        tp = min([max([0,t-theta]),len(U)-1])
        dydt = (-y + K*U[int(tp)])/tau
        return dydt

    # returns encoded array of size 5
    def encode(self):
        return np.array([1,self.K,self.tau,self.theta,0])
    
    def decode(self,arr):
        self.K,self.tau,self.theta = arr[1],arr[2],arr[3]

    # returns Y[i+1] for i'th time step
    def getNext(self,Yi,U,t_array):
        return odeint(self.fopdt,Yi,t_array,args=(U,self.K,self.tau,self.theta))[-1][0]
    
class waveform():
    def steps(stepList,tf): # stepList --> eg: [(0,0),(100,40),(200,0)]
        u = np.zeros(tf)
        for s in stepList:
            u[s[0]:] = s[1]             
        return u
    
class PID_Controller():
    def __init__(self,Kp = 1.0,Ki = 1.0,Kd = 1.0,name = "pid"):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.name = name
        # Bounds
        self.kpTunable = False
        self.kpUpper = np.inf
        self.kpLower = -np.inf
        self.kiTunable = False
        self.kiUpper = np.inf
        self.kiLower = -np.inf
        self.kdTunable = False
        self.kdUpper = np.inf
        self.kdLower = -np.inf

        # Controlled variable index
        self.contVarInd = 0 # default -> None

        self.ierr = 0.0
        self.prev_error = 0.0
    
    def Output(self,error,dt=1):
        P = self.Kp*error
        self.ierr += error*dt
        I = self.Ki*self.ierr
        D = self.Kd*(error - self.prev_error)/dt
        self.prev_error = error

        op = P+I+D

        return [op]
    
    def reset(self):
        self.ierr = 0
        self.prev_error = 0

class Centralized_PI():
    def __init__(self,GainMatrix,delta,eps,name = "Centralized PI"):
        self.K = GainMatrix
        self.K_1 = np.linalg.inv(self.K)
        self.K_p = delta*self.K_1
        self.K_i = eps*self.K_1
        self.name = name
        self.IErr = np.zeros((self.K.shape[0],1))

    def Output(self,error,dt=1):
        P = np.matmul(self.K_p,error)
        self.IErr+=error*dt
        I = np.matmul(self.K_i,self.IErr)
        return P+I
    
    def reset(self):
        self.IErr = np.zeros((self.K.shape[0],1))

# m -> no. of sensors
# n -> no. of actuators
# Y_init -> list of initial sensor readings
class MIMO_Model:
    def __init__(self,shape,Y_init,model=None,useDeadTimes = True) -> None:
        self.m,self.n = shape
        # FOPDT(K,tau,theta)
        if model is not None:
            self.model = model
        else:
            self.model = [[FOPDT(0,1,0)for i in range(self.n)] for j in range(self.m)]
        # self.model = [[FOPDT(0.634,184,8),FOPDT(0.1,278,30)],
        #               [FOPDT(0.227,297,49),FOPDT(0.326,156,13)]]
        
        self.state = np.zeros((self.m,self.n))

        if not useDeadTimes:
            for i in self.model:
                for j in i:
                    j.theta=0

        self.Y_init = Y_init

    def getModelWithoutDelay(self):
        model1 = self.model.copy()
        for i in model1:
                for j in i:
                    j.theta=0
        return model1

    def getGainMatrix(self):
        return [[self.model[i][j].K for j in range(self.n)] for i in range(self.m)]

    def reset(self,Y_init):
        self.state = np.zeros((self.m,self.n))
        self.Y_init = Y_init

    def getResponse(self,U,t_array):
        Y = np.zeros((self.m,1))
        for i in range(self.m):
            Y[i,0] = self.Y_init[i]
            for j in range(self.n):
                self.state[i][j] = self.model[i][j].getNext(self.state[i][j],U[j],t_array)
                Y[i,0] += self.state[i][j]

        return Y
    
tclab_model = MIMO_Model((2,2),[27,27])
tclab_model.model = [[FOPDT(0.634,184,8),FOPDT(0.1,278,30)],
                      [FOPDT(0.227,297,49),FOPDT(0.326,156,13)]]
    

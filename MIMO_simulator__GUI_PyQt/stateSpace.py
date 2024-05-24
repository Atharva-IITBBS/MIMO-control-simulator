import numpy as np
from scipy.integrate import odeint

delta_t  = 1
class StateSpace():
    def __init__(self,A,B,C,D,Theta = 0):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.m = np.shape(self.B)[1]
        if len(np.shape(Theta))!=0:
            self.Theta = Theta
        else:
            self.Theta = np.zeros(self.m)

    def x_dot(self,X,t,U):
        U_ = self.U_deadTime(U,t)
        X = np.atleast_2d(X).T
        return np.asarray(np.matmul(self.A,X)+np.matmul(self.B,U_)).reshape(-1)
    
    def U_deadTime(self,U,t):
        t_ = np.zeros(self.m)
        U_ = np.zeros((self.m,1))
        for i in range(self.m):
            t_[i] = min((U.shape[1]*delta_t-0.0001,max(0,t-self.Theta[i])))
            U_[i][0] = U[i,int(t_[i]/delta_t)]
        return U_

    def Output(self,U,X0,t_array):
        U_ = np.zeros((self.m,len(t_array)))
        for i in range(len(t_array)):
            U_[:,i:i+1] = self.U_deadTime(U,t_array[i])
        X = odeint(self.x_dot,X0,t_array ,args=(U,))
        return np.matmul(self.C,np.transpose(X))+np.matmul(self.D,U_)

    def get_observability_matrix(self):
        p = self.A.shape[0]
        O = self.C
        for i in range(1,p):
            O = np.vstack((O,np.matmul(self.C,np.linalg.matrix_power(self.A,i))))
        return O

    # def get_Controllability_matrix(self):


    def parallel(model1,model2): 
        Ap = np.zeros((model1.A.shape[0]+model2.A.shape[0],model1.A.shape[1]+model2.A.shape[1]))
        Bp = np.zeros((model1.B.shape[0]+model2.B.shape[0],model1.B.shape[1]+model2.B.shape[1]))
        Cp = np.zeros((model1.C.shape[0]+model2.C.shape[0],model1.C.shape[1]+model2.C.shape[1]))
        Dp = np.zeros((model1.D.shape[0]+model2.D.shape[0],model1.D.shape[1]+model2.D.shape[1]))
        Ap[:model1.A.shape[0],:model1.A.shape[1]] = model1.A
        Ap[model1.A.shape[0]:,model1.A.shape[1]:] = model2.A
        Bp[:model1.B.shape[0],:model1.B.shape[1]] = model1.B
        Bp[model1.B.shape[0]:,model1.B.shape[1]:] = model2.B
        Cp[:model1.C.shape[0],:model1.C.shape[1]] = model1.C
        Cp[model1.C.shape[0]:,model1.C.shape[1]:] = model2.C
        Dp[:model1.D.shape[0],:model1.D.shape[1]] = model1.D
        Dp[model1.D.shape[0]:,model1.D.shape[1]:] = model2.D
        Thetap = np.concatenate((model1.Theta,model2.Theta))
        return StateSpace(Ap,Bp,Cp,Dp,Thetap)
    
    def sum(model1,model2):
        if(model1.C.shape[1]!=model2.C.shape[1]):
            raise SystemExit("number of outputs of the models should be same")
        Ap = np.zeros((model1.A.shape[0]+model2.A.shape[0],model1.A.shape[1]+model2.A.shape[1]))
        Bp = np.zeros((model1.B.shape[0]+model2.B.shape[0],model1.B.shape[1]+model2.B.shape[1]))
        Cp = np.concatenate((model1.C,model2.C),1)
        Dp = np.concatenate((model1.D,model2.D),1)
        Ap[:model1.A.shape[0],:model1.A.shape[1]] = model1.A
        Ap[model1.A.shape[0]:,model1.A.shape[1]:] = model2.A
        Bp[:model1.B.shape[0],:model1.B.shape[1]] = model1.B
        Bp[model1.B.shape[0]:,model1.B.shape[1]:] = model2.B
        Thetap = np.concatenate((model1.Theta,model2.Theta))
        return StateSpace(Ap,Bp,Cp,Dp,Thetap)
    
    def subtract(model1,model2):
        if(model1.C.shape[1]!=model2.C.shape[1]):
            raise SystemExit("number of outputs of the models should be same")
        Ap = np.zeros((model1.A.shape[0]+model2.A.shape[0],model1.A.shape[1]+model2.A.shape[1]))
        Bp = np.zeros((model1.B.shape[0]+model2.B.shape[0],model1.B.shape[1]+model2.B.shape[1]))
        Cp = np.concatenate((model1.C,-model2.C),1)
        Dp = np.concatenate((model1.D,-model2.D),1)
        Ap[:model1.A.shape[0],:model1.A.shape[1]] = model1.A
        Ap[model1.A.shape[0]:,model1.A.shape[1]:] = model2.A
        Bp[:model1.B.shape[0],:model1.B.shape[1]] = model1.B
        Bp[model1.B.shape[0]:,model1.B.shape[1]:] = model2.B
        Thetap = np.concatenate((model1.Theta,model2.Theta))
        return StateSpace(Ap,Bp,Cp,Dp,Thetap)

from scipy.integrate import ode
import matplotlib.pyplot as plt

import sys
sys.path.append("..") # Adds higher directory to python modules path.

from circuit import *



Cir = Circuit(GND)

Cir.define([
    C("C1",     [GND,   1]      , 1e-6),
    L("L1",     [GND,   1]      , 1e-3),
    R("R1",     [GND,   1]      , 1000),
])


print("Number of Nodes: ", Cir.G.number_of_nodes())


#Get matricies, not symbolic
X, Y, RHS = Cir.matrices(symbolic=False)

#Solve System
Y = np.array(Y)
iY = np.linalg.inv(Y) 
iY = np.array(iY)
RHS = np.array(RHS, dtype=float)


def integration(t, Y):
    
    #Just filter out the dt entries from the state vector
    rhs = RHS.copy()
    idxs = sorted(list(X.state_vector["dt"].keys()))
    for y, idx in zip(Y, idxs):
        rhs[X.state_vector["dt"][idx]] = y

    state = rhs.dot(iY.transpose())
    dt = np.zeros(len(Y))

    for i, idx in enumerate(idxs):
        dt[i] = state[X.state_vector["dt"][idx]]

    return dt


r = ode(integration).set_integrator('dopri5')

t0 = 0      #Start Time
t1 = 0.01    #Stop Time
dt = 1e-6   #Time Step

#initial values at t0, one for every L or C
r.set_initial_value([1,1], t0)


state = []
time = []
while r.successful() and r.t < t1:
    r.integrate(r.t+dt)
    time.append(r.t)
    state.append(r.y) # keeping only position, not velocity
    

state = np.array(state)
time = np.array(time)


for i in range(len(state[0])):
    plt.plot(time*1e3, state[:,i])

plt.show()

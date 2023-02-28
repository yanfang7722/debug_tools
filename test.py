import numpy as np
from numpy import linalg as LA
dt = 0.1
A = np.array([[1, dt, 0.5*dt**2], [0, 1, dt], [0, 0, 1]])
B = np.array([1/6*dt**3, 0.5*dt**2, dt]).reshape(3, 1)
R = 1.0
weight = 4
tx=1
Q = weight * np.array([[1, tx, 0], [tx, tx*tx, 0], [0, 0, 0]])
P = Q.copy()

def get_tx(x):
    return 1-x*0.01*2

for i in range(10000):
    # tx = get_tx(i*dt)
    # Q = weight * np.array([[1, tx, 0], [tx, tx*tx, 0], [0, 0, 0]])
    M = np.matmul(np.matmul(A.transpose(), P),B)
    L = (R + np.matmul(np.matmul(B.transpose(), P),B))
    N = np.linalg.inv(L)
    P = np.matmul(np.matmul(A.transpose(),P), A) + Q - np.matmul(np.matmul(M,N),M.transpose())

    K = - np.matmul(N, M.transpose()) 
    S = A + np.matmul(B, K)-np.identity(np.shape(A)[0])

    w, _ = LA.eig(S)
    for item in w:
        if (item.real>=0):
            print (" i:",i*dt,"    s:",w)

# # Computed value function V  = x^T P x
# print("==P==\n",P)

# # print dynamic gain K
# print("==K==\n",K)

# validate stability
print("==s==\n",S)

w, _ = LA.eig(S)
print("==w==\n",w)
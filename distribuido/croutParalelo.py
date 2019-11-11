import scipy
import numpy as np
import threading
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.size

#A = [[45.0, -7.0, 8.0, -3.0], [-5.0, 75.0, 4.0, 1.0], [-3.0, -2.0, 88.0, 9.0 ], [-6.0, -3.0, -4.0, 98.0]]
A = scipy.array([[36.0, 3.0, -4.0, 5.0], [5.0, -45.0, 10.0, -2.0], [6.0, 8.0, 57.0, 5.0 ], [2.0, 3.0, -8.0, -42.0]])
n = len(A) 

L = scipy.array(np.zeros_like(A))
U = scipy.array(np.zeros_like(A))

#En crout los elementos de U[k][k] son iguales a 1
def crout():
    global L
    global U
    for k in range (0,n):
        sum1 = 0.0
        for p in range(0, k):
            sum1 += L[k][p]*U[p][k]
        #endfor

        U[k][k] = 1.0
        L[k][k] = A[k][k] - sum1 #depende del metodo

        if rank == 0:
            lik(k,n)
        elif rank == 1:
            ukj(k,n)
        else:
            exit(0)

    #endfor

    if rank == 0:
        print("\nL: ")
        print(L)
        U = comm.recv(source=1)
    else:
        print("\nU: ")
        print(U)
        comm.send(U,dest=0)
        exit(0)

    return L, U

def lik(k,n):
    global L
    global U
    for i in range(k+1, n):
        sum2 = 0.0
        for p in range(0,k):
            sum2 += L[i][p]*U[p][k]
        #endfor
        L[i][k] = (A[i][k]-sum2)/U[k][k]
        #Descomentar la siguiente linea para el paso a paso
        #print("\nL:\n",L)
    #endfor
    #return L

def ukj(k, n):
    global L
    global U
    for j in range(k+1, n):
        sum3 = 0
        for p in range(0, k):
            sum3 += L[k][p]*U[p][j]
        #endfor
        U[k][j]= (A[k][j]-sum3)/L[k][k]
        #Descomentar la siguiente linea para el paso a paso
        #print("\nU:\n",U)
    #endfor
    #return U

crout()

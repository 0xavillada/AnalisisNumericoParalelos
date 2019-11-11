from math import sqrt
import scipy
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.size

A = scipy.array([[45.0, -7.0, 8.0, -3.0], [-5.0, 75.0, 4.0, 1.0], [-3.0, -2.0, 88.0, 9.0 ], [-6.0, -3.0, -4.0, 98.0]])
n = len(A) 

L = scipy.array(np.zeros_like(A))
U = scipy.array(np.zeros_like(A))


#En cholesky los elementos de U[k][k] y L[k][k] son iguales
def cholesky():
    for k in range (0,n):
        sum1 = 0.0
        for p in range(0, k):
            sum1 += L[k][p]*U[p][k]
        #endfor
        #L[k][k]*U[k][k] = A[k][k] - sum1 #depende del metodo

        L[k][k] = float(sqrt(A[k][k] - sum1))
        U[k][k] = float(L[k][k])

        if rank == 0:
            lik(k,n)
        else:
            ukj(k,n)

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

    print("Desde aquí se hace solo desde el rank:",rank)
    print(L, U)
    return L, U

def lik(k, n):
    for i in range(k+1, n):
        sum2 = 0.0
        for p in range(0, k):
            sum2 += L[i][p]*U[p][k]
        #endfor
        L[i][k] = (A[i][k] - sum2)/U[k][k]
    #endfor
    return L

def ukj(k, n):
    for j in range(k+1, n):
        sum3 = 0.0
        for p in range(0, k):
            sum3 += L[k][p]*U[p][j]
        #endfor
        U[k][j] = (A[k][j] - sum3)/L[k][k]
    #endfor
    return U
    

cholesky()
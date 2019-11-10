from math import sqrt
import scipy
import numpy as np
import threading

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

        #paralelizar:
        t1 = threading.Thread(name="Hilo_L", target=lik, args=(k,n))
        
        #Paralelizar:   
        t2 = threading.Thread(name="Hilo_U", target=ukj, args=(k,n))

        t1.start()
        t2.start()

        t1.join()
        t2.join()
    #endfor
   
    print("L: ")
    print(L)
    print("")
    print("U: ")
    print(U)
    print("")
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

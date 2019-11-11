import math
import threading
from mpi4py import MPI

#Distribuido
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.size

ecuaciones = []
variables = []
cifras_sig = 0
maximo_iter = 0
n_incognitas = 0

error = 1
valores_iniciales = []
nueva_fila = []
error_list_diff=[]

lambda_value = 1

# PARALELISMO
n_hilos = 2
n_hilos_segment = n_incognitas
control_num_hilos = 0

if rank == 0:
    # ENTRADA DE DATOS -----------------------------------------------------------------------------
    try:
        n_incognitas = int(input("Numero de incognitas:"))
        n_hilos_segment = int(n_incognitas / n_hilos)
        if n_hilos_segment == 0:
            n_hilos_segment = 1
    except:
        print("> ERROR: Entrada invalida")
        exit(1)

    for ecuacion_index in range(n_incognitas):
        for variable in range(n_incognitas+1):
            try:
                if variable == n_incognitas:

                    variables.append(float(input("\nVaraiable A de la ecuacion numero"+str(ecuacion_index+1)+":")))
                    break

                variables.append(float(input("\nVaraiable X"+str(variable+1)+" de la ecuacion numero"+str(ecuacion_index+1)+":")))
            except:
                print("> ERROR: Entrada invalida")
                exit(1)
        ecuaciones.append(variables)
        variables = []

    for iniciales in range(n_incognitas):
        try:

            valores_iniciales.append(float(input("\nValor inicial para X"+str(iniciales+1)+":")))
        except:
            print("> ERROR: Entrada invalida")
            exit(1)

    try:

        cifras_sig = int(input("\nCifras significativas:"))

        maximo_iter = int(input("\nMaximo iteraciones:"))

        lambda_value = float(input("\nLambda de relajacion:"))

        n_hilos = int(input("\nNumero de hilos de ejecucion:"))

    except:
        print("> ERROR: Entrada invalida")
        exit(1)
    # ----------------------------------------------------------------------------------------------

def threading_segments(inicio, fin):

    global n_hilos_segment
    global n_hilos
    global control_num_hilos
    
    inicio_thread = inicio
    for hilo in range(n_hilos):
        if (inicio_thread + n_hilos_segment) >= fin or hilo == (n_hilos-1):
            t = threading.Thread(target=jacobi, args=(inicio_thread, fin))
            control_num_hilos+=1
            t.start()
            break
        else:
            t = threading.Thread(target=jacobi, args=(inicio_thread, (inicio_thread + n_hilos_segment)))
            control_num_hilos+=1
            t.start()
        inicio_thread += n_hilos_segment

def jacobi(inicio,fin):

    global valores_iniciales
    global error
    global error_list_diff
    global nueva_fila
    global control_num_hilos
    global ecuaciones
    global n_incognitas

    for x in range(0,n_incognitas):
        if x >= inicio:
            #print("x: ",x)
            nueva_fila.append(valores_iniciales[x])
        else:
            nueva_fila.append(0)

    for variables_index in range(inicio,fin):
        temp = 0
        for demas_variables in range(n_incognitas):
            if demas_variables == variables_index:
                continue
            else:
                temp += (-1*(ecuaciones[variables_index][demas_variables]*valores_iniciales[demas_variables]))

        nueva_fila[variables_index] = ( ecuaciones[variables_index][n_incognitas] + temp) / ecuaciones[variables_index][variables_index]

        # RELAJACION
        nueva_fila[variables_index] = lambda_value * nueva_fila[variables_index] + (1 - lambda_value )* valores_iniciales[variables_index]
        print("\nnueva fila: ",nueva_fila)
    # ERROR RELATIVO NORMA MAXIMO---------------------------------------
    for i in range(inicio,fin):
        error_list_diff.append(abs(nueva_fila[i]-valores_iniciales[i]))
    # ------------------------------------------------------------------
    #print(valores_iniciales,error,error_list_diff,nueva_fila)
    control_num_hilos-=1


if rank == 0:
    envio = []
    envio.append(n_incognitas)
    envio.append(variables)
    envio.append(valores_iniciales)
    envio.append(cifras_sig)
    envio.append(maximo_iter)
    envio.append(lambda_value)
    envio.append(n_hilos)
    envio.append(ecuaciones)
    #print("envio del 0 - 1")
    comm.send(envio,dest=1)


if rank == 1:
    #test = comm.recv(source=0)
    recivido = comm.recv(source=0)
    #print("recivido del 0 - 1")
    n_incognitas = recivido[0]
    variables = recivido[1]
    valores_iniciales = recivido[2]
    cifras_sig = recivido[3]
    maximo_iter = recivido[4]
    lambda_value = recivido[5]
    n_hilos = recivido[6]
    ecuaciones = recivido[7]

n_incognitas_medio = int(n_incognitas / 2)

cifras_sig = 0.5*(10**(-cifras_sig))
iteraciones = 0
while error > cifras_sig:
    if iteraciones > maximo_iter:
        print("> ERROR: Se llegó al maximo de iteraciones!")
        exit(1)
    
    hilo = 0
    if rank == 0:
        threading_segments(0,n_incognitas_medio)
        while control_num_hilos > 0:
            pass
        msg = comm.recv(source=1)
        errorRank1 = msg[0]
        nuevafRank1 = msg[1]
        
        print("error rank1:",errorRank1)
        print("nuevafRank rank1:",nuevafRank1)

        #print("recive del 1 - 2")
        error_list_diff = error_list_diff + errorRank1
        nueva_fila = nueva_fila[:1] + nuevafRank1[1:]
        print("queda asi nueva fila:",nueva_fila)
        print("queda asi el error:",error_list_diff)
        #print("rank 0 calculo: error list:",error_list_diff," nueva fila:",nueva_fila)
        error = max(error_list_diff) / max(map(abs,nueva_fila))
        for x in range(n_incognitas):
            valores_iniciales[x] = nueva_fila[x]
        comm.send((error,valores_iniciales), dest=1)

    if rank == 1:
        threading_segments(n_incognitas_medio,n_incognitas)
        while control_num_hilos > 0:
            pass
        comm.send((error_list_diff,nueva_fila), dest=0)
        msg = comm.recv(source=0)
        error = msg[0]
        valores_iniciales = msg[1]
    
    if rank == 0:
        print("rank:",rank)
        print("\n\n> Iteracion numero:",iteraciones)
        print("> Valores de Xn: ")
        for x in range(n_incognitas):
            print("X"+str(x+1)+" =",valores_iniciales[x])

        print("> Toleracia: +-",error)    
    
    nueva_fila.clear()
    error_list_diff.clear()
    iteraciones += 1

if rank == 0:
    # SALIDA ---------------------------------------------------------------------------------------
    print("\n\n> Iteracion numero:",iteraciones)
    print("> Valores de Xn: ")
    for x in range(n_incognitas):
        print("X"+str(x+1)+" =",valores_iniciales[x])

    print("> Toleracia: +-",error)
    # ----------------------------------------------------------------------------------------------

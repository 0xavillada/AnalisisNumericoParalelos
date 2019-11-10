import math
import threading
from mpi4py import MPI

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

    for x in range(inicio,fin):
        nueva_fila.append(valores_iniciales[x])

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

    # ERROR RELATIVO NORMA MAXIMO---------------------------------------
    for i in range(inicio,fin):
        error_list_diff.append(abs(nueva_fila[i]-valores_iniciales[i]))
    # ------------------------------------------------------------------
    control_num_hilos-=1


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.size
name = MPI.Get_processor_name()

mpi_particion = int (n_incognitas / size)
if mpi_particion < 1:
    mpi_particion = 1
indices = []
indiceInicial = 0
indiceFinal = mpi_particion

for x in range(size):
    indices.append((indiceInicial,indiceFinal))
    indiceInicial = indiceFinal

    if x == size - 1:
        indiceFinal = indiceInicial + n_incognitas
    else:
        indiceFinal = indiceInicial + mpi_particion

cifras_sig = 0.5*(10**(-cifras_sig))
iteraciones = 0
while error > cifras_sig:
    if iteraciones > maximo_iter:
        print("> ERROR: Se llegó al maximo de iteraciones!")
        exit(1)

    for procesador in range(size):
        if rank == procesador:
            threading_segments(indices[rank][0],indices[rank][1])
            while control_num_hilos > 0:
                pass

            if rank == 0:
                #se ensambla y se actualizan todos
                actualizaion 
                
            else:
                actualizacion = comm.recv(source=0)
                #se recive y se actualiza todo


    error = max(error_list_diff) / max(map(abs,nueva_fila))
    for x in range(n_incognitas):
        valores_iniciales[x] = nueva_fila[x]
    nueva_fila.clear()
    error_list_diff.clear()
    iteraciones += 1

# SALIDA ---------------------------------------------------------------------------------------
print("\n\n> Iteracion numero:",iteraciones)
print("> Valores de Xn: ")
for x in range(n_incognitas):
    print("X"+str(x+1)+" =",valores_iniciales[x])

print("> Toleracia: +-",error)
# ----------------------------------------------------------------------------------------------
import numpy as np

def RSI(t, periods=14):
    length = len(t)
    rsies = [np.nan]*length
         # La longitud de los datos no excede el período y no se puede calcular;
    if length <= periods:
        return rsies
         #Utilizado para cálculos rápidos;
    up_avg = 0
    down_avg = 0
 
         # Primero calcule el primer RSI, use los períodos anteriores + 1 dato para formar una secuencia de períodos;
    first_t = t[:periods+1]
    for i in range(1, len(first_t)):
                 #Precio aumentado;
        if first_t[i] >= first_t[i-1]:
            up_avg += first_t[i] - first_t[i-1]
                 #caída de los precios; 
        else:
            down_avg += first_t[i-1] - first_t[i]
    up_avg = up_avg / periods
    down_avg = down_avg / periods
    rs = up_avg / down_avg
    rsies[periods] = 100 - 100/(1+rs)
 
         # Lo siguiente utilizará cálculo rápido;
    for j in range(periods+1, length):
        up = 0
        down = 0
        if t[j] >= t[j-1]:
            up = t[j] - t[j-1]
            down = 0
        else:
            up = 0
            down = t[j-1] - t[j]
                 # Fórmula de cálculo similar a la media móvil;
        up_avg = (up_avg*(periods - 1) + up)/periods
        down_avg = (down_avg*(periods - 1) + down)/periods
        rs = up_avg/down_avg
        rsies[j] = 100 - 100/(1+rs)
    return rsies


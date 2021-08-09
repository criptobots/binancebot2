# binancebot2
Binance Bot es un script creado Para hacer trading automatico en la plataforma de binance 

Para utilizar Solo habria que instalar los paquetes Con:
pip install -r requirements.txt

Entrar a la carpeta USDtrading y renombrar el archivo configNew.py por config.py y colocar los datos de la api activada en binance.
si no tienes los datos de la api busca en youtube como generar api para binance.

Luego de colocar la key privada y publica en config.py
- ejectuar cualquiera de los tres bot creados

-rsi_bot: utiliza websoket para hacer una comprar por RSI si esta en sobreventa compra y vende cuando esta en sobrecompra

-usdt_bot : utiliza datos desde la api de binance y tiene dos estrategias para la compra y venta 
 - la primera estrategia es por Media aritmetica y grafica ascendente si el precio esta por debajo de la media y la curva de la grafica es ascendente compra.
 - la segunda estrategia se mezcla con la primera para comprar con sobreventa y vender en sobrecompra esta es opcional

 

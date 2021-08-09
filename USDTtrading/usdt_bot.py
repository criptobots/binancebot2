from binance.client import Client
from binance.enums import *
import time
import threading
import math
import csv
import itertools
import datetime
import numpy as np
import os,config
from functions import *
import pytz
#from scipy import stats
#import vlc
#import talib
#Tamaño de Inversion BTC


list_of_interval = [
KLINE_INTERVAL_1MINUTE, KLINE_INTERVAL_3MINUTE ,
KLINE_INTERVAL_5MINUTE , KLINE_INTERVAL_15MINUTE ,
KLINE_INTERVAL_30MINUTE , KLINE_INTERVAL_1HOUR ,
]

symbolsTicker = ["BTCUSDT","ETHUSDT","LTCUSDT","XRPUSDT","BNBUSDT","ADAUSDT","DOGEUSDT","DOTUSDT","THETAUSDT","EURUSDT"]
symbolTicker = ''
balance = 0
rd = 4
profit = 1.03
stopP = 0.991
stopLP = 0.99

RSI
RSI_ACTIVE = False
RSI_INTERVAL = ''
RSI_OVERSOLD = 0
RSI_PERIOD = 14
rsi_value = 0

while True :
    print("Selecione el indice del Par de Monedas a Operar ")
    print("Indice | Par de Monedas  ")
    for i,v in enumerate(symbolsTicker):
        print(f"[{i}] - {v}")
    input_index = input("Escoja el Par que desea operar\r\nSi desea agregar manualmente presione < a >\n")

    if input_index.isdigit():
        input_index = int(input_index)
        if input_index > len(symbolsTicker)-1 :
            print("Ingrese un indice Valido")
            continue
        else:
            symbolTicker = symbolsTicker[input_index]
            break
    elif input_index == "a":
        text_input = input("Escribe el par de Criptomonedas ejemplo BTCUSDT BNBUSDT, etc\r\n")
        symbolTicker = text_input.upper().strip()
        break


while True :
    rsi_activate_input = input("Estrategia RSI para Compra en Sobreventa \r\n[1] Activar\n\r[0] Desactivar\r\n")

    if rsi_activate_input.isdigit():
        rsi_activate_input =  int(rsi_activate_input)
        if rsi_activate_input == 1 :
            while RSI_OVERSOLD == 0:
                print("Escoja el Tiempo en el cual se aplicara el RSI")
                print("Indice | Temporalidad")
                for i,v in enumerate(list_of_interval):
                    print(f"[{i}] - {v}")
                rsi_interval_input = input("Escoja una temporalidad valor numerico\n")
                if rsi_interval_input.isdigit():
                    rsi_interval_input = int(rsi_interval_input)

                    if not rsi_interval_input > len(list_of_interval) -1:
                        RSI_INTERVAL = list_of_interval[rsi_interval_input]
                        rsi_value_input = input("Ingrese el Valor RSI de Sobreventa valores de 0-100\n")
                        if rsi_value_input.isdigit():
                            rsi_value_input = float(rsi_value_input)
                            if rsi_value_input > 0 and rsi_value_input < 100:
                                RSI_OVERSOLD = rsi_value_input
                                RSI_ACTIVE = True

            break

        elif rsi_activate_input == 0:
            break               
    print("Error Al ingresar Datos Intente Nuevamente")         



amount_to_invest = float(input(f"Cantidad a Invertir en  { symbolTicker.replace('USDT','') } : "))

            
while True :
    profit_input = input("Ingresa el porcentaje de ganacia entre 0 - 100%\r\n")
    stop_input = input("Ingresa el procentaje de perdida de 0-100%\r\n")

    if profit_input.isdigit() and stop_input.isdigit():
        profit_input = float(profit_input)
        stop_input = float(stop_input)
        if profit_input < 100 and stop_input < 100:
            profit = 1 + (profit_input/100)
            stopLP = 1 - (stop_input /100)
            stopP = stopLP + 0.001
            break
    print("Solo valores Numericos de 0-100 No colocar letras")


client = Client(config.API_KEY, config.API_SECRET, tld='com')
symbolPrice = 0
ma50 = 0
auxPrice = 0.0

def orderStatus(orderToCkeck):
    try:
        status = client.get_order(
            symbol = symbolTicker,
            orderId = orderToCkeck.get('orderId')
        )
        return status.get('status')
    except Exception as e:
        print(e)
        return 7


def _rsi_analysis(RSI_OVERSOLD):
    klines = client.get_historical_klines(symbolTicker, RSI_INTERVAL , "15 hour ago UTC")
    closes = [float(i[4]) for i in klines ]
    #np_closes = np.array(closes)  
    #rsi = talib.RSI(np_closes, RSI_PERIOD)
    rsi2 = RSI(closes, periods = RSI_PERIOD)
    rsi = round(float(rsi2[-1]),2)
    return rsi


def _tendencia_ma50_4hs_15minCandles_():
    x = []
    y = []
    sum = 0
    ma50_i = 0

    time.sleep(1)

    resp = False

    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, "18 hour ago UTC")

    if (len(klines) != 72):
        return False
    for i in range(56,72):
        for j in range(i-50,i):
            sum = sum + float(klines[j][4])
        ma50_i = round(sum / 50,2)
        sum = 0
        x.append(i)
        y.append(float(ma50_i))

    modelo = np.polyfit(x, y, 1)

    if (modelo[0]>0):
        resp = True

    return resp

def _ma50_():
    ma50_local = 0
    sum = 0

    klines = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_15MINUTE, "15 hour ago UTC")

    if (len(klines) == 60):

        for i in range(10,60):
            sum = sum + float(klines[i][4])

        ma50_local = sum / 50

    return ma50_local


def clear():
    if os.name == "nt":
        os.system("cls")
    else :
        os.system("clear")

while 1:
    clear()
    try:
        orders = client.get_open_orders(symbol=symbolTicker)
    except Exception as e:
        print(e)
        client = Client(config.API_KEY, config.API_SECRET, tld='com')
        continue

    if (len(orders) != 0):
        print("Tienes Ordenes abiertas en espera ...")
        time.sleep(20)
        continue

    try:
        balance_account = client.get_asset_balance(asset='USDT')
        balance = float(balance_account["free"])
    except Exception as e :
        with open(f"log_{symbolTicker}.txt", "a") as myfile:
            myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")

    sum = 0

    # BEGIN GET PRICE
    try:
        list_of_tickers = client.get_all_tickers()
    except Exception as e:
        with open(f"log_{symbolTicker}.txt", "a") as myfile:
            myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")
        client = Client(config.API_KEY, config.API_SECRET, tld='com')
        continue

    ma50 = _ma50_()
    if (ma50 == 0): continue

    list_of_tickers = list(filter( lambda x:x["symbol"] == symbolTicker ,list_of_tickers) )

    for tick_2 in list_of_tickers:
        if tick_2['symbol'] == symbolTicker:
            symbolPrice = float(tick_2['price'])
            rd = len( str(symbolPrice).split(".")[1])

    if round(amount_to_invest*symbolPrice,rd) > balance:
        print("\nFONDOS INSUFICIENTES PARA OPERAR !\n")
        print(f"Fondos Disponibles $ {round(balance,rd)}")
        print("Cantidad a Invertir $ " + str(round(amount_to_invest*symbolPrice,rd)))
        time.sleep(20)
        continue
           
    # END GET PRICE
   
    print("********** " + symbolTicker + " **********")
    print("Media Aritmetica Actual de 50 velas : "  + str(round(ma50,rd)))
    print("Precio Actual: " + str(round(symbolPrice,rd)))
    print("Precio de Compra: "  + str(round(ma50*0.995,rd)))
    print("Cantidad a Invertir $ " + str(round(amount_to_invest*symbolPrice,rd)))
    print("Disponible en Cuenta $ "  + str(round(balance,2)) )
    print(f"Ganancia {profit}   Precio Stop {stopP}    Precio Stop-Limit  {stopLP}")
    if RSI_ACTIVE:
        rsi_value =_rsi_analysis(RSI_OVERSOLD)
        print(f"RSI Para Compra en Sobreventa {RSI_OVERSOLD} Temporalidad {RSI_INTERVAL} Actual {rsi_value}")
    print("----------------------")


    if _tendencia_ma50_4hs_15minCandles_():
        print("Tendencia Alcista")
    else :
        if RSI_ACTIVE and (rsi_value < RSI_OVERSOLD):
            print(f"Compra en SobreVenta actual rsi {rsi_value}")

        else:    
            print("Tendencia Bajista")
            time.sleep(20)
            continue

    if not ( symbolPrice < ma50*0.995 ):
        print("En espera de precio de Compra ...")
        time.sleep(10)
        continue
    else:
        print("Iniciando Compra Dinamica")
        try:

            buyOrder = client.create_order(
                        symbol=symbolTicker,
                        side='BUY',
                        type='STOP_LOSS_LIMIT',
                        quantity=amount_to_invest,
                        price=round(symbolPrice*1.0055,rd),
                        stopPrice=round(symbolPrice*1.005,rd),
                        timeInForce='GTC')

            auxPrice = symbolPrice
            time.sleep(5)
            while orderStatus(buyOrder)=='NEW':

                # BEGIN GET PRICE
                try:
                    list_of_tickers = client.get_all_tickers()
                except Exception as e:
                    with open(f"log_{symbolTicker}.txt", "a") as myfile:
                        myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 2 ! \n")
                    client = Client(config.API_KEY, config.API_SECRET, tld='com')
                    continue
                list_of_tickers = list(filter(lambda x:x["symbol"]==symbolTicker  , list_of_tickers))

                for tick_2 in list_of_tickers:
                    if tick_2['symbol'] == symbolTicker:
                        symbolPrice = float(tick_2['price'])
                # END GET PRICE

                if (symbolPrice < auxPrice):

                    try:
                        result = client.cancel_order(
                            symbol=symbolTicker,
                            orderId=buyOrder.get('orderId'))

                        time.sleep(10)
                    except Exception as e:
                        with open(f"log_{symbolTicker}.txt", "a") as myfile:
                            myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ "Error Canceling Oops 4 ! \n")
                        break

                    buyOrder = client.create_order(
                                symbol=symbolTicker,
                                side='BUY',
                                type='STOP_LOSS_LIMIT',
                                quantity=amount_to_invest,
                                price=round(symbolPrice*1.0055,rd),
                                stopPrice=round(symbolPrice*1.005,rd),
                                timeInForce='GTC')
                    auxPrice = symbolPrice
                    time.sleep(5)

            time.sleep(5)

            orderOCO = client.order_oco_sell(
                        symbol = symbolTicker,
                        quantity=amount_to_invest,
                        price = round(float(symbolPrice) * profit ,rd),
                        stopPrice = round(float(symbolPrice)* stopP ,rd),
                        stopLimitPrice = round(float(symbolPrice) * stopLP,rd),
                        stopLimitTimeInForce = 'GTC'
                    )

            time.sleep(20)

        except Exception as e:
            with open(f"log_{symbolTicker}.txt", "a") as myfile:
                myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 3 ! \n")
            client = Client(config.API_KEY, config.API_SECRET, tld='com')
            print(format(e))
            orders = client.get_open_orders(symbol=symbolTicker)
            if (len(orders)>0):
                result = client.cancel_order(
                    symbol=symbolTicker,
                    orderId=orders[0].get('orderId'))
            continue

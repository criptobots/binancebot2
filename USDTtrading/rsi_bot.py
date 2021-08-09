import websocket, json, pprint, numpy
import config
from binance.client import Client
from binance.enums import *
import os, datetime,pytz
from functions import *



symbolsTicker = ["BTCUSDT","ETHUSDT","LTCUSDT","XRPUSDT","BNBUSDT","ADAUSDT","DOGEUSDT","DOTUSDT","THETAUSDT","EURUSDT"]
TRADE_SYMBOL = ''

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
            TRADE_SYMBOL = symbolsTicker[input_index]
            break
    elif input_index == "a":
        text_input = input("Escribe el par de Criptomonedas ejemplo BTCUSDT BNBUSDT, etc\r\n")
        TRADE_SYMBOL = text_input.upper().strip()
        break

TRADE_QUANTITY = float(input(f"Cantidad a Invertir en  { TRADE_SYMBOL.replace('USDT','') } : "))


RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
price_buy = 0

closes = []
in_position = False

SOCKET = f"wss://stream.binance.com:9443/ws/{TRADE_SYMBOL.lower()}@kline_1m"


client = Client(config.API_KEY, config.API_SECRET, tld='com')

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def clear():
    if os.name == "nt":
        os.system("cls")
    else :
        os.system("clear")

    
def on_open(ws):
    print('Conexion abierta')

def on_close(ws):
    print('Conexion cerrada')

def on_message(ws, message):
    global closes, in_position
    
    #print('received message')
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        clear()
        print(f"Moneda : {TRADE_SYMBOL}")
        print(f"Total invertido : { TRADE_QUANTITY }")
        print("Vela cerrada en {}".format(close))
        closes.append(float(close))
        print("Velas Cerradas")
        print(closes)
        
        if len(closes) > RSI_PERIOD:
            rsi = RSI(closes,periods =  RSI_PERIOD)
            print("Todos los rsi calculados")
            print(rsi)
            last_rsi = round(rsi[-1],2)
            print("Rsi Actual {}".format(last_rsi))
            if len(closes) > 30:
                closes.pop(0)

            if last_rsi > RSI_OVERBOUGHT:
                if in_position and close > price_buy:
                    print("Sobrecomprado! Vender! Vender! Vender!")
                    # put binance sell logic here
                    try:
                        order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    except Exception as e:
                        with open(f"log_rsi_{TRADE_SYMBOL}.txt", "a") as myfile:
                            myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")

                    if order_succeeded:
                        in_position = False
                else:
                    print("Esta sobrecomprado pero no tenemos nada que hacer !.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("Esta Sobrevendido pero tienes una posicion abierta")

                else:
                    print("Sobrevendido! Comprar! Comprar! Comprar!")
                    # put binance buy order logic here
                    try:
                        order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    except Exception as e:
                        with open(f"log_rsi_{TRADE_SYMBOL}.txt", "a") as myfile:
                            myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")
                    
                    if order_succeeded:
                        price_buy = close
                        in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()




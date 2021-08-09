import websocket, json, pprint, numpy
import config
from binance.client import Client
from binance.enums import *
import os, datetime,pytz
from functions import *
import time


client = Client(config.API_KEY, config.API_SECRET, tld='com')

symbolsTicker = ["BTCUSDT","ETHUSDT","LTCUSDT","XRPUSDT","BNBUSDT","ADAUSDT","DOGEUSDT","DOTUSDT","THETAUSDT","EURUSDT"]
symbolTicker = ''
balance = 0
profit = 1.03
stopP = 0.991
stopLP = 0.99
rd = 4

symbolPrice = 0.0
price_to_buy = 0.0
auxPrice = 0.0
dynamic_buy = False
elapsed = 0.0
buyOrder = None


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



price_to_buy = float(input("Ingresa el Precio para Compra Dinamica Decimales\r\n"))


SOCKET = f"wss://stream.binance.com:9443/ws/{symbolTicker.lower()}@kline_1m"



def orderStatus(orderToCkeck):
	global client
	try:
		status = client.get_order(
			symbol = symbolTicker,
			orderId = orderToCkeck.get('orderId')
		)
		return status.get('status')
	except Exception as e:
		print(e)
		return 7

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
	global client
	global symbolTicker,balance,profit,stopP,stopLP,rd,symbolPrice,price_to_buy,auxPrice,dynamic_buy,elapsed,buyOrder 
	global orderStatus
	#clear()
	
	try:
		orders = client.get_open_orders(symbol=symbolTicker)
	except Exception as e:
		print(e)
		client = Client(config.API_KEY, config.API_SECRET, tld='com')
		return 
	if (len(orders) != 0):
		if (orderStatus(buyOrder) != "NEW"):
			print("Tienes Ordenes abiertas en espera ...")
			dynamic_buy = False
			time.sleep(60)
			return 
	try:
		balance_account = client.get_asset_balance(asset='USDT')
		balance = float(balance_account["free"])
	except Exception as e :
		with open(f"log_{symbolTicker}.txt", "a") as myfile:
			myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")

	json_message = json.loads(message)
	candle = json_message['k']
	symbolPrice = float(candle['c'])
	rd = len( str(symbolPrice).split(".")[1])

	if round(amount_to_invest*symbolPrice,rd) > balance and dynamic_buy == False:
		print("\nFONDOS INSUFICIENTES PARA OPERAR !\n")
		print(f"Fondos Disponibles $ {round(balance,rd)}")
		print("Cantidad a Invertir $ " + str(round(amount_to_invest*symbolPrice,rd)))
		time.sleep(60)
		return 
	

	if (time.time() - elapsed > 3):
		clear()
		elapsed= time.time()

		print("********** " + symbolTicker + " **********")
		print("Precio Actual: " + str(round(symbolPrice,rd)))
		print("Precio de Compra: " + str(round(price_to_buy*0.995,rd)))
		print("Cantidad a Invertir $ " + str(round(amount_to_invest*symbolPrice,rd)))
		print("Disponible en Cuenta $ "  + str(round(balance,2)) )
		print(f"Ganancia {profit}   Precio Stop {stopP}    Precio Stop-Limit  {stopLP}")

	if not ( symbolPrice < price_to_buy*0.995 ):
		print("Esperando precio de Compra !")
		if not dynamic_buy:
			return
	elif not dynamic_buy : 
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
			dynamic_buy = True
			time.sleep(5)
 
		except Exception as e :
			with open(f"log_{symbolTicker}.txt", "a") as myfile:
				myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")
			return 	
	try:
		if dynamic_buy:
			print("Compra Dinamica en Ejecucion ")
			if orderStatus(buyOrder)=='NEW':
				print("Dentro de Order status")
				print(auxPrice)
				if (symbolPrice < auxPrice):
					print("Precio menor ")
					try:
						result = client.cancel_order(
						symbol=symbolTicker,
						orderId=buyOrder.get('orderId'))
						print("Cancelando Orden De Compra !")
						time.sleep(5)
					except Exception as e:
						with open(f"log_{symbolTicker}.txt", "a") as myfile:
							myfile.write(str(datetime.datetime.now(pytz.timezone("America/Caracas"))) +" - an exception occured - {}".format(e)+ "Error Canceling Oops 4 ! \n")
						return 


					buyOrder = client.create_order(
						symbol=symbolTicker,
						side='BUY',
						type='STOP_LOSS_LIMIT',
						quantity=amount_to_invest,
						price=round(symbolPrice*1.0055,rd),
						stopPrice=round(symbolPrice*1.005,rd),
						timeInForce='GTC')
					auxPrice = symbolPrice
					print("Creando Orden De compra Mejor Precio !")
					time.sleep(5)
					return 
				return 	

			
			print("Creando Ordenes De venta !")
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
            return 


				
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
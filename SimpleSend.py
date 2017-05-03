from network import LoRa
import socket
import time
import binascii
import pycom

lora = LoRa(mode=LoRa.LORAWAN)
app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

s.send('Hello LoRa')

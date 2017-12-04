from network import LoRa
import pycom
#
lora = LoRa(mode=LoRa.LORAWAN)

print('devEUI: ', '-'.join("{:02x}".format(b) for b in lora.mac()))

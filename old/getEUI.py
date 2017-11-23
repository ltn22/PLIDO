from network import LoRa
import pycom
#
lora = LoRa(mode=LoRa.LORAWAN)
mac = lora.mac()
#
print ('devEUI: ',  end='')
#
for i in range (0,  8):
        print(hex(mac[i]), end='-')
#
print ()

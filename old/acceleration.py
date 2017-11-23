from network import LoRa
import socket
import time
import binascii
import pycom
import ustruct

from machine import I2C
from machine import Pin


def pin_handler(arg):
    print("Hola")

i2c = I2C(0, I2C.MASTER, baudrate=100000)
print('In I2C bus:',  i2c.scan())

XYZ_DATA_CFG = 0x0E
FF_MT_CFG = 0x15
FF_MT_THS = 0x17
FF_MT_COUNT = 0x18
CTRL_REG1 = 0x2A
CTRL_REG2 = 0x2B
CTRL_REG3 = 0x2C
CTRL_REG4 = 0x2D
CTRL_REG5 = 0x2E

# i2c.writeto_mem(0x1c, 0x2A, b'\x00')
# i2c.writeto_mem(0x1c, 0x2A, b'\x01')
# i2c.writeto_mem(0x1c, 0x0E, b'\x00')

c = i2c.readfrom_mem(0x1c, CTRL_REG1, 1) # set standby mode for configuration
v = c[0] & ~(0x01)
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, CTRL_REG1, data) #active

v = 2 >> 2
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, XYZ_DATA_CFG, data) # fsr

c = i2c.readfrom_mem(0x1c, CTRL_REG2, 1) # set standby mode for configuration
v = c[0] & ~(0xF8)
v = v | 0x1C
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, CTRL_REG2, data) #SMODS MODS SLPE

v = 0x00
v = v | 0x0A
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, CTRL_REG3, data) #WAKE_FF_MT IPOL

v = 0x00
v = v | 0x85
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, CTRL_REG4, data) #WAKE_FF_MT IPOL

v = 0x00
v = v | 0x84
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, CTRL_REG5, data) #INT_CFG_ASLP INT_CFG_FF_MT

c = i2c.readfrom_mem(0x1c, CTRL_REG5, 1) # set standby mode for configuration
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, CTRL_REG5, data) #active

v = 0xF8
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, FF_MT_CFG, data) #INT_CFG_ASLP INT_CFG_FF_MT

v = 0x01
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, FF_MT_THS, data) #INT_CFG_ASLP INT_CFG_FF_MT

v = 0x01
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, FF_MT_COUNT, data) #INT_CFG_ASLP INT_CFG_FF_MT



c = i2c.readfrom_mem(0x1c, 0x2A, 1) # set standby mode for configuration
v = c[0]  | (0x01)
print (v)
data = ustruct.pack('!B', v)
i2c.writeto_mem(0x1c, 0x2A, data) #active


time.sleep(0.5)

p_in = Pin('P8', mode=Pin.IN, pull=Pin.PULL_UP)

p_in.callback(Pin.IRQ_FALLING |Pin.IRQ_HIGH_LEVEL, pin_handler)
#p_in.callback(Pin.IRQ_RISING, pin_handler)


for i in range(0,  10000):
    val = i2c.readfrom_mem(0x1C,  0,  7)
    xa = (val[1] << 8 | val[2])/16
    ya = (val[3] << 8 | val[4])/16
    za = (val[5] << 8 | val[6])/16

    if xa > 2047 : xa -= 4096
    if ya > 2047 : ya -= 4096
    if za > 2047 : za -= 3064

    print (xa,' ', ya, ' ', za)

    time.sleep(0.5);

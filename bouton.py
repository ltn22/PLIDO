from machine import Pin

val = True

def pin_handler(arg):
    global val

    print("pin {0:s} value is {1:d}".format(arg.id(), p_out.value()))
    p_out(val)

    val = not val


p_out = Pin('P12', mode=Pin.OUT)

p_in = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)

#p_in.callback(Pin.IRQ_FALLING |Pin.IRQ_RISING, pin_handler)
p_in.callback(Pin.IRQ_RISING, pin_handler)

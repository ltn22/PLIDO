from network import LoRa
import binascii
import pycom
import time
import socket
import math
import BitBuffer

rule_frag = {
    "ruleid": 0xC0,
    "fragmentation": {
        "ruleidLength": 2,
        "dtagLength": 1,
        "windowBit" : True,
        "FCNLength": 3
        }
}

class FragmentList:

    def __init__ (self,  message):
        self.idx       = 0
        self.msg       = message

    def getFrag(self, posNumber, FCNlength, MTU, start=-1):
        """ return the next FCNnumber and the corresponding Fragment
        regarding the position and the MTU.
        start can be used to avoid to start at the first FCN number
        i.e; 2**FCNlength - 2
        """
        if (start == -1): start = 2**FCNlength - 2
        if (start > 2**FCNlength):
            raise ValueError ('number too big')

        if (len(self.msg) < MTU*(2**FCNlength-1)): #not enough data to send
            start = math.ceil(len(self.msg)/MTU)
            print("aligned on", start)

        if ((posNumber < 0) or (posNumber > ((2**FCNlength)-1))):
            print (FCNlength)
            raise ValueError ("FCN number error: out of limits")

        end = (posNumber+1)*MTU

        if (end >= len(self.msg)):
            FCN = 2**FCNlength - 1
            end = len(self.msg)
        else:
            FCN =  start - posNumber

        return FCN, self.msg[posNumber*MTU:end]

    def ackFragWindow(self, fragNumber, MTU):
        self.msg = self.msg[fragNumber*MTU:]

    def getMsgLength(self):
        return len(self.msg)

class Frag:

    def __init__(self, socket, MTU, rule, dtag=0):

        if (not "fragmentation" in rule):
            raise ValueError('not a fragmentation rule')

        self.socket = socket
        self.MTU    = MTU

        self.FCNlength =   rule["fragmentation"]["FCNLength"]  #size in bit
        self.TAGlength =   rule["fragmentation"]["FCNLength"]  #size in bit
        self.ruleid    =   int(rule["ruleid"])
        self.ruleidlength = rule["fragmentation"]["ruleidLength"]  #size in bit
        self.dtag      = dtag
        self.dtaglength = rule["fragmentation"]["dtagLength"]  #size in bit

        self.window    = 0

        self.messagesList = []

    def send (self, msg):
        print ("send", msg)

        dataSize = self.MTU
        self.messagesList.append(FragmentList(msg))

        print (self.messagesList)

    def haveToSend (self, bitmap):
        print ("check if everything is received", bitmap)
        for i in range (0, 2**self.FCNlength-2):
            if ((bitmap & (1 << i)) == 0): return True
        return False

    def sleep (self, duration=60):
        if (len(self.messagesList) > 0):
            while (self.messagesList[0].getMsgLength() > 0):

                fragBitmap = 0x00; # frag bitmap is set to 0, all frag must be sent
                while (self.haveToSend(fragBitmap)):
                    maxFrag = 2**self.FCNlength-1 # /!\ must be shorter for the last window
                    print("max frag =", maxFrag)

                    for i in range(0, maxFrag):  # since maxFag is not included in range no need to -1

                        eBuf = BitBuffer.BitBuffer()
                        FCN, frag = self.messagesList[0].getFrag(i, self.FCNlength, self.MTU)
                        print(self.messagesList[0].getFrag(i, self.FCNlength, self.MTU))

                        print ("FCN = ", FCN)

                        for j in range (0, self.ruleidlength):
                            bit = (1 << (7 -j)) & int(self.ruleid)
                            eBuf.add_bit(bit)

                        for j in range (0, self.dtaglength):
                            bit = (1 << (7 -j)) & int(self.dtag)
                            eBuf.add_bit(bit)

                        eBuf.add_bit(self.window)

                        for j in range (self.FCNlength-1, -1, -1):
                            bit = (1 << j) & int(FCN)
                            eBuf.add_bit(bit)

                        if (fragBitmap & (1 << int(FCN)) == 0x00): # fragment is not sent nor ack
                            pycom.rgbled(0xff1493)
                            self.socket.send(eBuf.buffer())
                            pycom.rgbled(0x00)
                            if (FCN != 0): time.sleep(5)
                        else:
                            print ('fragment ', FCN,' already sent')
                            # /!\ empty FCN0

                    self.socket.setblocking( True )
                    self.socket.settimeout( 10 )

                    while True:
                        try:
                            data = self.socket.recv( 64 )
                            dataRcv = True
                            pycom.rgbled( 0x00FF00 )  # LED green ACK received
                            break
                        except:
                            print ( 'timeout in receive' )
                            dataRcv = False
                            pycom.rgbled( 0x000000 )

                            print ("send empty header")
                            eBuf = BitBuffer.BitBuffer() # only header no data

                            for j in range (0, self.ruleidlength):
                                bit = (1 << (7 -j)) & int(self.ruleid)
                                eBuf.add_bit(bit)

                            for j in range (0, self.dtaglength):
                                bit = (1 << (7 -j)) & int(self.dtag)
                                eBuf.add_bit(bit)

                            eBuf.add_bit(self.window)

                            for j in range (self.FCNlength-1, -1, -1): #FCN = 0
                                bit = 0
                                eBuf.add_bit(bit)
                                self.socket.send(eBuf.buffer())

                    if (dataRcv)   :
                        fragBitmap = 0x00
                        print("raw data = ", data)
                        for k in data:
                            print (k)
                            fragBitmap <<= 8
                            fragBitmap += k
                            print (fragBitmap)
                    else:
                        print("not received")

                    # /!\ window is not included in answer
                    # /!\ may have to send an emptu FRA0 to trigger receivers ACK
                    #repeat this loop until the receiver sends a bitmap = 0;

            print(createError)

                #remove the window message from transmission.
            self.messagesList[0].ackFragWindow(2**self.FCNlength-1, self.MTU)

        else:
            print ("empty queue")

def main():
    print ("Main Execution")

    app_eui = binascii.unhexlify('00 00 00 00 00 00 00 00'.replace(' ',''))
    app_key = binascii.unhexlify('11 22 33 44 55 66 77 88 11 22 33 44 55 66 77 88'.replace(' ',''))

    pycom.heartbeat(False)

    lora = LoRa(mode=LoRa.LORAWAN)

    for i in range (0,  255):
        led = i<< 16| i <<8  | i
        pycom.rgbled(led)
        time.sleep(0.01)


    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key),  timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

    pycom.rgbled(0)

    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.bind(0x02);

    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    s.setsockopt(socket.SOL_LORA,  socket.SO_CONFIRMED,  False)

    print("apres setsock")
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)

    f = Frag(s, MTU=50, rule=rule_frag)#,

    f.send ("""To be, or not to be: that is the question:
Whether ’tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles,
And by opposing end them? To die: to sleep;
No more; and by a sleep to say we end
The heart-ache and the thousand natural shocks
That flesh is heir to, ’tis a consummation
Devoutly to be wish’d. To die, to sleep;
To sleep: perchance to dream: ay, there’s the rub;
For in that sleep of death what dreams may come
When we have shuffled off this mortal coil,
Must give us pause: there’s the respect
That makes calamity of so long life;
For who would bear the whips and scorns of time,
The oppressor’s wrong, the proud man’s contumely,
The pangs of despised love, the law’s delay,
The insolence of office and the spurns
That patient merit of the unworthy takes,
When he himself might his quietus make
With a bare bodkin? who would fardels bear,
To grunt and sweat under a weary life,
But that the dread of something after death,
The undiscover’d country from whose bourn
No traveller returns, puzzles the will
And makes us rather bear those ills we have
Than fly to others that we know not of?
Thus conscience does make cowards of us all;
And thus the native hue of resolution
Is sicklied o’er with the pale cast of thought,
And enterprises of great pith and moment
With this regard their currents turn awry,
And lose the name of action.–Soft you now!
The fair Ophelia! Nymph, in thy orisons
Be all my sins remember’d.""")
    f.sleep()

if __name__ == "__main__":
    # execute only if run as a script
    main()

# Class CBOR

CBOR_POSITIVE = 0x00
CBOR_NEGATIVE = 0x20
CBOR_STRING = 0x40
CBOR_BITMAP = 0x60
CBOR_ARRAY= 0x80
CBOR_PAIR = 0xA0
CBOR_TAG = 0xC0
CBOR_FLOAT = 0xE0

class CBOR:
    
    def __init__(self,  value):
        self.buffer = []
          
        if type(value) is int:
            if (value >= 0):
                self.buffer.append(CBOR_POSITIVE)
            else:
                self.buffer.append(CBOR_NEGATIVE)
                value = -1 * value
                value = value  - 1
            
            if (value < 24):
                self.buffer[0] |= value
                return
            else:
                # find the size in bit (first bit to the left != 0)
                for i in range (31,  0,  -1):
                    if ((0x01 << i) & value):
                        break
                                
                if (i < 7):
                    self.buffer[0] |= 24
                    nb_byte = 1
                elif (i < 15):
                    self.buffer[0] |= 25
                    nb_byte = 2
                elif (i < 31):
                    self.buffer[0] |= 26
                    nb_byte = 4
                elif (i <63):
                    self.buffer[0] |=27
                    nb_byte = 8
                else:
                    print('Too big number')
                    return
                
                for k in range (nb_byte,  0,  -1):
                    msk = 0xFF << 8*(k-1)
                    result = (value & msk) >> 8*(k-1)
                    self.buffer.append(result)
            
            return #end of Int
        
        if type(value) is str:
            l = len (value)
            self.buffer.append(CBOR_STRING | l)
            
            for c in value:
                self.buffer.append(ord(c))
            
            return  #end of string
            
        if type(value) is list:
                l = len(value)
                if (l < 23):
                    self.buffer.append(CBOR_ARRAY | l)
                else:
                    print('Too much elements')
                    return
                for elm in value:
                   self.buffer += elm.buffer
                   
                return # end of list
                
    def dump(self):
        for h in self.buffer:  
                print ("%3.2x"% h,  end='')
        print('')

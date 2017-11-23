'''
SCHC compressor, Copyright (c) <2017><IMT Atlantique and Philippe Clavier>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
'''
#
# CLASS CBOR
#

import struct

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
        self.buffer = b''

        if type(value) is int:
            if (value >= 0):
                firstByte = CBOR_POSITIVE
            else:
                firstByte = CBOR_NEGATIVE
                value = -1 * value
                value = value  - 1

            if (value < 24):
                self.buffer = struct.pack('!B', firstByte | value)
                return
            else:
                # find the size in bit (first bit to the left != 0)
                for i in range (31,  0,  -1):
                    if ((0x01 << i) & value):
                        break

                if (i < 7):
                    l = 24
                    nb_byte = 1
                elif (i < 15):
                    l = 25
                    nb_byte = 2
                elif (i < 31):
                    l = 26
                    nb_byte = 4
                elif (i <63):
                    l = 27
                    nb_byte = 8
                else:
                    print('Too big number')
                    return

                self.buffer = struct.pack('!B', firstByte | l)


                for k in range (nb_byte,  0,  -1):
                    msk = 0xFF << 8*(k-1)
                    result = (value & msk) >> 8*(k-1)
                    self.buffer += struct.pack('!B', result)

            return #end of Int

        if type(value) is str:
            l = len (value)
            self.buffer = struct.pack('!B', (CBOR_STRING | l))
            self.buffer += value


            return  #end of string

        if type(value) is list:
                l = len(value)
                if (l < 23):
                    self.buffer = struct.pack('!B', (CBOR_ARRAY | l))
                else:
                    print('Too much elements')
                    return
                for elm in value:
                   self.buffer += elm.buffer

                return # end of list

    def addList(self, elm):

        nbElm = 0;

        if (self.buffer[0] & 0xE0 == CBOR_ARRAY):
            currentLength = self.buffer[0] & 0x1F
            if (currentLength < 24): #length on 1 Byte
                nbElm = currentLength
                self.buffer = self.buffer[1:]
            elif (currentLength == 24): # length on 2 bytes
                nbElm = self.buffer[1]
                self.buffer = self.buffer[2:]
            elif currentLength == 25:
                nbElm = self.buffer[1]<< 8 + self.buffer[2]
                self.buffer = self.buffer[3:]
            elif currentLength == 26:
                nbElm = self.buffer[1]<<24 + self.buffer[2]<<16 + self.buffer[3]<< 8 + self.buffer[4]
                self.buffer = self.buffer[5:]
            elif currentLength == 27:
                nbElm = self.buffer[1]<<56 + self.buffer[2]<<48 + self.buffer[3]<< 40 + self.buffer[4]<<32 + \
                    self.buffer[5]<<24 + self.buffer[6]<<16 + self.buffer[7]<< 8 + self.buffer[8]
                self.buffer = self.buffer[9:]
            else:
                raise Exception ("Length not allowed")

            nbElm += 1

            if (nbElm < 24):
                self.buffer = struct.pack('!B', CBOR_ARRAY | nbElm) + self.buffer
            elif nbElm < 0xFF:
                self.buffer = struct.pack('!BB', CBOR_ARRAY | 24, nbElm) + self.buffer
            elif nbElm < 0xFFFF:
                self.buffer = struct.pack('!BH', CBOR_ARRAY | 25, nbElm) + self.buffer
            elif nbElm < 0xFFFFFFFF:
                self.buffer = struct.pack('!BL', CBOR_ARRAY | 26, nbElm) + self.buffer
            elif nbElm < 0xFFFFFFFFFFFFFFFF:
                self.buffer = struct.pack('!BQ', CBOR_ARRAY | 27, nbElm) + self.buffer

            #self.buffer[0] =

            self.buffer += elm.buffer

        else:
            print ("KO")


    def length (self):
        return len(self.buffer)

    def dump(self):
        for h in self.buffer:
                print ("%3.2x"% h,  end='')
        print('')


#
#  END OF CLASS CBOR
#

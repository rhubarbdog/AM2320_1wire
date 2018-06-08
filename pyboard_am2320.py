#
# This code is based  on
"""
https://github.com/rhubarbdog/AM2320_1wire raspberry_am2320.py
"""
#
# modifications by phil hall
"""
This implements an AM2320 over the 1 wire protocol
"""


import time
from pyb import Pin

class DataError(Exception):
    pass

class AM2320_1WIRE:

    def __init__(self,pin=None):
        self.__p_name=pin
        self.__p_object=None

    def readSensor(self):

        self.__p_object=Pin(self.__p_name, Pin.OUT_PP)
        # send initial high
        self._send_and_sleep(True,50,"ms")

        #Tbe
        self._send_and_sleep(False,5,"ms")

        #Tgo
        self._send_and_sleep(True,30,"us")
        
        # change to input using pull up
        self.__p_object=Pin(self.__p_name,Pin.IN,Pin.PULL_UP)

        #Trel and Treh are in the data
        # collect data into an array
        data=self._collect_input()

        # parse lengths of all data pull up periods
        pull_up_lengths=self._parse_data_pull_up_lengths(data)

        # if bit count mismatch,return error (4 byte data + 1 byte checksum)
        if len(pull_up_lengths)!=40:
            raise DataError("Too many or too few bits. "+ \
                            str(len(pull_up_lengths)))

        # calculate bits from lengths of the pull up periods
        bits=self._calculate_bits(pull_up_lengths)

        # we have the bits,calculate bytes
        the_bytes=self._bits_to_bytes(bits)

        # calculate checksum and check
        checksum=self._calculate_checksum(the_bytes)
        if the_bytes[4]!=checksum:
            raise DataError("Checksum invalid.")
        
        temp=((the_bytes[2] & 0x7f ) << 8 ) + the_bytes[3]
        if the_bytes[2] & 0x80:
            temp*=-1
        temp/=10
        humid=(the_bytes[0] << 8 ) + the_bytes[1]
        humid/=10
        return (temp,humid)
    
    def _send_and_sleep(self,output_is_high,sleep,units=None):
        if output_is_high:
            self.__p_object.high()
        else:
            self.__p_object.low()
            
        if units is not None:
            units=units.lower()
            
        if units == "ms":
            time.sleep_ms(sleep)
        elif units == "us":
            time.sleep_us(sleep)
        else:
            time.sleep(sleep)

    def _collect_input(self):
        # this is used to determine where is the end of the data
        MAX_CHANGE=100

        unchanged=0
        last=None
        data=[]
        
        while True:
            if self.__p_object.value():
                current=1
            else:
                current=0
                
            data.append(current)

            if last is None or last != current:
                unchanged=0
                last=current
            else:
                unchanged+=1
                if unchanged>MAX_CHANGE:
                    break

        return data

    def _parse_data_pull_up_lengths(self,data):

        PULL_UP=1
        PULL_DOWN=2
        first_time=True

        looking_for=PULL_DOWN
        
        lengths=[] # will contain the lengths of data pull up periods
        current_length=0 # will contain the length of the previous period

        for i in range(len(data)):

            current=data[i]
            current_length+=1

            if looking_for==PULL_UP:
                if current==1:

                    current_length=0
                    looking_for=PULL_DOWN

            elif looking_for==PULL_DOWN:
                if current==0:

                    if first_time:
                        first_time=False
                    else:
                        lengths.append(current_length)
                    
                    looking_for=PULL_UP

        return lengths

    def _calculate_bits(self,pull_up_lengths):

        shortest=None
        longest=None

        for i in range(len(pull_up_lengths)):
            length=pull_up_lengths[i]

            if shortest is None or length < shortest:
                shortest=length

            if longest is None or length > longest:
                longest=length

        # use the halfway to determine whether the period it is long or short
        halfway=shortest+(longest-shortest)/2
        bits=[]

        for i in range(len(pull_up_lengths)):
            bit=pull_up_lengths[i] > halfway
            bits.append(bit)

        return bits

    def _bits_to_bytes(self,bits):
        the_bytes=[]
        byte=0x00

        for i in range(len(bits)):
            byte=byte << 1
            if bits[i]:
                byte=byte | 1

            if ((i + 1) % 8)==0:
                the_bytes.append(byte)
                byte=0x00

        return the_bytes

    def _calculate_checksum(self,the_bytes):
        return (the_bytes[0] + the_bytes[1] + \
                the_bytes[2] + the_bytes[3]) & 0xff

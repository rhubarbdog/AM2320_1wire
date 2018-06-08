import pyb
import pyboard_am2320 as AOSONG

DELAY=2000


def main():

    am2320=AOSONG.AM2320_1WIRE('X12')
    
    while True:

        message="Fatal Error."
        try:
            t,h=am2320.readSensor()
            message=("Temp  :%2.1fC\nHumid :%2.1f%%" % (t,h))
        except AOSONG.DataError as e:
            message="Error:"+str(e)
            
        print(message)
        pyb.delay(DELAY)

        
if __name__=="__main__":
    main()

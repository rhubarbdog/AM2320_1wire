import RPi.GPIO as GPIO
import AOSONG
import time

DEGREE_SIGN=u"\N{DEGREE SIGN}"

# initialize GPIO
GPIO.setmode(GPIO.BCM)

# read data using pin 17
sensor = AOSONG.AM2320_1WIRE(pin=17)
failure=0
max_fail=0
try:
    while True:
        try:
            (t,h) = sensor.read()
            failure=0
        except AOSONG.DataError as e:
            #print("\n"+str(e))
            failure+=1
            if failure>max_fail:
                max_fail=failure
                
            t="--%02d-" % failure
            h="-%02d-" % max_fail
            
        print("  "+str(t)+DEGREE_SIGN+"C "+str(h)+"%  ",end="\r")

        time.sleep(2)
except KeyboardInterrupt:
    pass

print("")
GPIO.cleanup()

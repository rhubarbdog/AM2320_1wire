# AM2320_1wire
python and microptython module to deal with an am2320 temperature and humidity sensor using a one wire protocol.

The am2320 has 4 wires to operate as an i2c device if you wire as follows the sensor will work over a 1 wire protocol.
Pin 1 - Vcc (3.3v).
Pin 2 - Data , this should have a 5.1k pull up resistor connecting it to Vcc. 
Pin 3 - Ground. 
Pin 4 - Ground. 

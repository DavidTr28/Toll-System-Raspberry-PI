from picozero import Speaker
import time
from machine import I2C, Pin, SPI
from mfrc522 import MFRC522
from servo import Servo # Importing some of the libraries needed


s1 = Servo(0)       # Servo pin is connected to GP0
 
def servo_Map(x, in_min, in_max, out_min, out_max):       # Function to map a value from one range to another
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
 
def servo_Angle(angle):    # Function to set the angle of the servo motor
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180
    s1.goto(round(servo_Map(angle,0,180,0,1024))) # Convert range value to angle value


led = Pin(25, Pin.OUT)
true = Pin(15, Pin.OUT)
false = Pin(14, Pin.OUT)
sck = Pin(6, Pin.OUT)                  # Setting up GPIO Pins
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
sda = Pin(5, Pin.OUT)
rst = Pin(22, Pin.OUT)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
speaker = Speaker(18)

vehicle1 = "0xede90132" #Authorized tag
vehicle1credit = 9
servo_Angle(20) # Setting the initial angle of the servo motor

while True:   # Main loop
    led.value(1)
    time.sleep(0.001)
    led.value(0)
    false.value(1)
    
    rdr = MFRC522(spi, sda, rst)                 # Setting up RFID reader
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    
    if stat == rdr.OK:                           # Checking for RFID tag
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            uid = ("0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
            
            
            if (uid == vehicle1) and (vehicle1credit >= 3):  # Checking if the RFID tag is authorized 
                vehicle1credit-=3
                print('Passing this toll costs you 3$. \n\nYou have ', int(vehicle1credit), '$ left on your card\n\n')
                false.value(0)
                servo_Angle(130)
                true.value(1)
                speaker.on()
                time.sleep(4)
                true.value(0)
                speaker.off()
                servo_Angle(20)
                time.sleep(0)
            else:                          # Unauthorized tag alert
                if (vehicle1credit < 3): 
                    print('You do not have enought balance to pass this toll!')   
                for i in range(4):   
                    false.value(1)
                    speaker.on()
                    time.sleep(0.2)
                    false.value(0)
                    speaker.off()
                    time.sleep(0.2)
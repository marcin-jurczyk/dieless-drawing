import serial
import time

with serial.Serial("/dev/ttyACM0", 9600, timeout=1) as arduino:
    time.sleep(0.1) # wait for serial to open
    if arduino.isOpen():
        print("{} connected".format(arduino.port))
        try:
            while True:
                cmd = input("Enter command : ")
                arduino.write(cmd.encode())
                while arduino.inWaiting() == 0: pass
        except KeyboardInterrupt:
            print("Keyboard interrupt has been caught.")
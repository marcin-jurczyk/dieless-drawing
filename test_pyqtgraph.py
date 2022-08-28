import serial, time

serial_ports = ("/dev/ttyACM0", "/dev/ttyACM1")

for port in serial_ports: 
    try:
        arduino = serial.Serial(port, 9600, timeout=1) 
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print("{} connected! Press CTRL-C to exit. ".format(arduino.port))
            try:
                while True:
                    cmd=input("Enter command : ")
                    arduino.write(bytes("{}".format(cmd), "utf-8"))
                    time.sleep(0.01) # wait for arduino to answer
                    while arduino.inWaiting() == 0: pass
                    if arduino.inWaiting() > 0: 
                        answer=arduino.readline()
                        print(answer.decode("utf-8").replace('\n', ''))
                        arduino.flushInput() #remove data after reading
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")
    except: pass
print("Check your connection!")
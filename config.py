# raspberry ports
usb_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1']
serial_ports = ["/dev/ttyACM0", "/dev/ttyACM1"]

save_file_location = '/data'

# Force sensor (WDT11-U)
force_sensor_config = {
    "address": 1,
    "baudrate": 38400,
    "stopbits": 1,
    "bytesize": 8
}

rotation_stepper_motors_config = {
    "max_speed": 1000,
    "min_speed": 7000,
    "initial_speed": 3500
}

pre_heating_config = {
    "min_value": 5,
    "max_value": 300
}

# class ForceSensorWorker(QThread):
#     finished = pyqtSignal()
#     enabled = pyqtSignal(bool)
#     update = pyqtSignal(float, float, float)

#     def __init__(self):
#         super(ForceSensor, self).__init__()
#         self.connectForceSensor()
#         self.is_running = False
#         self.data = {}
#         self.data['measurements'] = {}

#     def connectForceSensor(self):
#         """connect and setup WDT11-U"""
#         try:
#             self.instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
#             self.instrument.serial.baudrate = 38400                           # BaudRate
#             self.instrument.serial.bytesize = 8                               # number of data bits to be requested
#             self.instrument.serial.parity = minimalmodbus.serial.PARITY_NONE  # Parity Setting here is NONE but can be ODD or EVEN
#             self.instrument.serial.stopbits = 1                               # number of stop bits
#             self.instrument.serial.timeout  = 0.5                             # timeout time in seconds
#             self.instrument.mode = minimalmodbus.MODE_RTU                     # mode to be used (RTU or ascii mode)
#             self.instrument.clear_buffers_before_each_transaction = True      # clean up before each execution
#             self.instrument.close_port_after_each_call = True                 # clean up after each execution
#             self.tara()
            
#         except:
#             self.is_exception = True
#             print("cannot connect")

#     def run(self):
#         self.data = {}
#         self.data['measurements'] = {}
#         self.tara()
#         self.min_max_reset()
#         time_started = time.time()
#         while(self.is_running):
#             time.sleep(0.01)
#             current_time = (time.time() - time_started)
#             self.data['measurements'][current_time] = self.filter_value(self.get_current_value())
#             self.data['max_val'] = self.filter_value(self.get_max_value())
#             self.update.emit(current_time, self.data['measurements'][current_time], self.data['max_val'])
#         self.finished.emit()
    
#     def filter_value(self, value):
#         if value > 6000:
#             # 6553.6 58981.5
#             return float(f'{(value - 65533.6):.2f}')
#         else:
#             return float(f'{(value):.2f}')

#     def tara(self):
#         self.instrument.write_bit(4000, True)

#     def min_max_reset(self):
#         self.instrument.write_bit(4001, True)

#     def get_current_value(self):
#         return self.instrument.read_register(0)

#     def get_min_value(self):
#         return self.instrument.read_register(2)
    
#     def get_max_value(self):
#         return self.instrument.read_register(4)
        
#     def stop(self):
#         self.is_running = False
#         self.enabled.emit(True)




    # def run(self):
    #     if self.arduino.isOpen():
    #         # print("{} connected! Press CTRL-C to exit. ".format(arduino.port))
    #         try:
    #             while True:
    #                 cmd=input("Enter command : ")
    #                 self.arduino.write(bytes("{}".format(cmd), "utf-8"))
    #                 time.sleep(0.1) # wait for arduino to answer
    #                 # while arduino.inWaiting() == 0: pass
    #                 # if arduino.inWaiting() > 0: 
    #                 #     answer=arduino.readline()
    #                 #     print(answer.decode("utf-8").replace('\n', ''))
    #                 #     arduino.flushInput() #remove data after reading
    #         except KeyboardInterrupt:
    #             print("KeyboardInterrupt has been caught.")


# class RotationStepperMotorsWorker(QThread):
#     update = pyqtSignal(float, float, float)

#     def __init__(self, p):                       
#         super(RotationStepperMotorsWorker, self).__init__()
#         self.p = p

#     def run(self):
#         if self.arduino.isOpen():
#             # print("{} connected! Press CTRL-C to exit. ".format(arduino.port))
#             try:
#                 while True:
#                     cmd=input("Enter command : ")
#                     self.arduino.write(bytes("{}".format(cmd), "utf-8"))
#                     time.sleep(0.1) # wait for arduino to answer
#                     # while arduino.inWaiting() == 0: pass
#                     # if arduino.inWaiting() > 0: 
#                     #     answer=arduino.readline()
#                     #     print(answer.decode("utf-8").replace('\n', ''))
#                     #     arduino.flushInput() #remove data after reading
#             except KeyboardInterrupt:
#                 print("KeyboardInterrupt has been caught.")

#     def stop(self):
#         self.p.is_running = False
#         self.enabled.emit(True)
    
#     def filter_value(self, value):
#         if value > 6000:
#             # 6553.6 58981.5
#             return float(f'{(value - 65533.6):.2f}')
#         else:
#             return float(f'{(value):.2f}')

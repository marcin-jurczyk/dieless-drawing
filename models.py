from sqlite3 import connect
from PyQt5.QtCore import pyqtSignal, QThread
import minimalmodbus, time, serial
from config import *
from enum import Enum

class Device():
    def __init__(self): 
        self.paused = False
        # self.cancel = cancel_func
        self.is_exception = False

class ForceSensor():
    def __init__(self):
        self.connect()
        self.is_running = False
        self.data = {}
        self.data['measurements'] = {}
        self.worker: ForceSensorWorker = None

    def connect(self):
        for port in usb_ports:
            try:
                self.instrument = minimalmodbus.Instrument(port, force_sensor_config["address"])
                self.instrument.serial.baudrate = force_sensor_config["baudrate"]        # BaudRate
                self.instrument.serial.bytesize = force_sensor_config["bytesize"]        # number of data bits to be requested
                self.instrument.serial.parity = minimalmodbus.serial.PARITY_NONE         # Parity Setting here is NONE but can be ODD or EVEN
                self.instrument.serial.stopbits = force_sensor_config["stopbits"]        # number of stop bits
                # self.instrument.clear_buffers_before_each_transaction = True             # clean up before each execution
                # self.instrument.close_port_after_each_call = True                        # clean up after each execution
                self.tara()
                break
            except:
                self.is_exception = True
                print(f"cannot connect to {port}")

    def tara(self):
        self.instrument.write_bit(4000, True)

    def min_max_reset(self):
        self.instrument.write_bit(4001, True)

    def get_current_value(self):
        return self.instrument.read_register(0)

    def get_min_value(self):
        return self.instrument.read_register(2)
    
    def get_max_value(self):
        return self.instrument.read_register(4)

    def reset_data(self):
        self.data = {}
        self.data['measurements'] = []
        self.min_max_reset()
        self.tara()


class ForceSensorWorker(QThread):
    finished = pyqtSignal()
    enabled = pyqtSignal(bool)
    update = pyqtSignal(float, float, float)

    def __init__(self, p):                       
        super(ForceSensorWorker, self).__init__()
        self.p = p

    def run(self):

        self.p.reset_data()
        self.p.is_running = True
        time_started = time.time()
        while(self.p.is_running):
            time.sleep(0.01)
            current_time = (time.time() - time_started)
            self.p.data['measurements'].append({"time": current_time, "value": self.filter_value(self.p.get_current_value())})
            self.p.data['max_val'] = self.filter_value(self.p.get_max_value())
            self.update.emit(current_time, self.p.data['measurements'][-1]["value"], self.p.data['max_val'])
        self.p.data['duration'] = (time.time() - time_started)
        self.finished.emit()
        # self.enabled.emit()

    def stop(self):
        self.p.is_running = False
        self.enabled.emit(True)
    
    def filter_value(self, value):
        if value > 6000:
            # 6553.6 58981.5
            return float(f'{(value - 65533.6):.2f}')
        else:
            return float(f'{(value):.2f}')


class Direction(Enum):
    CLOCKWISE = 0
    COUNTERCLOCKWISE = 1


class RotationStepperMotors():
    def __init__(self):
        self.arduino = None
        self.running = False
        self.direction = Direction.CLOCKWISE
        self.speed = 5000
        self.connect()

    def connect(self):
        time.sleep(1)
        for port in serial_ports: 
            try:
                self.arduino = serial.Serial(port, 9600, timeout=1) 
                time.sleep(0.1) #wait for serial to open
                break
            except: 
                print("Check your connection!")
        

    def send_command(self, running = None, direction = None, speed = None):
        if running is None:
            running = self.running
        if direction is None:
            direction = self.direction
        if speed is None:
            speed = self.speed
            
        if self.arduino.isOpen():
            try:
                cmd = "{};{};{}".format({False: '0', True: '1'}[running], direction.value, speed)
                print(cmd)
                self.arduino.write(bytes("{}".format(cmd), "utf-8"))
            except:
                print("Device is disconnected!")

    def set_running(self, r: bool):
        self.running = r

    def set_direction(self, d: Direction):
        self.direction = d

    def set_speed(self, new_speed: int):
        self.speed = new_speed


class progressThread(QThread):

    progress_update = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, limit):
        QThread.__init__(self)
        self.limit = limit

    def stop(self):
        print("thread 'ProgressBar' stopped")
        self.quit()
        self.wait()

    def run(self):
        for i in range (self.limit):
            self.progress_update.emit(i+1)
            time.sleep(1)
        self.finished.emit()


        # while 1:      
        #     maxVal = 1 # NOTE THIS CHANGED to 1 since updateProgressBar was updating the value by 1 every time
        #     self.progress_update.emit(maxVal) # self.emit(SIGNAL('PROGRESS'), maxVal)
        #     # Tell the thread to sleep for 1 second and let other things run
        #     time.sleep(1)


# def updateProgressBar(self, maxVal):
#     self.ui.progressBar.setValue(self.ui.progressBar.value() + maxVal)
#     if maxVal == 0:
#         self.ui.progressBar.setValue(100)
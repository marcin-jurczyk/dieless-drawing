import sys, datetime, json
import pymongo
import pyqtgraph as pg
from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtCore import pyqtSlot, QThread, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QSlider, QMenu, QToolButton
from PyQt5.uic import loadUi
import numpy as np
from scipy.interpolate import make_interp_spline
from models import *



client = pymongo.MongoClient("mongodb+srv://creative:creative@dieless-drawing.v0znjch.mongodb.net/?retryWrites=true&w=majority")
db = client.test
db = client["dieless-drawing"]
collection = db['data'] 


class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()
        self.force_sensor = ForceSensor()
        self.rotation_motors = RotationStepperMotors()
        self.setupUi()
        self.setupPlot()
        # self.connectForceSensor()
        
    
    def setupPlot(self):
        self.graphWidget.setBackground('w')
        self.graphWidget.plot(title="Three plot curves")
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setAntialias = True
        # self.graphWidget.setRenderHints(QtGui.QPainter.Antialiasing)
        self.pen = pg.mkPen(color=(255, 0, 0))

        
    def setupUi(self):
        loadUi('layout.ui',self)
        self.setWindowTitle('Dieless drawing machine control')
        self.startBtn.clicked.connect(self.handleStartBtn)
        self.stopBtn.clicked.connect(self.handleStopBtn)
        self.startBtn.setIcon(QIcon('resources/start-icon.png'))
        self.stopBtn.setIcon(QIcon('resources/stop-icon.png'))

        # self.addComboBoxAndTooltip()

        self.preHeatingCheckBox.stateChanged.connect(self.handlePreHeatingCheckBox)
        self.preHeatingProgressBar.setValue(0)

        self.preHeatingSpinBox.setMinimum(pre_heating_config['min_value'])
        self.preHeatingSpinBox.setMaximum(pre_heating_config['max_value'])
        self.preHeatingSpinBox.setEnabled(False)

        self.rotationSpeedSlider.setMinimum(rotation_stepper_motors_config['max_speed'])
        self.rotationSpeedSlider.setMaximum(rotation_stepper_motors_config['min_speed'])
        self.rotationSpeedSlider.setMaximum(rotation_stepper_motors_config['min_speed'])
        self.rotationSpeedSlider.setTickPosition(QSlider.TicksBelow)
        self.rotationSpeedSlider.setSingleStep(10)
        self.rotationSpeedSlider.setTickInterval(1000)
        self.rotationSpeedSlider.setValue(rotation_stepper_motors_config['initial_speed'])
        self.rotationSpeedSlider.valueChanged.connect(self.handleRotationSpeedSlider)
        self.rotationSpeedLine.setText(str(self.rotation_motors.speed))
        
        self.moveLeftRSBtn.pressed.connect(lambda: self.rotation_motors.send_command(True, Direction.CLOCKWISE))
        self.moveLeftRSBtn.released.connect(lambda: self.rotation_motors.send_command(False))
        self.moveRightRSBtn.pressed.connect(lambda: self.rotation_motors.send_command(True, Direction.COUNTERCLOCKWISE))
        self.moveRightRSBtn.released.connect(lambda: self.rotation_motors.send_command(False))


    def addComboBoxAndTooltip(self):
        self.saveComboBox.view().pressed.connect(self.handleItemPressed)
        self.saveComboBox.setModel(QStandardItemModel(self.saveComboBox))
        self.saveToolButton.setText('Save options')
        self.toolmenu = QMenu(self)
        for i in range(3):
            self.saveComboBox.addItem('Category %s' % i)
            item = self.saveComboBox.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)
            action = self.toolmenu.addAction('Category %s' % i)
            action.setCheckable(True)
        self.saveToolButton.setMenu(self.toolmenu)
        self.saveToolButton.setPopupMode(QToolButton.InstantPopup)

    def handleItemPressed(self, index):
        item = self.saveComboBox.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    # @pyqtSignal
    def handleRotationSpeedLine():
        pass

    @pyqtSlot()
    def handlePreHeatingCheckBox(self):
        self.preHeatingSpinBox.setEnabled(self.preHeatingCheckBox.isChecked())


    @pyqtSlot()
    def handleRotationSpeedSlider(self):
        self.rotationSpeedLine.setText(str(self.rotationSpeedSlider.value()))
        # self.rotation_motors.send_command(speed = str(self.rotationSpeedSlider.value()))
        self.rotation_motors.set_speed(str(self.rotationSpeedSlider.value()))

    @pyqtSlot()
    def handleStopBtn(self):
        self.currentValueLbl.setText(f"STOP")
        self.preHeatingProgressBar.setValue(0)
        # collection.insert_one(self.force_sensor.data)

    @pyqtSlot()
    def handleSaveBtn(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        if self.saveFileCheckBox.isChecked():
            with open(f"{save_file_location}/measurment_{date}.json", "w") as fp:
                json.dump(self.force_sensor.data , fp)
        if self.sa

    
    def updateForceSensor(self, current_time, current_value, max_value):
        self.updateTime(current_time)
        self.currentValueLbl.setText(str(current_value))
        self.maxValueLbl.setText(str(max_value))
        self.graphWidget.plot(
            [o['time'] for o in self.force_sensor.data['measurements']], 
            [o['value'] for o in self.force_sensor.data['measurements']], 
            clear=True, pen=self.pen, antialias=True)
        
    def updateTime(self, new_time):
        self.timeLbl.setText(f'{new_time:.2f}')
        
    def enableStartButton(self, enabled):
        self.startBtn.setEnabled(enabled)

    def handlePreHeating(self):
        
        self.preHeatingProgressBar.setMaximum(self.preHeatingSpinBox.value())
        self.pre_heating_thread = progressThread(self.preHeatingSpinBox.value())
        self.pre_heating_thread.progress_update.connect(self.preHeatingProgressBar.setValue)
        self.pre_heating_thread.finished.connect(self.pre_heating_thread.stop)
        self.pre_heating_thread.finished.connect(self.startMeasurement)
        self.pre_heating_thread.start()
            
            # for i in range (self.preHeatingSpinBox.value()):
            #     time.sleep(1)
            #     self.preHeatingProgressBar.setValue(i)

    
    @pyqtSlot()
    def handleStartBtn(self):
        self.enableStartButton(False)
        if self.preHeatingCheckBox.isChecked() == True:
            self.handlePreHeating()
        else:
            self.startMeasurement()

        
    def startMeasurement(self):
        self.thread = QThread()
        self.force_sensor.worker = ForceSensorWorker(self.force_sensor)
        self.stopBtn.clicked.connect(self.force_sensor.worker.stop)
        self.force_sensor.worker.moveToThread(self.thread)
        self.force_sensor.is_running = True
        self.thread.started.connect(self.force_sensor.worker.run)
        self.force_sensor.worker.finished.connect(self.thread.quit)
        self.force_sensor.worker.finished.connect(self.force_sensor.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.force_sensor.worker.update.connect(self.updateForceSensor)
        self.force_sensor.worker.enabled.connect(self.enableStartButton)
        self.thread.start()


        # print(f'{1}: {sensy_boi.read_register(0, 1)}')
        #     if i == 150:
        #         for j in range(60000):
        #             try:
        #                 sensy_boi.write_register(i, 1, 0, 6)
        #                 print("done")
        #             except:
        #                 pass
    
    
# class Force_Sensor(QThread):
#     finished = pyqtSignal()
#     update = pyqtSignal(float, float, float)
#     enabled = pyqtSignal(bool)
    
#     def __init__(self, instrument):
#         super(Force_Sensor, self).__init__()
#         self.instrument = instrument
#         self.is_running = True
    
#     def run(self):
#         time_started = time.time()
#         self.instrument.write_bit(4001, True) # reset max/min value
#         while(self.is_running):
#             time.sleep(0.01)
#             current_time = (time.time() - time_started)
#             current_val = self.filter_force(self.instrument.read_register(0))
#             max_val = self.filter_force(self.instrument.read_register(4))
#             self.update.emit(current_time, current_val, max_val)
#         self.finished.emit()
    
#     def filter_force(self, value):
#         if value > 6000:
#             # 6553.6 58981.5
#             return float(f'{(value - 65533.6):.2f}')
#         else:
#             return float(f'{(value):.2f}')
        
#     def stop(self):
#         self.is_running = False
#         self.enabled.emit(True)
        
    
app=QApplication(sys.argv)
gui=GUI()
gui.show()
sys.exit(app.exec_())
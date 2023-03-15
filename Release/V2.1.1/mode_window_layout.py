'''
Import
'''
import sys
import time
import threading
import serial
import re
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, \
    QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QRadioButton, QMenu

from areamode import AreaModeFunc

class SingleModeWindow(QWidget):

    # !!!!!!! I switched to the test_data to display the location##
    test_data = ''

    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial = None
        self.ESPserial = None
        self.location = None  # Initialize location variable
        self.location_lock = threading.Lock()

        self.start_resetting = False

        self.init_ui()

    def init_ui(self):
        # Create central widget and main layout
        main_layout = QVBoxLayout(self)

        # Create 3D printer layout
        printer_layout = QVBoxLayout()

        # Create button layout
        button_layout = QHBoxLayout()
        button_label = QLabel('Button Model:')
        button_layout.addWidget(button_label)
        self.button_combo = QComboBox()
        self.button_combo.addItems(['Button Profile 1', 'Button Profile 2'])
        button_layout.addWidget(self.button_combo)
        self.test_button = QPushButton('Test')
        self.test_button.clicked.connect(self.send_gcode)
        button_layout.addWidget(self.test_button)
        printer_layout.addLayout(button_layout)

        # Create port layout
        port_layout = QHBoxLayout()
        port_label = QLabel('Port:')
        port_layout.addWidget(port_label)
        self.port_combo = QComboBox()
        self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8'])
        port_layout.addWidget(self.port_combo)

        # Create baud layout
        baud_layout = QHBoxLayout()
        baud_label = QLabel('Baud Rate:')
        baud_layout.addWidget(baud_label)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        baud_layout.addWidget(self.baud_combo)

        # Create connect button layout
        connect_layout = QHBoxLayout()
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect)
        connect_layout.addWidget(self.connect_button)

        # Combine port and baud layouts
        port_baud_layout = QHBoxLayout()
        port_baud_layout.addLayout(port_layout)
        port_baud_layout.addLayout(baud_layout)
        port_baud_layout.addLayout(connect_layout)
        printer_layout.addLayout(port_baud_layout)

        # Create send layout
        send_layout = QHBoxLayout()
        send_label = QLabel('Send:')
        send_layout.addWidget(send_label)
        self.send_edit = QTextEdit()
        self.send_edit.setMaximumHeight(80)  # set maximum height to 50 pixels
        send_layout.addWidget(self.send_edit)
        self.send_button = QPushButton('Send')
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send)
        send_layout.addWidget(self.send_button)
        printer_layout.addLayout(send_layout)

        # Create receive layout
        receive_layout = QHBoxLayout()
        receive_label = QLabel('Receive:')
        receive_layout.addWidget(receive_label)
        self.debug_monitor = QTextEdit()
        self.debug_monitor.setMaximumHeight(100)  # set maximum height to 50 pixels
        self.debug_monitor.setReadOnly(True)
        receive_layout.addWidget(self.debug_monitor)
        printer_layout.addLayout(receive_layout)

        # Add printer layout to main layout
        main_layout.addLayout(printer_layout)

        # Create microcontroller layout
        microcontroller_layout = QVBoxLayout()

        # Create microcontroller port layout
        microcontroller_port_layout = QHBoxLayout()
        microcontroller_port_label = QLabel('Microcontroller Port:')
        microcontroller_port_layout.addWidget(microcontroller_port_label)
        self.microcontroller_port_combo = QComboBox()
        self.microcontroller_port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8'])
        microcontroller_port_layout.addWidget(self.microcontroller_port_combo)

        # Create microcontroller baud layout
        microcontroller_baud_layout = QHBoxLayout()
        microcontroller_baud_label = QLabel('Microcontroller Baud Rate:')
        microcontroller_baud_layout.addWidget(microcontroller_baud_label)
        self.microcontroller_baud_combo = QComboBox()
        self.microcontroller_baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        microcontroller_baud_layout.addWidget(self.microcontroller_baud_combo)

        # Create microcontroller connect button layout
        microcontroller_connect_layout = QHBoxLayout()
        self.microcontroller_connect_button = QPushButton('Connect Microcontroller')
        self.microcontroller_connect_button.clicked.connect(self.connect_microcontroller)
        microcontroller_connect_layout.addWidget(self.microcontroller_connect_button)

        # Combine microcontroller port, baud, and connect button layouts
        microcontroller_port_baud_layout = QHBoxLayout()
        microcontroller_port_baud_layout.addLayout(microcontroller_port_layout)
        microcontroller_port_baud_layout.addLayout(microcontroller_baud_layout)
        microcontroller_port_baud_layout.addLayout(microcontroller_connect_layout)

        # Add microcontroller port and baud layouts to main layout
        main_layout.addLayout(microcontroller_port_baud_layout)

########################################################
        # Create microcontroller debug monitor layout
        receive_layout_microcontroller = QHBoxLayout()
        receive_label_microcontroller = QLabel('Microcontroller Receive:')
        receive_layout_microcontroller.addWidget(receive_label_microcontroller)
        self.microcontroller_debug_monitor = QTextEdit()
        self.microcontroller_debug_monitor.setMaximumHeight(100)  # set maximum height to 100 pixels
        self.microcontroller_debug_monitor.setReadOnly(True)
        receive_layout_microcontroller.addWidget(self.microcontroller_debug_monitor)
        main_layout.addLayout(receive_layout_microcontroller)

        self.setWindowTitle('NeoPrint')
        self.resize(800, 400)

    def send_M114(self):
        self.serial.write(b'M114') # Send M114 separately to the 3D printer

    def connect_microcontroller(self):
        port = self.microcontroller_port_combo.currentText()
        baud = int(self.microcontroller_baud_combo.currentText())

        # self.microcontroller_serial = serial.Serial(port, baud)
        # print("Microcontroller is now online!")
        # self.microcontroller_connect_button.setText('Disconnect')
        # self.microcontroller_connect_button.clicked.disconnect(self.connect_microcontroller)
        # self.microcontroller_connect_button.clicked.connect(self.disconnect_microcontroller)
        # #self.microcontroller_send_button.setEnabled(True)
        # # Start the serial reader thread
        # self.microcontroller_reader_thread = threading.Thread(target=self.read_microcontroller_serial)
        # self.microcontroller_reader_thread.daemon = True
        # self.microcontroller_reader_thread.start()

        try:
            self.microcontroller_serial = serial.Serial(port, baud)
            print("Microcontroller is now online!")
            self.microcontroller_connect_button.setText('Disconnect')
            self.microcontroller_connect_button.clicked.disconnect(self.connect_microcontroller)
            self.microcontroller_connect_button.clicked.connect(self.disconnect_microcontroller)
            #self.microcontroller_send_button.setEnabled(True)

            # Start the serial reader thread
            self.microcontroller_reader_thread = threading.Thread(target=self.read_microcontroller_serial)
            self.microcontroller_reader_thread.daemon = True
            self.microcontroller_reader_thread.start()

        except:
            self.microcontroller_debug_monitor.append('Failed to connect to microcontroller')
            #self.microcontroller_send_button.setEnabled(False)

    def connect(self):
        port = self.port_combo.currentText()

        baud = int(self.baud_combo.currentText())
        try:
            self.serial = serial.Serial(port, baud)
            print("Printer is now online!")
            self.connect_button.setText('Disconnect')
            self.connect_button.clicked.disconnect(self.connect)
            self.connect_button.clicked.connect(self.disconnect)
            self.send_button.setEnabled(True)
            self.test_button.setEnabled(True)  # Enable the Test button

            # Start the serial reader thread
            self.reader_thread = threading.Thread(target=self.read_serial)
            self.reader_thread.daemon = True
            self.reader_thread.start()

        except:
            self.debug_monitor.append('Failed to connect')

            # Add the error message to the test data string
            self.test_data += "Failed to connect \n"
            self.test_button.setEnabled(False)  # Disable the Test button

    def disconnect_microcontroller(self):
        if self.microcontroller_serial is not None:
            self.microcontroller_reader_running = False  # Set the flag to stop the reader thread
            self.microcontroller_serial.close()
            self.microcontroller_serial = None
            self.microcontroller_connect_button.setText('Connect')
            self.microcontroller_connect_button.clicked.disconnect(self.disconnect_microcontroller)
            self.microcontroller_connect_button.clicked.connect(self.connect_microcontroller)
            self.microcontroller_send_button.setEnabled(False)

    def disconnect(self):
        if self.serial is not None:
            self.reader_running = False  # Set the flag to stop the reader thread
            self.serial.close()
            self.serial = None
            self.connect_button.setText('Connect')
            self.connect_button.clicked.disconnect(self.disconnect)
            self.connect_button.clicked.connect(self.connect)
            self.test_button.setEnabled(False)

    def send(self):
        if self.serial is None:
            return
        data = self.send_edit.toPlainText() + '\n'
        self.serial.write(data.encode())
        response = self.serial.readline().decode()
        self.debug_monitor.append(response)

    def send_command(self, command):
        if self.serial is None:
            return
        data = command + '\n'
        self.serial.write(data.encode())
        response = self.serial.readline().decode()
        self.debug_monitor.append(response)

    def send_gcode(self):
        # self.send_M114()
        time.sleep(1)
        button_model = self.button_combo.currentText()
        if button_model == 'Button Profile 1':
            filename = 'button1.gcode'
        else:
            filename = 'button2.gcode'
        with open(filename, 'r') as f:
            for line in f:
                self.send_edit.setText(line.strip())
                self.send()
                time.sleep(1)  # Add a small delay between sending each line

        command = "M400\n"
        self.serial.write(command.encode())
        # self.send_command('M400')
        # self.send_command("G91")
        self.start_resetting = True

    def read_microcontroller_serial(self):
        self.microcontroller_reader_running = True

        wait_time = True

        while self.microcontroller_reader_running:
            if self.microcontroller_serial is not None:
                response = ''
                while self.microcontroller_serial.inWaiting() > 0:
                    foo = str(self.microcontroller_serial.read(self.microcontroller_serial.inWaiting()))
                    # print(type(foo))
                    # print('')
                    if foo.startswith("b'"):
                        response += foo
                if response:
                    # self.microcontroller_debug_monitor.append(response)
                    # self.microcontroller_test_data += response

                    activated_force = response.split(';')[1][:-5]  # records
                    activated_signal = response.split(';')[0][2:]
                    print(response)
                    self.microcontroller_debug_monitor.append(f"force: {activated_force}, signal: {activated_signal}")
                    print(f"force: {activated_force}, signal: {activated_signal}")




                    if self.start_resetting:
                        if wait_time:
                            for i in range(15):
                                time.sleep(1)
                                # self.microcontroller_serial.flush()
                                # self.microcontroller_serial.flushInput()
                                # self.microcontroller_serial.flushOutput()

                            wait_time = False

                        if activated_signal == "1":
                            self.microcontroller_reader_running = False
                            self.start_resetting = False
                            print("end")

                            data = "M114\n"
                            self.serial.write(data.encode())
                            response = self.serial.readline().decode()
                            self.debug_monitor.append(response)



                            # command = "M114\n"
                            # self.serial.write(command.encode())
                            # time.sleep(0.5)
                            #
                            # corr = ""
                            #
                            # while self.serial.inWaiting() > 0:
                            #     corr += self.serial.read(self.serial.inWaiting()).decode()
                            #     print()
                            # if r'X:[0-9].[0-9] Y:[0-9].[0-9] Z:[0-9].[0-9] E:[0-9].[0-9] Count X:[0-9]* Y:[0-9]* Z:[0-9]*' in response:
                            #     self.debug_monitor.append(response)

                            break

                        command = "G91\n"
                        self.serial.write(command.encode())
                        command = "G0 Z-0.01\n"
                        self.serial.write(command.encode())
                        # self.send_command("G0 Z-0.01")
                        # self.send_command("M400")
                        print("command sent")


            # self.p.send("G91")
            # self.p.send("G0 Z-0.01")

            time.sleep(0.001)

    def read_serial(self):
        # global location_data
        self.reader_running = True
        while self.reader_running:
            if self.serial is not None:
                response = ''
                while self.serial.inWaiting() > 0:
                    response += self.serial.read(self.serial.inWaiting()).decode()
                if r'X:[0-9].[0-9] Y:[0-9].[0-9] Z:[0-9].[0-9] E:[0-9].[0-9] Count X:[0-9]* Y:[0-9]* Z:[0-9]*' in response:
                    with self.location_lock:
                        location_data = response
                    #     print(f"Location: {self.location}")
                    self.debug_monitor.append(response)

                    # Add the current response to the test data string
                    self.test_data += response

                time.sleep(0.01)
class AreaModeWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial = None
        self.ESPserial = None
        self.location = None  # Initialize location variable
        self.location_lock = threading.Lock()

        self.start_resetting = False

        self.init_ui()

    def init_ui(self):
        # Create central widget and main layout
        main_layout = QVBoxLayout(self)

        # Create 3D printer layout
        printer_layout = QVBoxLayout()

        # Create button layout
        button_layout = QHBoxLayout()
        button_label = QLabel('Button Model:')
        button_layout.addWidget(button_label)
        self.button_combo = QComboBox()
        self.button_combo.addItems(['Button Profile 1', 'Button Profile 2'])
        button_layout.addWidget(self.button_combo)
        self.test_button = QPushButton('Test')
        self.test_button.clicked.connect(self.send_gcode)
        button_layout.addWidget(self.test_button)
        printer_layout.addLayout(button_layout)

        # Create test point layout
        test_point_layout = QHBoxLayout()
        test_point_label = QLabel('Test Points:')
        test_point_layout.addWidget(test_point_label)
        self.test_point_combo = QComboBox()
        self.test_point_combo.addItems(['1', '3', '5'])
        self.test_button.clicked.connect(AreaModeFunc.generateTestpoints)
        test_point_layout.addWidget(self.test_point_combo)
        printer_layout.addLayout(test_point_layout)


        # Create port layout
        port_layout = QHBoxLayout()
        port_label = QLabel('Port:')
        port_layout.addWidget(port_label)
        self.port_combo = QComboBox()
        self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8'])
        port_layout.addWidget(self.port_combo)

        # Create baud layout
        baud_layout = QHBoxLayout()
        baud_label = QLabel('Baud Rate:')
        baud_layout.addWidget(baud_label)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        baud_layout.addWidget(self.baud_combo)

        # Create connect button layout
        connect_layout = QHBoxLayout()
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect)
        connect_layout.addWidget(self.connect_button)

        # Combine port and baud layouts
        port_baud_layout = QHBoxLayout()
        port_baud_layout.addLayout(port_layout)
        port_baud_layout.addLayout(baud_layout)
        port_baud_layout.addLayout(connect_layout)
        printer_layout.addLayout(port_baud_layout)

        # Create send layout
        send_layout = QHBoxLayout()
        send_label = QLabel('Send:')
        send_layout.addWidget(send_label)
        self.send_edit = QTextEdit()
        self.send_edit.setMaximumHeight(80)  # set maximum height to 50 pixels
        send_layout.addWidget(self.send_edit)
        self.send_button = QPushButton('Send')
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send)
        send_layout.addWidget(self.send_button)
        printer_layout.addLayout(send_layout)

        # Create receive layout
        receive_layout = QHBoxLayout()
        receive_label = QLabel('Receive:')
        receive_layout.addWidget(receive_label)
        self.debug_monitor = QTextEdit()
        self.debug_monitor.setMaximumHeight(100)  # set maximum height to 50 pixels
        self.debug_monitor.setReadOnly(True)
        receive_layout.addWidget(self.debug_monitor)
        printer_layout.addLayout(receive_layout)

        # Add printer layout to main layout
        main_layout.addLayout(printer_layout)

        # Create microcontroller layout
        microcontroller_layout = QVBoxLayout()

        # Create microcontroller port layout
        microcontroller_port_layout = QHBoxLayout()
        microcontroller_port_label = QLabel('Microcontroller Port:')
        microcontroller_port_layout.addWidget(microcontroller_port_label)
        self.microcontroller_port_combo = QComboBox()
        self.microcontroller_port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8'])
        microcontroller_port_layout.addWidget(self.microcontroller_port_combo)

        # Create microcontroller baud layout
        microcontroller_baud_layout = QHBoxLayout()
        microcontroller_baud_label = QLabel('Microcontroller Baud Rate:')
        microcontroller_baud_layout.addWidget(microcontroller_baud_label)
        self.microcontroller_baud_combo = QComboBox()
        self.microcontroller_baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        microcontroller_baud_layout.addWidget(self.microcontroller_baud_combo)

        # Create microcontroller connect button layout
        microcontroller_connect_layout = QHBoxLayout()
        self.microcontroller_connect_button = QPushButton('Connect Microcontroller')
        self.microcontroller_connect_button.clicked.connect(self.connect_microcontroller)
        microcontroller_connect_layout.addWidget(self.microcontroller_connect_button)

        # Combine microcontroller port, baud, and connect button layouts
        microcontroller_port_baud_layout = QHBoxLayout()
        microcontroller_port_baud_layout.addLayout(microcontroller_port_layout)
        microcontroller_port_baud_layout.addLayout(microcontroller_baud_layout)
        microcontroller_port_baud_layout.addLayout(microcontroller_connect_layout)

        # Add microcontroller port and baud layouts to main layout
        main_layout.addLayout(microcontroller_port_baud_layout)

########################################################
        # Create microcontroller debug monitor layout
        receive_layout_microcontroller = QHBoxLayout()
        receive_label_microcontroller = QLabel('Microcontroller Receive:')
        receive_layout_microcontroller.addWidget(receive_label_microcontroller)
        self.microcontroller_debug_monitor = QTextEdit()
        self.microcontroller_debug_monitor.setMaximumHeight(100)  # set maximum height to 100 pixels
        self.microcontroller_debug_monitor.setReadOnly(True)
        receive_layout_microcontroller.addWidget(self.microcontroller_debug_monitor)
        main_layout.addLayout(receive_layout_microcontroller)

        self.setWindowTitle('NeoPrint')
        self.resize(800, 400)

    def send_M114(self):
        self.serial.write(b'M114') # Send M114 separately to the 3D printer

    def connect_microcontroller(self):
        port = self.microcontroller_port_combo.currentText()
        baud = int(self.microcontroller_baud_combo.currentText())

        # self.microcontroller_serial = serial.Serial(port, baud)
        # print("Microcontroller is now online!")
        # self.microcontroller_connect_button.setText('Disconnect')
        # self.microcontroller_connect_button.clicked.disconnect(self.connect_microcontroller)
        # self.microcontroller_connect_button.clicked.connect(self.disconnect_microcontroller)
        # #self.microcontroller_send_button.setEnabled(True)
        # # Start the serial reader thread
        # self.microcontroller_reader_thread = threading.Thread(target=self.read_microcontroller_serial)
        # self.microcontroller_reader_thread.daemon = True
        # self.microcontroller_reader_thread.start()

        try:
            self.microcontroller_serial = serial.Serial(port, baud)
            print("Microcontroller is now online!")
            self.microcontroller_connect_button.setText('Disconnect')
            self.microcontroller_connect_button.clicked.disconnect(self.connect_microcontroller)
            self.microcontroller_connect_button.clicked.connect(self.disconnect_microcontroller)
            #self.microcontroller_send_button.setEnabled(True)

            # Start the serial reader thread
            self.microcontroller_reader_thread = threading.Thread(target=self.read_microcontroller_serial)
            self.microcontroller_reader_thread.daemon = True
            self.microcontroller_reader_thread.start()

        except:
            self.microcontroller_debug_monitor.append('Failed to connect to microcontroller')
            #self.microcontroller_send_button.setEnabled(False)

    def connect(self):
        port = self.port_combo.currentText()

        baud = int(self.baud_combo.currentText())
        try:
            self.serial = serial.Serial(port, baud)
            print("Printer is now online!")
            self.connect_button.setText('Disconnect')
            self.connect_button.clicked.disconnect(self.connect)
            self.connect_button.clicked.connect(self.disconnect)
            self.send_button.setEnabled(True)
            self.test_button.setEnabled(True)  # Enable the Test button

            # Start the serial reader thread
            self.reader_thread = threading.Thread(target=self.read_serial)
            self.reader_thread.daemon = True
            self.reader_thread.start()

        except:
            self.debug_monitor.append('Failed to connect')

            # Add the error message to the test data string
            self.test_data += "Failed to connect \n"
            self.test_button.setEnabled(False)  # Disable the Test button

    def disconnect_microcontroller(self):
        if self.microcontroller_serial is not None:
            self.microcontroller_reader_running = False  # Set the flag to stop the reader thread
            self.microcontroller_serial.close()
            self.microcontroller_serial = None
            self.microcontroller_connect_button.setText('Connect')
            self.microcontroller_connect_button.clicked.disconnect(self.disconnect_microcontroller)
            self.microcontroller_connect_button.clicked.connect(self.connect_microcontroller)
            self.microcontroller_send_button.setEnabled(False)

    def disconnect(self):
        if self.serial is not None:
            self.reader_running = False  # Set the flag to stop the reader thread
            self.serial.close()
            self.serial = None
            self.connect_button.setText('Connect')
            self.connect_button.clicked.disconnect(self.disconnect)
            self.connect_button.clicked.connect(self.connect)
            self.test_button.setEnabled(False)

    def send(self):
        if self.serial is None:
            return
        data = self.send_edit.toPlainText() + '\n'
        self.serial.write(data.encode())
        response = self.serial.readline().decode()
        self.debug_monitor.append(response)

    def send_command(self, command):
        if self.serial is None:
            return
        data = command + '\n'
        self.serial.write(data.encode())
        response = self.serial.readline().decode()
        self.debug_monitor.append(response)

    def send_gcode(self):
        # self.send_M114()
        time.sleep(1)
        button_model = self.button_combo.currentText()
        if button_model == 'Button Profile 1':
            filename = 'button1.gcode'
        else:
            filename = 'button2.gcode'
        with open(filename, 'r') as f:
            for line in f:
                self.send_edit.setText(line.strip())
                self.send()
                time.sleep(1)  # Add a small delay between sending each line

        command = "M400\n"
        self.serial.write(command.encode())
        # self.send_command('M400')
        # self.send_command("G91")
        self.start_resetting = True

    def read_microcontroller_serial(self):
        self.microcontroller_reader_running = True

        wait_time = True

        while self.microcontroller_reader_running:
            if self.microcontroller_serial is not None:
                response = ''
                while self.microcontroller_serial.inWaiting() > 0:
                    foo = str(self.microcontroller_serial.read(self.microcontroller_serial.inWaiting()))
                    # print(type(foo))
                    # print('')
                    if foo.startswith("b'"):
                        response += foo
                if response:
                    # self.microcontroller_debug_monitor.append(response)
                    # self.microcontroller_test_data += response

                    activated_force = response.split(';')[1][:-5]  # records
                    activated_signal = response.split(';')[0][2:]
                    print(response)
                    self.microcontroller_debug_monitor.append(f"force: {activated_force}, signal: {activated_signal}")
                    print(f"force: {activated_force}, signal: {activated_signal}")




                    if self.start_resetting:
                        if wait_time:
                            for i in range(15):
                                time.sleep(1)
                                # self.microcontroller_serial.flush()
                                # self.microcontroller_serial.flushInput()
                                # self.microcontroller_serial.flushOutput()

                            wait_time = False

                        if activated_signal == "1":
                            self.microcontroller_reader_running = False
                            self.start_resetting = False
                            print("end")

                            data = "M114\n"
                            self.serial.write(data.encode())
                            response = self.serial.readline().decode()
                            self.debug_monitor.append(response)



                            # command = "M114\n"
                            # self.serial.write(command.encode())
                            # time.sleep(0.5)
                            #
                            # corr = ""
                            #
                            # while self.serial.inWaiting() > 0:
                            #     corr += self.serial.read(self.serial.inWaiting()).decode()
                            #     print()
                            # if r'X:[0-9].[0-9] Y:[0-9].[0-9] Z:[0-9].[0-9] E:[0-9].[0-9] Count X:[0-9]* Y:[0-9]* Z:[0-9]*' in response:
                            #     self.debug_monitor.append(response)

                            break

                        command = "G91\n"
                        self.serial.write(command.encode())
                        command = "G0 Z-0.01\n"
                        self.serial.write(command.encode())
                        # self.send_command("G0 Z-0.01")
                        # self.send_command("M400")
                        print("command sent")


            # self.p.send("G91")
            # self.p.send("G0 Z-0.01")

            time.sleep(0.001)

    def read_serial(self):
        # global location_data
        self.reader_running = True
        while self.reader_running:
            if self.serial is not None:
                response = ''
                while self.serial.inWaiting() > 0:
                    response += self.serial.read(self.serial.inWaiting()).decode()
                if r'X:[0-9].[0-9] Y:[0-9].[0-9] Z:[0-9].[0-9] E:[0-9].[0-9] Count X:[0-9]* Y:[0-9]* Z:[0-9]*' in response:
                    with self.location_lock:
                        location_data = response
                    #     print(f"Location: {self.location}")
                    self.debug_monitor.append(response)

                    # Add the current response to the test data string
                    self.test_data += response

                time.sleep(0.01)
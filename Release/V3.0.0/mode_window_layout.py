'''
Import
'''
import sys
import time
import threading
import serial
import math
import re
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, \
    QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QRadioButton, QMenu

#from areamode import AreaModeFunc

class SingleModeWindow(QWidget):

    # !!!!!!! I switched to the test_data to display the location##
    test_data = ''

    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial = None
        self.ESPserial = None
        self.location = None  # Initialize location variable
        self.location_lock = threading.Lock()

        self.button_not_pressed = False

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
        self.button_not_pressed = True

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




                    if self.button_not_pressed:
                        if wait_time:
                            for i in range(15):
                                time.sleep(1)
                                # self.microcontroller_serial.flush()
                                # self.microcontroller_serial.flushInput()
                                # self.microcontroller_serial.flushOutput()

                            wait_time = False

                        if activated_signal == "1":
                            self.microcontroller_reader_running = False
                            self.button_not_pressed = False
                            print("end")

                            data = "M114\n"
                            self.serial.write(data.encode())
                            response = self.serial.readline().decode()
                            self.debug_monitor.append(response)

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
        self.button_not_pressed = True
        self.point_coords = None

        #self.gf = general_function
        self.force_data = None
        self.distance_data = None
        self.activation = None
        self.on_surface = False
        self.current_z = None

        self.local_increment_record = None
        self.local_increment_list = []
        self.z_activation = None
        self.z_activation_list = []

        self.surface_z = None


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
        self.test_button.clicked.connect(self.TEST)
        button_layout.addWidget(self.test_button)
        printer_layout.addLayout(button_layout)

        # Create generate point button layout
        test_point_layout = QHBoxLayout()
        test_point_label = QLabel('Test Points:')
        test_point_layout.addWidget(test_point_label)
        self.test_point_combo = QComboBox()
        self.test_point_combo.addItems(['1', '3', '5'])
        test_point_layout.addWidget(self.test_point_combo)
        self.generate_button = QPushButton('Generate')
        self.generate_button.clicked.connect(self.click_to_generate_points)
        test_point_layout.addWidget(self.generate_button)
        printer_layout.addLayout(test_point_layout)

        # Create Test button
        self.TESTbutton = QPushButton('TESTBY')
        self.TESTbutton.clicked.connect(self.TEST)
        test_point_layout.addWidget(self.TESTbutton)



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

    def connect_microcontroller(self):
        port = self.microcontroller_port_combo.currentText()
        baud = int(self.microcontroller_baud_combo.currentText())

        try:
            self.microcontroller_serial = serial.Serial(port, baud)
            print("Microcontroller is now online!")
            self.microcontroller_connect_button.setText('Disconnect')
            self.microcontroller_connect_button.clicked.disconnect(self.connect_microcontroller)
            self.microcontroller_connect_button.clicked.connect(self.disconnect_microcontroller)
            # self.microcontroller_send_button.setEnabled(True)

            # Start the serial reader thread
            self.microcontroller_reader_thread = threading.Thread(target=self.read_microcontroller_serial)
            self.microcontroller_reader_thread.daemon = True
            self.microcontroller_reader_thread.start()

        except:
            self.microcontroller_debug_monitor.append('Failed to connect to microcontroller')
            # self.microcontroller_send_button.setEnabled(False)

    def connect(self):
        port = self.port_combo.currentText()

        baud = int(self.baud_combo.currentText())
        try:
            self.serial = serial.Serial(port, baud, timeout=10)
            #print(self.serial)
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

            #self.m114_thread = threading.Thread(target=self.send_M114_thread)
            #self.m114_thread.daemon = True
            #self.m114_thread.start()

        except:
            self.debug_monitor.append('Failed to connect')

            # Add the error message to the test data string
            #self.test_data += "Failed to connect \n"
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
                    #print(response)
                    self.microcontroller_debug_monitor.append(
                        f"force: {activated_force}, signal: {activated_signal}")
                    print(f"force: {activated_force}, signal: {activated_signal}")

                    # store the force data & distance data
                    self.force_data = activated_force
                    #print(self.button_not_pressed)
                    if activated_signal == "0":
                        self.button_not_pressed = True
                    if activated_signal == "1":
                        self.button_not_pressed = False
                        #print("button activated~")
                        #self.append_single_data()
                        #print(self.button_not_pressed)

    def read_serial(self):
        # global location_data
        #self.send_M114()
        self.reader_running = True
        while self.reader_running:
            if self.serial is not None:
                response = ''
                while self.serial.inWaiting() > 0:
                    response += self.serial.read(self.serial.inWaiting()).decode()
                #if r'X:[0-9].[0-9] Y:[0-9].[0-9] Z:[0-9].[0-9] E:[0-9].[0-9] Count X:[0-9]* Y:[0-9]* Z:[0-9]*' in response:
                if response.startswith('X:'):
                    # with self.location_lock:
                    #     location_data = response
                    # #     print(f"Location: {self.location}")
                    self.debug_monitor.append(response)
                    self.current_z = re.search(r'Z:(\d+\.\d+)', response).group(1)

                    # Add the current response to the test data string
                    #self.test_data += response

                time.sleep(0.01)


    # New added
    """
    #####################################################
    Area Logic
    #####################################################
    """
    def TEST(self):
        self.send_gcode_Test()

    def send_gcode_Test(self):
        # 先创建一个现成的list
        testpoint_list = self.point_coords
        # 先用一个坐标
        # 从list里生成gcode
        # 下面补充这个method，然后进行测试
        round = 0
        for point in testpoint_list:
            self.local_increment_record = 0

            x, y = point[0], point[1]
            self.move_to_safe_z(50) #这里的45后面需要从profile里提取
            self.move_to_xy(x, y)
            self.move_to_surface(45.9) #这里的37后面需要从profile里提取
            time.sleep(5)
            self.send_single_gcode("M400\n")
            self.increment_logic()
            time.sleep(1)
            self.send_M114()
            time.sleep(1)
            self.append_single_data()
            time.sleep(1)

            self.extract_distance_data()
            self.local_increment_list.append(self.local_increment_record) # append the increment result to the list
            print(self.z_activation) #print out to see the result
            print(self.current_z)
            self.z_activation_list.append(self.current_z)

            self.point_coords[round][2] = 45.7 - float(self.current_z) # give the current_z value back to the point_coords
            self.point_coords[round][3] = self.force_data
            round += 1

            if self.button_not_pressed is False:
                self.move_to_safe_z(45)

        self.move_to_safe_z(50)
        print("z_activation_list:", self.z_activation_list)
        print("local_increment_list:", self.local_increment_list)
        self.print_points()

    """
    #####################################################
    Generate points
    #####################################################
    """
    def click_to_generate_points(self):
        self.generate_points(3, int(self.test_point_combo.currentText()))


    def generate_points(self, radius_button, numPoints):
        #radius_button = 3
        #numPoints = 5
        new_center = [132.5, 118.4] # This value is fixed, but need to recalibrate
        radius = radius_button - 0.1  # so the very edge is not pressed
        points = []
        points.append([new_center[0], new_center[1], None, None])
        boundary = math.sqrt(numPoints)
        phi = (math.sqrt(5) + 1) / 2

        for k in range(1, numPoints):
            if (k > numPoints - boundary):
                r = radius
            else:
                r = radius * math.sqrt(k - 1 / 2) / math.sqrt(numPoints - (boundary + 1) / 2)

            angle = k * 2 * math.pi / phi / phi
            curr_x = r * math.cos(angle) + new_center[0]
            curr_y = r * math.sin(angle) + new_center[1]
            points.append([round(curr_x, 2), round(curr_y, 2), None, None])
        self.point_coords = points
        print(points)
        return 1
    def print_points(self):
        if self.point_coords:
            for point in self.point_coords:
                print(point)
        else:
            print("No points generated yet")

# 底下都是工具method

    """
    #####################################################
    Send
    #####################################################
    """
    def send_M114(self):
        self.send_single_gcode("M114\n")
    def send_single_gcode(self, gcommand):
        try:
            if self.serial is not None:
                self.serial.write(gcommand.encode())
        except Exception as e:
            print("333")
            print(f"Error: {e}")

    """
    #####################################################
    Move & increment
    #####################################################
    """
    def move_to_xy(self, x_coord, y_coord):
        gcode = f'G1 X{x_coord} Y{y_coord}\n'
        self.send_single_gcode(gcode)

    def move_to_surface(self, z_coord):
        self.send_single_gcode("G90\n")
        gcode = f'G0 Z{z_coord}\n'
        self.send_single_gcode(gcode)

    def move_to_safe_z(self, z_coord):
        self.send_single_gcode("G90\n")
        gcode = f'G0 Z{z_coord}\n'
        self.send_single_gcode(gcode)

    def increment_logic(self):
        try:
            while self.button_not_pressed:
                if float(self.force_data) > 200:
                    self.send_single_gcode("M112\n")
                    exit(0)
                self.send_single_gcode("G91\n")
                self.send_single_gcode("G0 Z-0.01\n")
                self.local_increment_record += 1  # local record of increment, can be used to compare with test result
                if float(self.force_data) > 200: # or float(self.current_z) < 44.9
                    self.send_single_gcode("M112\n")
                    exit(0)
            print("Increment process done")
            return
        except Exception as e:
            print("111")
            print(f"Error: {e}")


    """
    #####################################################
    Data
    #####################################################
    """
    def append_single_data(self):
        try:
            self.send_single_gcode("M114\n")
            response = self.serial.readline().decode()
            self.debug_monitor.append(response)
            # 这里逻辑要和serial相关，很重要，要一点点弄清楚
        except Exception as e:
            print("222")
            print(f"Error: {e}")

    def extract_distance_data(self):
        try:
            self.send_M114()
            z_value = re.search(r'Z:(\d+\.\d+)', self.debug_monitor.toPlainText()).group(1)
            self.z_activation = float(z_value)
            z_activation_distance = 45.7 - float(z_value)

        except AttributeError:
            print('Error: Unable to extract Z value from debug monitor')
            return




    # def generate_gcode(self, points, safe_z_height=5):
    #     """
    #     Generate G-code commands to probe a list of points.
    #
    #     :param points: List of points in the format [[x1, y1, None, None], [x2, y2, None, None], ...]
    #     :param safe_z_height: The safe Z height for travel moves (default: 5)
    #     :return: List of G-code commands
    #     """
    #     # Initialize an empty list to store the G-code commands
    #     gcode_commands = []
    #     # Add a G28 command to home all axes before starting the probing process
    #     gcode_commands.append("G28")
    #     for point in points:
    #         x, y = point[0], point[1]
    #         # Move the probe up to the safe Z height
    #         gcode_commands.append(f"G1 Z{safe_z_height}")
    #         # Move the probe to the XY coordinates of the testing point
    #         gcode_commands.append(f"G1 X{x} Y{y}")
    #         # Add the G30 command to perform a single Z-probe at the current XY position
    #         gcode_commands.append("G30")
    #     # Add a G28 command to home all axes after completing the probing process
    #     gcode_commands.append("G0 Z50") #为了homing，这里可以设置一个temp的坐标然后完成下一个点
    #     return gcode_commands

    # def one_time_logic(self, x, y):
    #     each_time_command = []
    #     each_time_command.append(f"G1 Z{50}") # this 50 is about to change to a pre-set value
    #     each_time_command.append(f"G1 X{x} Y{y}")


# 最重要的method
#     def area_test_logic(self):
#         # 1. Single point test at the centre
#         # 其实就是下面几个method的一个combination，不用单独为了centre做一个method
#         centre_x_coord = "50"
#         centre_y_coord = "50"
#         point2x = "40"
#         point2y = "40"
#         self.move_to_xy(centre_x_coord, centre_y_coord)
#         # 2. When test is done Lift to a safe z - position
#         self.move_to_safe_z()
#         # 3. Move to the next point (x&y) 这里有个绝对还是相对坐标的问题，是否需要归零？
#         # 这里的point2x和point2y后面需要从list里面导出来
#         self.move_to_xy(point2x,point2y)
#         # 4. Move to the surface again
#         self.move_to_surface()
#         # 5. Begin new test
#             # 往下increment，触发之后停止步进



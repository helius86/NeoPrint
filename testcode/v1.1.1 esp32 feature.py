#serESP32 = serial.Serial('COM4', 115200)
## current_data = (str(serESP32.readline())) # this has to be
#
#
#SinglePointsList.append([0, 0, None, None])
#point_index = 0
#current_dataType = 2
#
#while True:
#    current_data = (str(serESP32.readline()))
#    # print(current_data)
#    if current_data.startswith("b'"):
#        activatedForce = current_data.split(';')[1]  # records
#        activatedSignal = current_data.split(';')[0]
#    # activatedForce = current_data
#    # with open("results.txt", "w") as file1:
#    #     file1.write(activatedForce + '\n')
#
#    print(activatedForce)
#    print(activatedSignal)
#    if (activatedSignal == "b'1"):
#        SinglePointsList[point_index][current_dataType] = activatedForce
#        break

import sys
import time
import serial
import re
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, \
    QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QRadioButton
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction



''' 
Comment these out
'''
# location_data = ''


class TestWindow(QWidget):

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

    # def disconnect_esp(self):
    #     if self.ESPserial is not None:
    #         self.reader

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



    #def auto_increment(self):

    # while True:
    #    current_data = (str(serESP32.readline()))
    #    # print(current_data)
    #    if current_data.startswith("b'"):
    #        activatedForce = current_data.split(';')[1]  # records
    #        activatedSignal = current_data.split(';')[0]
    #    # activatedForce = current_data
    #    # with open("results.txt", "w") as file1:
    #    #     file1.write(activatedForce + '\n')
    #
    #    print(activatedForce)
    #    print(activatedSignal)
    #    if (activatedSignal == "b'1"):
    #        SinglePointsList[point_index][current_dataType] = activatedForce
    #        break


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
                            self.debug_monitor.append(f'activated force is: {activated_force}')




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

class SinglePointTestWindow(TestWindow):
    def init(self, parent=None):
        super().init(parent)

        # Add SinglePointTest-specific functionality here

class MultiPointTestWindow(TestWindow):
    def init(self, parent=None):
        super().init(parent)
        # Add MultiPointTest-specific functionality here

class ModeSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create dialog layout
        dialog_layout = QVBoxLayout(self)

        # Create form layout for mode selection
        form_layout = QFormLayout()
        dialog_layout.addLayout(form_layout)

        # Create radio buttons for mode selection
        self.single_point_radio = QRadioButton('SinglePointTest', self)
        self.multi_point_radio = QRadioButton('Multi-point test', self)
        form_layout.addRow(self.single_point_radio)
        form_layout.addRow(self.multi_point_radio)

        # Create OK and cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        dialog_layout.addWidget(button_box)

    def get_selected_mode(self):
        if self.single_point_radio.isChecked():
            return 'SinglePointTest'
        elif self.multi_point_radio.isChecked():
            return 'Multi-point test'
        else:
            return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial = None
        self.mode_select_dialog = None  # Initialize the dialog attribute to None

        self.init_ui()

    def init_ui(self):

        # Set the window icon
        self.setWindowIcon(QIcon('neil-icon.png'))



        # Show mode selection dialog
        mode_select_dialog = ModeSelectDialog(self)
        if mode_select_dialog.exec() == QDialog.DialogCode.Accepted:
            selected_mode = mode_select_dialog.get_selected_mode()
            if selected_mode == 'SinglePointTest':
                self.test_window = SinglePointTestWindow(self)
            elif selected_mode == 'Multi-point test':
                self.test_window = MultiPointTestWindow(self)
            else:
                # No mode selected, so quit the application
                sys.exit()

            self.setCentralWidget(self.test_window)

            # Create menu bar
            menu_bar = QMenuBar()
            self.setMenuBar(menu_bar)
            # Create file menu and "Quit" action
            file_menu = menu_bar.addMenu('File')
            quit_action = QAction('Quit', self)
            quit_action.setShortcut('Ctrl+Q')
            quit_action.triggered.connect(self.close)
            file_menu.addAction(quit_action)

            # Create mode menu and "Select Mode" action
            mode_menu = menu_bar.addMenu('Mode')
            select_mode_action = QAction('Select Mode', self)
            select_mode_action.triggered.connect(self.select_mode)
            mode_menu.addAction(select_mode_action)

            # Create "Location" menu and "Show Location" action
            location_menu = menu_bar.addMenu('Location')
            show_location_action = QAction('Show Location', self)
            show_location_action.triggered.connect(self.show_location)
            location_menu.addAction(show_location_action)

            # Create "Location" menu and "Show Location" action
            operation_menu = menu_bar.addMenu('Operation')
            action_homing = QAction('Homing', self)
            action_homing.triggered.connect(self.homing)
            operation_menu.addAction(action_homing)

            # Create "Location" menu and "Show Location" action
            location_menu = menu_bar.addMenu('Data Processing')
            data_processing = QAction('Single Point Test Result', self)
            data_processing.triggered.connect(self.data_processing_single)
            location_menu.addAction(data_processing)


        else:
            # No mode selected, so quit the application
            sys.exit()


        self.setWindowTitle('NeoPrint')
        self.resize(800, 400)


    # def homing(self):
    #     self.test_window.send_command('M114')

    def homing(self):
        self.test_window.send_command('G28')

    def data_processing_single(self):
        try:
            # Extract z value from debug monitor
            z_value = re.search(r'Z:(\d+\.\d+)', self.test_window.debug_monitor.toPlainText()).group(1)
            z_activation_distance = 50.00 - float(z_value)
        except AttributeError:
            print('Error: Unable to extract Z value from debug monitor')
            return

        try:
            # Extract activation force from debug monitor
            activated_force = re.search(r'activated force is: (-?\d+\.\d+)', self.test_window.debug_monitor.toPlainText()).group(1)
            #activated_force = float(activated_force), 2
        except AttributeError:
            print('Error: Unable to extract activated force from debug monitor')
            activated_force = 'N/A'

        # SPT - Single Point Test

        #SPT_window = SinglePointTestResultWindow(self, z_activation_distance, activated_force)
        #SPT_window.exec()

        print("Creating SPT_window")
        SPT_window = SinglePointTestResultWindow(self)
        print("Showing SPT_window")
        SPT_window.set_values(z_activation_distance, activated_force)
        print("Window opened")
        SPT_window.exec()

    def show_location(self):

        # I changed the location data to test data
        z_value = re.search(r'Z:(\d+\.\d+)', self.test_window.debug_monitor.toPlainText()).group(1)

        #print(z_value)
        location_window = LocationWindow(self, self.test_window.debug_monitor.toPlainText())
        location_window.exec()

    def select_mode(self):
        if self.mode_select_dialog is None:
            self.mode_select_dialog = ModeSelectDialog(self)
        else:
            if self.mode_select_dialog.isVisible():  # Check if the dialog is currently visible
                self.mode_select_dialog.reject()  # Close the dialog if it's visible
            self.mode_select_dialog = ModeSelectDialog(self)
        mode = self.mode_select_dialog.exec()
        if mode == QDialog.DialogCode.Accepted:
            selected_mode = self.mode_select_dialog.get_selected_mode()
            if selected_mode == 'SinglePointTest':
                self.setWindowTitle('NeoPrint - Single Point Test')
                # Add code for setting up SinglePointTest window
            elif selected_mode == 'Multi-point test':
                self.setWindowTitle('NeoPrint - Multi-point test')
                # Add code for setting up Multi-point test window


class SinglePointTestResultWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create layout
        layout = QVBoxLayout(self)

        # Create labels for the values and units
        self.distance_label = QLabel()
        self.distance_unit_label = QLabel('mm')
        self.force_label = QLabel()
        self.force_unit_label = QLabel('g')

        # Add labels to layout
        layout.addWidget(QLabel('Activation distance:'))
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(self.distance_label)
        distance_layout.addWidget(self.distance_unit_label)
        layout.addLayout(distance_layout)

        layout.addWidget(QLabel('Activation force:'))
        force_layout = QHBoxLayout()
        force_layout.addWidget(self.force_label)
        force_layout.addWidget(self.force_unit_label)
        layout.addLayout(force_layout)

        self.setWindowTitle('Single Point Test')
        self.resize(200, 100)  # set maximum width and height

    def set_values(self, distance, force):
        try:
            # Convert distance and force to floats and round them to two decimal places
            distance = round(float(distance), 2)
            force = round(float(force), 2)

            # Set the values of the labels
            self.distance_label.setText(str(distance))
            self.force_label.setText(str(force))
        except Exception as e:
            print(f"Error: set_value method failed: {e}")


class LocationWindow(QDialog):

    # Changed the constructor to receive test data
    def __init__(self, parent=None, test_data=''):
        super().__init__(parent)
        self.setWindowTitle('Location Data')
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout(self)

        label = QLabel('Location Data:')
        layout.addWidget(label)


        # Use test data to create the label
        test_label = QLabel(test_data)
        layout.addWidget(test_label)

        # self.location_label = QLabel(location_data)
        # layout.addWidget(self.location_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setModal(True)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

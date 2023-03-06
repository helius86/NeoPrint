import sys
import time
import serial
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, \
    QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QRadioButton
from PyQt6.QtCore import QTimer

from PyQt6.QtGui import QAction

location_data = ''
class TestWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.serial = None
        self.location = None  # Initialize location variable
        self.location_lock = threading.Lock()

        self.init_ui()

    def init_ui(self):
        # Create central widget and main layout
        main_layout = QVBoxLayout(self)

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
        main_layout.addLayout(button_layout)

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

        # Combine all layouts into main layout
        main_layout.addLayout(port_baud_layout)

        # Create send layout
        send_layout = QHBoxLayout()
        send_label = QLabel('Send:')
        send_layout.addWidget(send_label)
        self.send_edit = QTextEdit()
        self.send_edit.setMaximumHeight(80) # set maximum height to 50 pixels
        send_layout.addWidget(self.send_edit)
        self.send_button = QPushButton('Send')
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send)
        send_layout.addWidget(self.send_button)
        main_layout.addLayout(send_layout)

        # Create receive layout
        receive_layout = QHBoxLayout()
        receive_label = QLabel('Receive:')
        receive_layout.addWidget(receive_label)
        self.debug_monitor = QTextEdit()
        self.debug_monitor.setMaximumHeight(100) # set maximum height to 50 pixels
        self.debug_monitor.setReadOnly(True)
        receive_layout.addWidget(self.debug_monitor)
        main_layout.addLayout(receive_layout)

        self.setWindowTitle('NeoPrint')
        self.resize(800, 400)

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
            self.test_button.setEnabled(False)  # Disable the Test button

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

    def send_gcode(self):
        button_model = self.button_combo.currentText()
        if button_model == 'Button Profile 1':
            filename = 'button1.gcode'
        else:
            filename = 'button2.gcode'
        with open(filename, 'r') as f:
            for line in f:
                self.send_edit.setText(line.strip())
                self.send()
                time.sleep(0.01)  # Add a small delay between sending each line

    def extract_location_info(self, response):
        location_start = response.find('X:')
        if location_start != -1:
            location_end = response.find(' ', location_start)
            location_str = response[location_start:location_end]
            location_dict = dict([pair.split(':') for pair in location_str.split()])
            return location_dict
        else:
            return {1}

    def read_serial(self):
        global location_data
        self.reader_running = True
        while self.reader_running:
            if self.serial is not None:
                response = ''
                while self.serial.inWaiting() > 0:
                    response += self.serial.read(self.serial.inWaiting()).decode()
                if 'X:0.00 Y:0.00 Z:0.00 E:0.00 Count X:0 Y:0 Z:0' in response:
                    location_data = response
                    with self.location_lock:
                        self.location = response
                        print(f"Location: {self.location}")
                    self.debug_monitor.append(response)

                time.sleep(0.01)

    def get_location(self):
        return self.location
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



        else:
            # No mode selected, so quit the application
            sys.exit()


        self.setWindowTitle('NeoPrint')
        self.resize(800, 400)

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




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

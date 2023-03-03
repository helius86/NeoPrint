import sys
import time
import serial
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, \
    QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QMenuBar
from PyQt6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial = None

        self.init_ui()

    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create menu bar
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Create file menu and "Quit" action
        file_menu = menu_bar.addMenu('File')
        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

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

        self.setCentralWidget(central_widget)
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
        self.debug_monitor.append(response) # This is where the debug_monitor is connected to the serial readback

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
                #time.sleep(0.01)  # Add a small delay between sending each line

    def read_serial(self):
        self.reader_running = True  # Set the flag to indicate the thread is running
        while self.reader_running:
            if self.serial is not None:
                response = ''
                while self.serial.inWaiting() > 0:
                    response += self.serial.read(self.serial.inWaiting()).decode()
                if response != '':
                    self.debug_monitor.append(response)

            # Sleep for a short time to avoid high CPU usage
            time.sleep(0.01)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

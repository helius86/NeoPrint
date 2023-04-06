import sys
import time
import threading
import serial
import re
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QComboBox, \
    QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QMenuBar, QDialog, QDialogButtonBox, QFormLayout, QRadioButton, QMenu
from mode_window_layout import SingleModeWindow, AreaModeWindow


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
        #self.AreaClass = AreaModeWindow()
        #self.serial = self.AreaClass.serial
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
                self.test_window = SingleModeWindow(self)
            elif selected_mode == 'Multi-point test':
                self.test_window = AreaModeWindow(self)
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

            areadata_processing = QAction('Single Point Test Result', self)
            areadata_processing.triggered.connect(self.data_processing_area)
            location_menu.addAction(areadata_processing)


        else:
            # No mode selected, so quit the application
            sys.exit()


        self.setWindowTitle('NeoPrint')
        self.resize(1200, 900)

    def homing(self):
        #self.test_window.send_command('G28')
        try:
            #self.AreaClass.send_single_gcode("G28\n")
            print("1")
        except Exception as e:
            print(f"Error: {e}")

    def data_processing_area(self):
        return


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
                self.test_window = SingleModeWindow(self)
                self.setCentralWidget(self.test_window)

                # Add code for setting up SinglePointTest window
            elif selected_mode == 'Multi-point test':
                self.setWindowTitle('NeoPrint - Multi-point test')
                self.test_window = AreaModeWindow(self)
                self.setCentralWidget(self.test_window)
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


class AreaModeResultWindow(QDialog):
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
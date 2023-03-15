from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QMessageBox
import sys


class Window(QWidget):
    test_done = 1
    def __init__(self):
        super().__init__()
        self.resize(300, 250)
        self.setWindowTitle("CodersLegacy")
        #test_done = 1
    def test_done_dialog(self):
        dialog = QMessageBox(parent=self)
        dialog.setWindowTitle("Test Completed")
        dialog.setText("The test is done. Now you can go to data processing.")
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes)
        dialog.exec()


app = QApplication(sys.argv)
window = Window()
window.show()
if(Window.test_done):
        test_done_dialog()
sys.exit(app.exec())
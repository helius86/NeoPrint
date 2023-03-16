# This file defines the function for both single-point-mode and area-mode
# such as connect, disconnect, send etc.

class GeneralFunction:
    def __init__(self, parent=None):
        super().__init__()

    def general_function(self):
        def send_M114(self):
            self.serial.write(b'M114')  # Send M114 separately to the 3D printer


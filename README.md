# README

# NeoPrint

## Introduction

NeoPrint is an application developed to test a cylindrical assistive switch based on a modified 3D printer. It includes two Python files, `main.py` and `single_mode_window.py`, that work together to allow users to perform single-point and multi-point tests on the switch.

## Dependencies

- Python 3
- PyQt6
- numpy

## Getting Started

 1) Download the files inside `NeoPrint` directory.
 2) Install a Python IDE   eg. [Pycharm](https://www.jetbrains.com/pycharm/download/#section=windows)
 3) Run `main.py`
 4) Install libraries and dependencies as prompted in the console

This will launch the main window of the application, which includes a mode selection dialog. Users can choose between single-point and multi-point tests by selecting the appropriate radio button and clicking the "OK" button.

## Features

### Mode Selection

The mode selection dialog allows users to choose between single-point and multi-point tests.

### Single-Point Test

The single-point test window allows users to test an arbitrary point on the switch. The user can initiate the test by pressing the "Activate" button. After the test is complete, the application will display the activation distance and force required to activate the switch.

### Multi-Point Test

The multi-point test window allows users to autogenerate and test multiple points on the switch. 

The user has the option to generate points that form equidistant rings around the switch by specifying the number of rings (up to 7), or generate points that are equidistant from each other by specifying the number of points (up to 99).  

The user can see the generated test points by clicking the "Generate" button. 

The user can initiate the test by pressing the "Test" button. After the test is complete, the application will display 2 heatmaps, showing: 
   - the actuation distance at each point 
   - the actuation force at each point
  
See examples of the generated test points and heatmap in the `Examples` directory. 

## Known Issues

- None

## Future Enhancements

- Improved UI design
- Additional testing features

## Credits

- Developed by UBC 2023 Capstone team CG-65
- Corporate client: Neil Squire

## License

This project is licensed under **GNU General Public License v3.0**

NeoPrint is free software: you are allowed to redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

NeoPrint is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with NeoPrint. If not, please visit **[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)** to obtain a copy.

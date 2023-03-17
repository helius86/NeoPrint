import math
#from mode_window_layout import AreaModeWindow

class AreaModeFunc:
    def __init__(self, parent=None):
        super().__init__()

        self.point_coords = None


    def generateTestpoints(self, radius_button, numPoints):
        radius = radius_button - 0.1  # so the very edge is not pressed
        points = []
        points.append([0, 0, None, None])
        boundary = math.sqrt(numPoints)
        phi = (math.sqrt(5) + 1) / 2

        for k in range(1, numPoints):
            if (k > numPoints - boundary):
                r = radius
            else:
                r = radius * math.sqrt(k - 1 / 2) / math.sqrt(numPoints - (boundary + 1) / 2)

            angle = k * 2 * math.pi / phi / phi
            curr_x = r * math.cos(angle)
            curr_y = r * math.sin(angle)
            points.append([round(curr_x, 2), round(curr_y, 2), None, None])
        self.point_coords = points
        return points

    def print_points(self):
        if self.point_coords:
            for point in self.point_coords:
                print(point)
        else:
            print("No points generated yet")

    def generate_gcode(self, points, safe_z_height=5):
        """
        Generate G-code commands to probe a list of points.

        :param points: List of points in the format [[x1, y1, None, None], [x2, y2, None, None], ...]
        :param safe_z_height: The safe Z height for travel moves (default: 5)
        :return: List of G-code commands
        """
        # Initialize an empty list to store the G-code commands
        gcode_commands = []
        # Add a G28 command to home all axes before starting the probing process
        gcode_commands.append("G28")
        for point in points:
            x, y = point[0], point[1]
            # Move the probe up to the safe Z height
            gcode_commands.append(f"G1 Z{safe_z_height}")
            # Move the probe to the XY coordinates of the testing point
            gcode_commands.append(f"G1 X{x} Y{y}")
            # Add the G30 command to perform a single Z-probe at the current XY position
            gcode_commands.append("G30")
        # Add a G28 command to home all axes after completing the probing process
        gcode_commands.append("Gxx") #为了homing，这里可以设置一个temp的坐标然后完成下一个点
        return gcode_commands






# 最重要的method
    def area_test_logic(self):
        # 1. Single point test at the centre
        # 其实就是下面几个method的一个combination，不用单独为了centre做一个method
        centre_x_coord = "50"
        centre_y_coord = "50"
        point2x = "40"
        point2y = "40"
        self.move_to_xy(centre_x_coord, centre_y_coord)
        # 2. When test is done Lift to a safe z - position
        self.move_to_safe_z()
        # 3. Move to the next point (x&y) 这里有个绝对还是相对坐标的问题，是否需要归零？
        # 这里的point2x和point2y后面需要从list里面导出来
        self.move_to_xy(point2x,point2y)
        # 4. Move to the surface again
        self.move_to_surface()
        # 5. Begin new test
            # 往下increment，触发之后停止步进



# 底下都是工具method
    def move_to_xy(self, x_coord, y_coord):
        gcode = f'G1 X{x_coord} Y{y_coord}\n'
        self.send_single_gcode(gcode)
    def move_to_surface(self):
        # 这里先用一个固定的z值，后面再开发从button profile引出这个不同z值的功能
        self.send_single_gcode("G1 Z50")
    def send_single_gcode(self, gcommand):
        # gcommand form should be 'G91\n'
        AreaModeWindow.serial.write(gcommand.encode())
    def move_to_safe_z(self):
        # 这里先用一个固定的z值，后面再开发从button profile引出这个不同z值的功能
        self.send_single_gcode("G1 Z60")








mode_func = AreaModeFunc()
points = [
    [0, 0, None, None],
    [-1.04, 0.95, None, None],
    [0.21, -2.42, None, None]
]

gcode_commands = mode_func.generate_gcode(points)

# Print the generated G-code commands
for command in gcode_commands:
    print(command)


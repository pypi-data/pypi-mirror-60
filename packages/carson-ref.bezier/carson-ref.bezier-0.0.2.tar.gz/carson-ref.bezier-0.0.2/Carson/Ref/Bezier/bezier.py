from .pkg.mathHelper import ncr
from .pkg.yamlHelper import *
import numpy as np
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backend_bases import MouseButton
from typing import NewType, Any

T_AxesSubplot = NewType('T_AxesSubplot', Any)
NUMBER_OF_T: int = 10


class BezierBuilder:
    """
    Bezier curve interactive builder.
    """
    __slots__ = ('xp', 'yp',
                 'control_polygon', 'other_control_points',
                 'bezier_curve', 'other_bezier_curve',
                 'ax_points', 'ax_bezier',
                 'canvas',)

    def __init__(self, control_polygon: Line2D,
                 ax_points: T_AxesSubplot):
        """Constructor.
        Receives the initial control polygon of the curve.
        """
        self.control_polygon = control_polygon
        self.other_control_points = Line2D([], [], ls='--', c='#FFFF00', marker='o', mew=2, mec='#00FFFF')
        self.xp = list(control_polygon.get_xdata())
        self.yp = list(control_polygon.get_ydata())

        self.ax_points = ax_points
        self.ax_bezier = control_polygon.axes  # let bezier points on control_polygon
        self.ax_bezier.add_line(self.other_control_points)  # # let other control points on control_polygon
        if 'Create Bezier curve':
            line_bezier = Line2D([], [],
                                 c=control_polygon.get_markeredgecolor())  # same as control_polygon.markeredgecolor

            self.bezier_curve = self.ax_bezier.add_line(line_bezier)

            other_bezier_line = Line2D([], [], ls='--', c='#FF00FF')
            self.other_bezier_curve = self.ax_bezier.add_line(other_bezier_line)
        self.canvas = control_polygon.figure.canvas  # this canvas control polygon and bezier curve.

        # Event handler for mouse clicking
        # self.canvas.mpl_connect('button_press_event', self)
        self.canvas.mpl_connect('button_press_event', self.on_click_mouse_button)  # return int (cid)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)  # return int (cid)

    def on_key_press(self, event):
        key = event.key.upper()
        if key == 'ESCAPE':
            exit()
        if key == 'C':  # clear
            self.xp = []
            self.yp = []

            self.other_control_points.set_data([], [])
            self.other_bezier_curve.set_data([], [])  # unzip tuple

            event.button = MouseButton.LEFT
            self.on_click_mouse_button(event, is_init=True)

    # def __call__(self, event):
    def on_click_mouse_button(self, event, **option):
        # Ignore clicks outside axes
        if event.inaxes != self.control_polygon.axes:
            return

        button = event.button
        if button != MouseButton.LEFT:
            return

        # Add point
        if not option.get('is_init'):
            self.xp.append(event.xdata)
            self.yp.append(event.ydata)
        self.control_polygon.set_data(self.xp, self.yp)

        # Rebuild Bezier curve and update canvas
        all_tuple_bezier_points = self._build_bezier()
        self.bezier_curve.set_data(*all_tuple_bezier_points)  # unzip tuple

        if 'test bezier 3 to 2' and len(self.xp) == 4:
            xy = self.bezier_n_1_to_n([(x, y) for x, y in zip(self.xp, self.yp)])
            bezier2_xp = list(xy[:, 0])
            bezier2_yp = list(xy[:, 1])

            self.other_control_points.set_data(bezier2_xp, bezier2_yp)

            all_tuple_bezier_points = BezierBuilder.build_bezier(bezier2_xp, bezier2_yp)
            self.other_bezier_curve.set_data(*all_tuple_bezier_points)  # unzip tuple

        # plt.plot([x], [y], marker='o', markersize=3, color="red")
        self._update_points(all_tuple_bezier_points, is_init=option.get('is_init', False))
        self._update_bezier()  # canvas.draw will call plt.show command, so it should put last.

    def _build_bezier(self) -> tuple:
        x, y = bezier(list(zip(self.xp, self.yp)), number_of_t=NUMBER_OF_T).T
        return x, y

    @staticmethod
    def build_bezier(list_x, list_y):
        x, y = bezier(list(zip(list_x, list_y)), number_of_t=NUMBER_OF_T).T
        return x, y

    def _update_bezier(self):
        """
        Update polygon and bezier curve
        """

        """
        ax.set_title("Bernstein basis, N = {}".format(N))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        """
        self.canvas.draw()

    def _update_points(self, all_tuple_bezier_points: tuple, **option):
        # self.ax_points.clear()  # will remove title
        title = self.ax_points.get_title()
        self.ax_points.cla()  # which clears data but not axes
        # self.ax_points.clf()  # which clears data and axes
        self.ax_points.set_title(title)
        if not option.get('is_init', False):
            self.ax_points.plot(*all_tuple_bezier_points, ls='--', marker='o', markersize=3, color="red")

    @staticmethod
    def _get_reduction_matrix(n: int) -> np.array:
        """
        :param n: number of points
        :return:
        """
        matrix = np.zeros((n + 1, n), dtype=float)
        upper = 1
        for row in range(matrix.shape[1]):
            matrix[row][row] = upper - row / n

        for row in range(1, matrix.shape[0]):
            matrix[row][row - 1] = row / n
        return matrix

    @staticmethod
    def bezier_n_1_to_n(points: list, fixed_start_and_end_flag=False):
        """
        n+1 - > n
        :param points: means: n+1
        :param fixed_start_and_end_flag:
        """
        m = BezierBuilder._get_reduction_matrix(len(points) - 1)
        result = np.linalg.inv((m.T @ m)) @ m.T @ np.array(points)
        if fixed_start_and_end_flag:
            result[0] = points[0]
            result[-1] = points[-1]
        return result


def bezier_coefficient(n_degree: int, k: int):
    """
    one points
    """

    def _fun(t, check_on: bool = False):
        if check_on:
            if isinstance(t, (int, float)):
                assert 0 <= t <= 1, f"it's not correctly of the input parameter of t. t={t}"
            elif isinstance(t, (list, np.ndarray)):
                assert all([0 <= val <= 1 for val in t]), f"it's not correctly of the input parameter of t. t={t}"
        return ncr(n_degree, k) * (1 - t) ** (n_degree - k) * t ** k
    return _fun


def bezier(points: list, number_of_t) -> np.ndarray:
    """
    Build Bezier curve from points.
    """

    n = len(points)
    t = np.linspace(0, 1, num=number_of_t)  # shape: number_of_t. that are likely list
    xy_bezier_points = np.zeros((number_of_t, 2), dtype=float)
    for k in range(n):  # calculate all the points, and calculate one at one time.
        xy_bezier_points += np.outer(bezier_coefficient(n-1, k)(t), points[k])
    return xy_bezier_points


def bezier_curve_monitor(config_path: Path = Path(__file__).parent / 'config/config.yaml'):
    matplotlib.use('webagg')
    with open(str(config_path), 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    dict_config = config.get(Path(__file__).stem.upper())
    if dict_config is None:
        raise ImportError(f'{config_path}')
    global NUMBER_OF_T
    input_image = dict_config['DEFINE']['IMAGE']
    input_bezier = dict_config['DEFINE']['BEZIER']
    max_row_of_image = input_image['max_row_of_image']
    max_col_of_image = input_image['max_col_of_image']
    img_width, img_height = eval(input_image['img_size'])  # PER IMAGE

    NUMBER_OF_T = input_bezier['number_of_t']

    # Initial setup
    fig, (ax_bezier, ax_points) = plt.subplots(max_row_of_image, max_col_of_image,
                                               figsize=(img_width * max_col_of_image, img_height * max_row_of_image))

    # Empty line
    line = Line2D([], [], ls='--', c='#666666',
                  marker='x', mew=2, mec='#204a87')
    ax_bezier.add_line(line)

    # Canvas limits
    ax_bezier.set_xlim(0, 1)
    ax_bezier.set_ylim(0, 1)
    ax_bezier.set_title("Bezier curve")

    # Bernstein plot
    ax_points.set_title("Bernstein basis")

    # Create BezierBuilder
    BezierBuilder(line, ax_points)

    plt.show()


if __name__ == '__main__':
    bezier_curve_monitor()

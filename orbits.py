"""
Simulates Newtonian orbital dynamics by iterating through Newton's equation
for the force of gravity:

            F_g = G*m_1*m_2/r^2

By the following quick derivation:

    F_x/|F| = −x/r
    F_x = −|F|*x/r
    F_x = −G*m_1*m_2/r^2 * x/r
    F_x = -G*m_1*m_2*x/r^3

This comes about since "we see that the horizontal component of the force is
related to the complete force in the same manner as the horizontal distance x is
to the complete hypotenuse r, because the two triangles are similar. Also, if x
is positive, F_x is negative." (http://www.feynmanlectures.caltech.edu/I_09.html)

We also have the relation that r = sqrt(x^2 + y^2) for a 2D system. To find the
force on an object i created by all other forces, we have:

        F_i = sum_j=1^N(-G*m_i*m_j(x_i - x_j)/r^3)
    m_i*a_i = sum_j=1^N(-G*m_i*m_j(x_i - x_j)/r^3)
        a_i = sum_j=1^N(-G*m_j(x_i - x_j)/r^3)
        a_i = -G * sum_j=1^N(m_j(x_i - x_j)/r^3)

The only difference from above is that the x becomes a measure of distance
between the two objects and the acceleration vector x-component is a sum of the
effects of every object on object i. And it is analogous for the y-component
(and any other if you wish to be higher dimensional).

The simulation is ran in Qt and that's pretty much it!
"""


import sys
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union

import matplotlib.colors as mpl_colors
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QKeySequence, QPainter, QPaintEvent, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass
class Body:
    """
    All data for each celestial body
    """

    mass: float
    pos: Tuple[float, float]
    vel: Tuple[float, float]
    body_color: Optional[str] = None
    line_color: Optional[str] = None
    show_path: bool = True
    centered: bool = False


def is_float(element: Any) -> bool:
    """Checks if `element` can be cast as a float"""
    try:
        float(element)
        return True
    except ValueError:
        return False


class Orbit:
    """
    Models Newtonian dynamics numerically and discretely of the graviational
    attraction and subsequent effect of such on various objects (think
    planets)

    Parameters:
    objs - An arbitrary number of objects' data given as dictionaries of their
           masses, velocities and positions and other details:

                {'mass': 10, 'pos': [1, 5], 'vel':[3, 0], 'show_path':True,
                 'centered':True, 'body_color': 'green', 'line_color': blue'}

            mass - The mass of the object
            pos - The (x,y) starting position of the object
            vel - The (x,y) starting velocity of the object
            show_path - (default True) Shows the line path of the object if
                True, otherwise doesn't display the line
            centered - (default False) Will center the image on the object, i.e.
                the object won't move. If more than one object has this keyword
                set to True, then it will be centered on their average position
            body_color - (default black) The color of the body
            line_color - (default `body_color`) The color of the path line, defaults
                to whatever color the ball is

    G - (default 1) The value for the graviational constant found in Newton's
        equation for the force from gravity
    dt - (default 0.01) The time interval, how much time passes between each
         calculation of the positions and velocities. Lower is more accurate.
    """

    def __init__(self, objs: Sequence[Body], G: float, dt: float):
        self.G = G
        self.dt = dt
        self.offset = [0.0, 0.0]

        # Index of dicts that is to have orbits centered on
        self.cinds: Optional[List[int]]
        self.cinds = [
            objs.index(obj) for obj in filter(lambda x: x.centered is True, objs)
        ]

        # Arrays with dimension (no. objects, no. dimensions)
        self.pos = np.array([obj.pos for obj in objs], dtype="float128")
        self.vel = np.array([obj.vel for obj in objs], dtype="float128")
        self.mass = np.array([obj.mass for obj in objs])
        self.dim = len(self.pos[0])

        # Make sure consistent number of objects between pos and vel
        if len(self.pos) != len(self.vel):
            raise Exception(
                "Different number of objects for position and velocity lists."
            )
        self.num_objects = len(self.pos)

        # Make sure consistent number of dimensions across pos and vel
        if not all(
            [
                len(self.pos[obj]) == len(self.vel[obj])
                for obj in range(self.num_objects)
            ]
        ):
            raise Exception("Different number of dimensions for velocity and position.")
        self.num_dims = len(self.pos[0])

    def find_new_acc(self) -> Sequence[Sequence[float]]:
        """
        Given data on position and velocity of all objects, the resulting
        acceleration of each object due to every other object can be found with
        the following equation:

                a_i = -G * sum_j=1^N(m_j(x_i - x_j)/r^3)

        This is for the x-direction but is analogous for any other axis. Here,
        a_i is the acceleration for the ith object for the specific axis, the
        sum is over all of the N objects and r is the euclidean distance between
        the ith and jth object.
        """
        new_acc = [[0.0] * self.num_dims] * self.num_objects
        # Iterate through each object
        for oind in range(self.num_objects):
            # Initialize the accelerations for each dimension
            tot_acc = [0] * self.num_dims

            # Iterate through the other objects
            for eind in range(self.num_objects):
                # Skip itself
                if oind == eind:
                    continue

                # Find r^3 as shown above in the equation
                dist_cubed = (
                    np.sqrt(
                        sum(
                            [
                                (self.pos[oind][dim] - self.pos[eind][dim]) ** 2
                                for dim in range(self.num_dims)
                            ]
                        )
                    )
                    ** 3
                )

                # Iterate through each dimension
                for dind in range(self.num_dims):
                    # Tack on total for each accerleration component
                    tot_acc[dind] += (
                        self.mass[eind]
                        * (self.pos[oind][dind] - self.pos[eind][dind])
                        / dist_cubed
                    )

            # Multiply on the constants to the sum
            new_acc[oind] = [-self.G * acc for acc in tot_acc]

        return new_acc

    def update_objects(self, acc: Sequence[Sequence[float]]) -> None:
        """
        With acceleration data, the velocity and position vectors for each
        object is updated in-place.
        """
        for oind in range(self.num_objects):
            for dind in range(self.num_dims):
                self.vel[oind][dind] += acc[oind][dind] * self.dt
                self.pos[oind][dind] += self.vel[oind][dind] * self.dt

        if len(self.cinds):
            # Takes the average of each coordinate of objs with centered=True so that
            # the centered point is the average of all of them. For example, if there
            # is a binary system, you can center on the COM of the binary.
            self.offset = list(
                map(
                    lambda x: sum(x) / len(x),
                    [
                        [
                            coord[ind]
                            for coord in [self.pos[cind] for cind in self.cinds]
                        ]
                        for ind in range(self.dim)
                    ],
                )
            )
        else:
            self.offset = self.dim * [0.0]

    def iterate(self) -> None:
        """
        Goes through one 'iteration' where each takes a total time of dt. Since
        this is a discretized version of Newtonian dynamics, it will be more
        accurate the lower dt is.
        """
        new_acc = self.find_new_acc()
        self.update_objects(new_acc)


class Window(QMainWindow):
    """
    Main window contains the menubar and the central widget for the simulation.
    All parameters are for Foreground and Background classes

    Parameters:
    default_color (default black) - Only one not passed on. The default color
        of the objects if no color is specified.
    G, dt, width, height, obj_size, scale_coeff - See Foreground class
    """

    def __init__(
        self,
        objs: Sequence[Body],
        default_color: str = "black",
        G: Union[float, int] = 1.0,
        dt: Union[float, int] = 0.00005,
        width: int = 500,
        height: int = 500,
        obj_size: float = 5,
        scale_coeff: float = 1.5,
        parent=None,
    ):
        super().__init__(parent=parent)
        self._create_menubar()
        self.setWindowTitle("Newtonian Orbital Dynamics")
        self.setGeometry(300, 200, width, height)
        self._place_new_body = False
        self.width = width
        self.height = height

        self.picture = Picture(
            objs,
            default_color=default_color,
            G=float(G),
            dt=float(dt),
            width=width,
            height=height,
            obj_size=obj_size,
            scale_coeff=scale_coeff,
            parent=self,
        )
        self.setCentralWidget(self.picture)

    def _create_menubar(self) -> None:
        """
        Menu for the main window.
        """
        file = self.menuBar().addMenu("File")
        self.file_pause = file.addAction("Pause Simulation")
        self.file_pause.triggered.connect(self._toggle_pause)
        self.file_pause.setShortcut(Qt.Key_Space)

        edit = self.menuBar().addMenu("Edit")
        edit_dt = edit.addAction("Change time")
        edit_dt.setShortcut(QKeySequence("Ctrl+T"))
        edit_dt.triggered.connect(lambda: self._edit_val("dt", "time"))
        edit_G = edit.addAction("Change gravity")
        edit_G.setShortcut(QKeySequence("Ctrl+G"))
        edit_G.triggered.connect(lambda: self._edit_val("G", "gravity"))
        edit_add = edit.addAction("Add Body")
        edit_add.setShortcut(QKeySequence("Ctrl+A"))
        edit_add.triggered.connect(self._add_body)

    def _edit_val(self, attr: str, name: str) -> None:
        """
        Abstract method to change the value of attribute `attr`
        in the Orbit class. The value `name` is the string to use
        to describe it in the Popup window. The new value for the 
        attribute is given in the QLineEdit `self.new_val` of the
        Popup class. Currently being used for `dt` and `G`.
        """
        popup = ChangeValue(
            f"New {name.capitalize()} Value",
            self._change_val,
            val=getattr(self.picture.foreground.orbit, attr),
            attr=attr,
            parent=self,
        )
        popup.setGeometry(350, 250, 300, 100)
        popup.show()

    def _change_val(self, attr: str, new_val: Union[str, float, int]) -> None:
        """
        Method called when the QPushButton `self.accept` is clicked
        in the Popup class. Changes the value of the attribute `attr`
        of the Orbit class to `new_val`.
        """
        setattr(self.picture.foreground.orbit, attr, float(new_val))

    def _toggle_pause(self) -> None:
        """
        Pause and unpause the simulation.
        """
        if self.picture.timer.isActive():
            self.picture.timer.stop()
            self.file_pause.setText("Unpause Simulation")
        else:
            self.picture.timer.start()
            self.file_pause.setText("Pause Simulation")

    def _add_body(self) -> None:
        """
        Places a new body into the simulation.
        """
        popup = AddBody(self._setup_new_body_placement, self)
        popup.setGeometry(350, 250, 400, 300)
        popup.show()

    def _setup_new_body_placement(self, vel: Tuple[float], mass: float) -> None:
        """
        Records info for new body from popup and primes next mouse click to place.
        """
        self.new_obj_vel = vel
        self.new_obj_mass = mass
        self._place_new_body = True

    def mousePressEvent(self, evt):
        """
        Place new body on mouse down press if `self._place_new_body=True`.
        """
        if self._place_new_body:
            new_obj_pos = (evt.x(), evt.y())
            self._place_new_body = False

            foreground = self.picture.foreground
            background = self.picture.background
            orbit = foreground.orbit

            # Add new info
            foreground.body_colors.append("black")
            background.line_colors.append("black")
            background.show_paths.append(False)
            orbit.vel = np.append(orbit.vel, [self.new_obj_vel], axis=0)
            orbit.mass = np.append(orbit.mass, self.new_obj_mass)
            orbit.num_objects += 1

            # Scale from pixel coordinates to object coordinates
            x = foreground._inverse_scale(new_obj_pos[0], 0, 1.01)
            y = foreground._inverse_scale(new_obj_pos[1], 1, 1.06)
            orbit.pos = np.append(orbit.pos, [[x, y]], axis=0)

            # Remove these variables
            del self.new_obj_vel
            del self.new_obj_mass


class Picture(QWidget):
    """
    Widget which contains the simulation (the Foreground and Background classes).
    All parameters are for Foreground and Background classes

    Parameters:
    G, dt, width, height, obj_size, scale_coeff - See Foreground class
    """

    def __init__(
        self,
        objs: Sequence[Body],
        default_color: str,
        G: float,
        dt: float,
        width: int,
        height: int,
        obj_size: float,
        scale_coeff: float,
        parent,
    ):
        super().__init__(parent=parent)
        # Fill in default colors
        for obj in objs:
            if obj.body_color is None:
                obj.body_color = default_color
            if obj.line_color is None:
                obj.line_color = obj.body_color
        # Used to save previous position tuples to draw next pixel in Background
        self.orbital_prev: List[Tuple[float, float]] = []

        self.foreground = Foreground(
            objs,
            G=G,
            dt=dt,
            width=width,
            height=height,
            obj_size=obj_size,
            scale_coeff=scale_coeff,
            parent=self,
        )
        self.background = Background(width=width, height=height, parent=self)

        # Makes a list of the colors for each object
        self.background.line_colors = [obj.line_color for obj in objs]
        self.foreground.body_colors = [obj.body_color for obj in objs]

        # Makes a list of whether or not to show the path for each object
        # Check to make sure every input for `show_path` is either a boolean or an empty string
        osp = [obj.show_path for obj in objs]
        if not len(list(filter(lambda x: type(x) == bool, osp))) == len(osp):
            raise Exception("Unknown data type for show_path parameter.")
        self.background.show_paths = osp

        # Update every N milliseconds
        self.timer = QTimer()
        self.timer.timeout.connect(self._multi_update)
        self.timer.start(5)

    def _multi_update(self) -> None:
        """Moves everything forward"""
        self.foreground.update()
        self.background.paintEvent()
        self.update()

    def paintEvent(self, evt: QPaintEvent) -> None:
        """Paints the background, i.e. paths, to window"""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.background)
        painter.end()


class Background(QPixmap):
    """
    The background of the animation along with the paths. Since the foreground
    repaints everything everytime, painting the the paths would become more and
    more cumbersome. For n objects, after m calculations, there would be
    n^m points to paint but with this, it's just 2n points.
    """

    def __init__(self, width: int, height: int, parent: Window):
        QPixmap.__init__(self, width, height)
        self.parent = parent
        # Background color
        self.fill(QColor(200, 200, 200))

    def paintEvent(self) -> None:
        # QPixmap doesn't have a paintEvent, this is just a mocked-up version
        painter = QPainter(self)
        for n, orbit in enumerate(self.parent.orbital_prev):
            # Use `False` explicitly sign empty string is considered `True`
            if self.show_paths[n] is not False:
                color = QColor(mpl_colors.cnames[self.line_colors[n]])
                painter.setPen(color)
                painter.drawPoint(*[int(x) for x in orbit])
        painter.end()


class Foreground(QWidget):
    """
    Displays the simulation of the orbits in a Qt Widget by painting each frame
    with QPainter and being refreshed via an internal timer.

    Parameters:
    objs - The arbitrary number of objects to be passed to the Orbit class.
    G - The value for the gravitational constant to be passed to the Orbit class.
    dt - The time interval to be passed to the Orbit class.
    height - Height of the widget
    width - Width of the widget
    obj_size - The size of the shape representing the body
    scale_coeff - The scale of the simulation. The x and y limit will
        be at the maximum absolute distance from the center (in either x and y) multiplied
        by `scale_coeff`.
    parent - Parameter for the inherited QWidget class.
    """

    def __init__(
        self,
        objs: Sequence[Body],
        G: float,
        dt: float,
        height: int,
        width: int,
        obj_size: float,
        scale_coeff: float,
        parent: Window,
    ):
        super().__init__(parent=parent)
        self.height = height
        self.width = width
        # Paint points within a square window so they aren't skewed, so assume a square
        # window with the smaller dimension as the side length. Then will be centered
        # within longer dimension
        self.min_axis = min(height, width)
        self.obj_size = obj_size

        self.setGeometry(0, 0, width, height)
        # Create class to calculate data for simulation
        self.orbit = Orbit(objs, G=G, dt=dt)
        # Scale to normalize distances in the window
        self.scale = scale_coeff * max(np.abs(self.orbit.pos.flatten()))

    def paintEvent(self, evt: QPaintEvent) -> None:
        painter = QPainter(self)
        self.drawPoints(painter)
        painter.end()
        self.orbit.iterate()

    def drawPoints(self, painter: QPainter) -> None:
        """
        Draws one frame to the window.

        Parameters:
        painter - The QPainter object doing the painting on the window.
        """
        self.parent().orbital_prev = []
        for n, obj in enumerate(self.orbit.pos):
            # Set body_color for the painter
            body_color = QColor(mpl_colors.cnames[self.body_colors[n]])
            painter.setPen(body_color)
            painter.setBrush(body_color)
            # Scale x and y distances by the size of the window with magic
            x = self._scale(obj[0], 0)
            y = self._scale(obj[1], 1)

            # Record points to add to bg for path (and centers on circles)
            self.parent().orbital_prev.append(
                (x + self.obj_size / 2, y + self.obj_size / 2)
            )
            # Draw circle (ellipse with equal length and width)
            painter.drawEllipse(int(x), int(y), self.obj_size, self.obj_size)

    def _scale(self, coord_val: float, coord_ind: int) -> float:
        """
        For `coord_ind`, 0 is x and 1 is y. Scales from relative coordinates given in the input
        to pixel coordinates of the window. Keeps the window square, hence using `min_axis`
        """
        return ((coord_val - self.orbit.offset[coord_ind]) / self.scale) * (
            self.min_axis / 2 - 1
        ) + {0: self.width, 1: self.height}[coord_ind] / 2

    def _inverse_scale(
        self, pixel_val: float, coord_ind: int, offset_factor: float = 1
    ) -> float:
        """
        Inverse of `_scale`. Uses for adding a new body. `offset_factor` will offset
        the value of `pixel_val` by a percentage of the width or height.
        """
        return (
            self.scale
            * (
                2 * pixel_val
                - offset_factor * {0: self.width, 1: self.height}[coord_ind]
            )
            / (self.min_axis - 2)
            + self.orbit.offset[coord_ind]
        )


class PopupBase(QDialog):
    def _button_clicked(
        self,
        wrapped_cmd: Callable[..., None],
        wrapped_args: Sequence[Any],
        checks: Sequence[Tuple[int, Callable[..., bool]]],
    ) -> None:
        """
        When this method is called, the function `wrapped_cmd` will be run with arguments
        `wrapped_args`. Each element of `checks` is a tuple with an int referring to an
        element of `wrapped_args` and a function to pass that element to which will return
        a boolean value. Essentially, you can check specific arguments being passed for specific
        conditions, e.g. if an argument can be cast into a float.
        """
        for check in checks:
            if not check[1](check[0]):
                return
        wrapped_cmd(*wrapped_args)
        self.close()


class ChangeValue(PopupBase):
    def __init__(
        self,
        name: str,
        button_cmd: Callable[[str, Union[str, float, int]], None],
        val: float,
        attr: str,
        parent: Window,
    ):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(f"{name} (Current: {val}): ", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.new_val = QLineEdit(parent=self)
        self.accept = QPushButton("Accept")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.new_val)
        self.layout.addWidget(self.accept)
        self.accept.clicked.connect(
            lambda: self._button_clicked(
                button_cmd, [attr, self.new_val.text()], [(1, is_float)]
            )
        )


class AddBody(QDialog):
    def __init__(self, button_cmd: Callable[..., None], parent: Window) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        mass_row = QHBoxLayout()
        mass_label = QLabel("Mass:", self)
        self.mass_val = QLineEdit(parent=self)
        mass_row.addWidget(mass_label)
        mass_row.addWidget(self.mass_val)
        vel_row = QHBoxLayout()
        vel_label = QLabel("Velocity:", self)
        velx_label = QLabel("x:", self)
        self.velx_val = QLineEdit(parent=self)
        vely_label = QLabel("y:", self)
        self.vely_val = QLineEdit(parent=self)
        vel_row.addWidget(vel_label)
        vel_row.addWidget(velx_label)
        vel_row.addWidget(self.velx_val)
        vel_row.addWidget(vely_label)
        vel_row.addWidget(self.vely_val)
        self.accept = QPushButton("Place")
        self.accept.clicked.connect(lambda: self._button_clicked(button_cmd))

        self.layout.addLayout(mass_row)
        self.layout.addLayout(vel_row)
        self.layout.addWidget(self.accept)

    def _button_clicked(self, button_cmd: Callable[..., Any]) -> None:
        # Don't do anything if valid numbers aren't entered.
        try:
            button_cmd(
                (float(self.velx_val.text()), -float(self.vely_val.text())),
                float(self.mass_val.text()),
            )
            self.close()
        except ValueError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    size = app.primaryScreen().size()

    WIDTH = int(size.width() / 1.2)
    HEIGHT = int(size.height() / 1.2)
    OBJ_SIZE = 10
    IS_SOLARSYSTEM = False

    if not IS_SOLARSYSTEM:
        objs = [
            Body(
                mass=100.0,
                pos=(-0.1, -0.1),
                vel=(8, -8),
                body_color="firebrick",
                show_path=False,
                centered=True,
            ),
            Body(
                mass=100.0,
                pos=(0.1, 0.1),
                vel=(-8, 8),
                body_color="indianred",
                show_path=False,
                centered=True,
            ),
            Body(mass=0.1, pos=(0.5, 0.0), vel=(0, -18), body_color="oldlace"),
            Body(mass=0.2, pos=(0.0, 0.6), vel=(20, 0), body_color="mediumpurple"),
            Body(mass=1.2, pos=(1.0, 1.0), vel=(6, -5), body_color="darkkhaki"),
            Body(mass=8.2, pos=(3.2, 3.2), vel=(2, -5), body_color="green"),
            Body(mass=3.3, pos=(-4.1, -3.5), vel=(-2, 4), body_color="steelblue"),
            Body(mass=20.5, pos=(0.0, -2.0), vel=(-12, -1), body_color="navajowhite"),
        ]
        G = 1
        dt = 0.0003
    else:
        # The Solar System
        objs = [
            Body(mass=1.99e30, pos=(0.0, 0.0), vel=(0.0, 0.0), body_color="red"),  # Sun
            Body(
                mass=3.30e23,
                pos=(69.82e9, 0.0),
                vel=(0.0, 47.36e3),
                body_color="gray",
                line_color="black",
            ),  # Mercury
            Body(
                mass=4.87e24,
                pos=(10.89e10, 0.0),
                vel=(0.0, 35.02e3),
                body_color="gray",
                line_color="black",
            ),  # Venus
            Body(
                mass=5.97e24,
                pos=(15.21e10, 0.0),
                vel=(0.0, 29.78e3),
                body_color="blue",
                line_color="dodgerblue",
            ),  # Earth
            Body(
                mass=6.42e23,
                pos=(24.92e10, 0.0),
                vel=(0.0, 24.01e3),
                body_color="olive",
                line_color="tan",
            ),  # Mars
            Body(
                mass=1.90e27,
                pos=(81.66e10, 0.0),
                vel=(0.0, 13.07e3),
                body_color="gray",
                line_color="black",
            ),  # Juptier
            Body(
                mass=5.68e26,
                pos=(15.14e11, 0.0),
                vel=(0.0, 9.68e3),
                body_color="gray",
                line_color="black",
            ),  # Saturn
            Body(
                mass=8.68e25,
                pos=(30.08e11, 0.0),
                vel=(0.0, 6.80e3),
                body_color="gray",
                line_color="black",
            ),  # Uranus
            Body(
                mass=1.02e26,
                pos=(45.37e11, 0.0),
                vel=(0.0, 5.43e3),
                body_color="gray",
                line_color="black",
            ),  # Neptune
        ]
        G = 6.67408e-11  # Gravitational constant
        dt = 864000  # 10 days

    window = Window(
        objs, G=G, dt=dt, width=WIDTH, height=HEIGHT, obj_size=OBJ_SIZE, scale_coeff=3
    )
    window.show()
    sys.exit(app.exec_())

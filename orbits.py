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
is positive, Fx is negative." (http://www.feynmanlectures.caltech.edu/I_09.html)

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

import numpy as np
import matplotlib.colors as mpl_colors
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QTimer


class Orbit:
    """
    Models Newtonian dynamics numerically and discretely of the graviational
    attraction and subsequent effect of such on various objects (think
    planets)

    Parameters:
    objs - An arbitrary number of objects' data given as dictionaries of their
           masses, velocities and positions. For example, one object could be:

                {'mass': 10, 'pos': [1, 5], 'vel':[3, 0], 'show_path':True}

           where the lists are for the x- and y-directions of the position
           and velocity vectors and `show_path` is a boolean (defauled to
           True) that determines whether the orbit path is shown.
    G - (default 1) The value for the graviational constant found in Newton's
        equation for the force from gravity
    dt - (default 0.01) The time interval, how much time passes between each
         calculation of the positions and velocities. Lower is more accurate.
    """

    def __init__(self, *objs, G=None, dt=None):
        self.G = G or 1
        self.dt = dt or 0.00005
        self.offset = [0, 0]

        # Index of dict that is to have orbits centered on
        try:
            self.cind = objs.index(list(filter(lambda x: x['centered'] is True, objs))[0])
        except IndexError:
            self.cind = None

        # Turn into numpy arrays with dimension (no. objects, no. dimensions)
        self.pos, self.vel, self.mass = [], [], []
        for obj in objs:
            self.pos.append(obj['pos'])
            self.vel.append(obj['vel'])
            self.mass.append(obj['mass'])
        self.pos = np.array(self.pos, dtype='float64')
        self.vel = np.array(self.vel, dtype='float64')
        self.mass = np.array(self.mass)

        # Make sure consistent number of objects between pos and vel
        if len(self.pos) != len(self.vel):
            raise Exception('Different number of objects for position and velocity lists.')
        self.num_objects = len(self.pos)

        # Make sure consistent number of dimensions across pos and vel
        if not all([len(self.pos[obj]) == len(self.vel[obj]) for obj in range(self.num_objects)]):
            raise Exception('Different number of dimensions for velocity and position.')
        self.num_dims = len(self.pos[0])

    def find_new_acc(self):
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
        new_acc = [[]] * self.num_objects
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
                dist_cubed = np.math.sqrt(sum(
                    [(self.pos[oind][dim] - self.pos[eind][dim])**2
                        for dim in range(self.num_dims)]))**3

                # Iterate through each dimension
                for dind in range(self.num_dims):
                    # Tack on total for each accerleration component
                    tot_acc[dind] += self.mass[eind] * \
                      (self.pos[oind][dind] - self.pos[eind][dind]) / dist_cubed

            # Multiply on the constants to the sum
            new_acc[oind] = [-self.G * acc for acc in tot_acc]

        return new_acc

    def update_objects(self, acc):
        """
        With acceleration data, the velocity and position vectors for each
        object is updated in-place.
        """
        for oind in range(self.num_objects):
            for dind in range(self.num_dims):
                self.vel[oind][dind] += acc[oind][dind] * self.dt
                self.pos[oind][dind] += self.vel[oind][dind] * self.dt

        self.offset = self.pos[self.cind] if self.cind is not None else [0, 0]

    def iterate(self):
        """
        Goes through one 'iteration' where each takes a total time of dt. Since
        this is a discretized version of Newtonian dynamics, it will be more
        accurate the lower dt is.
        """
        new_acc = self.find_new_acc()
        self.update_objects(new_acc)


class Window(QWidget):
    """
    Main window which has the timer which updates both the foreground and the
    background. All parameters are for Foreground and Background classes

    Parameters:
    default_color (default black) - Only one not passed on. The default color
                                    of the objects if no color is specified.
    """
    def __init__(self, *objs, default_color='black', G=None, dt=None, width=500,
                 height=500, obj_size=5, parent=None):
        super().__init__(parent=parent)
        # Fills in the blanks in the list of dict due to default values
        # `show_path` defaults to `True`, `centered` defaults to `False`
        # and `color` to `black`
        objs = [dict(obj,
            show_path=obj.get('show_path', True),
            centered=obj.get('centered', False),
            color=obj.get('color', 'black')) for obj in objs]
        self.setWindowTitle('Newtonian Orbital Dynamics')

        self.setGeometry(300, 200, width, height)

        # Create the canvases
        self.foreground = Foreground(*objs, G=G, dt=dt, width=width,
            height=height, obj_size=obj_size, parent=self)
        self.background = Background(width, height)

        # Makes a list of the colors for each object
        self.colors = [obj['color'] or default_color for obj in objs]
        self.background.colors = self.colors
        self.foreground.colors = self.colors

        # Makes a list of whether or not to show the path for each object
        # Check to make sure every input for `show_path` is either a boolean or an empty string
        osp = [obj['show_path'] for obj in objs]
        if not len(list(filter(lambda x: type(x)==bool, osp))) == len(osp):
            raise Exception('Unknown data type for show_path parameter.')
        self.background.show_paths = osp

        # Update every N milliseconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.multi_update)
        self.timer.start(5)

    def multi_update(self):
        # Update everything
        self.foreground.update()
        self.background.orbital_prev = self.foreground.orbital_prev
        self.background.paintEvent()
        self.update()

    def paintEvent(self, evt):
        # Adds the pixmap to itself
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

    def __init__(self, width, height):
        QPixmap.__init__(self, width, height)
        # Background color
        self.fill(QColor(200, 200, 200))
        self.orbital_prev = []

    def paintEvent(self):
        # QPixmap doesn't have a paintEvent, this is just a mocked-up version
        painter = QPainter(self)
        for n, orbit in enumerate(self.orbital_prev):
            # Use `False` explicitly sign empty string is considered `True`
            if self.show_paths[n] is not False:
                color = QColor(mpl_colors.cnames[self.colors[n]])
                painter.setPen(color)
                painter.drawPoint(*orbit)
        painter.end()


class Foreground(QWidget):
    """
    Displays the simulation of the orbits in a Qt Widget by painting each frame
    with QPainter and being refreshed via an internal timer.

    Parameters:
    objs - The arbitrary number of objects to be passed to the Orbit class.
    G (default None) - The value for the gravitational constant to be passed to
                       the Orbit class.
    dt (default None) - The time interval to be passed to the Orbit class.
    height (default 500) - Height of the widget
    width (default 500) - Width of the widget
    parent (default None) - Parameter for the inherited QWidget class.
    """

    def __init__(self, *objs, G=None, dt=None, height=500, width=500,
                 obj_size=5, parent=None):
        super().__init__(parent=parent)
        self.height = height
        self.width = width
        self.obj_size = obj_size
        self.orbital_prev = []

        self.setGeometry(0, 0, width, height)
        # Create class to calculate data for simulation
        self.orbit = Orbit(*objs, G=G, dt=dt)
        # Scale to normalize distances in the window
        self.scale = 1.5 * max(self.orbit.pos.flatten())

    def paintEvent(self, evt):
        painter = QPainter(self)
        self.drawPoints(painter)
        painter.end()
        self.orbit.iterate()

    def drawPoints(self, painter):
        """
        Draws one frame to the window.

        Parameters:
        painter - The QPainter object doing the painting on the window.
        """
        self.orbital_prev = []

        for n, obj in enumerate(self.orbit.pos):
            # Set color for the painter
            color = QColor(mpl_colors.cnames[self.colors[n]])
            painter.setPen(color)
            painter.setBrush(color)

            # Scale x and y distances by the size of the window
            x = ((obj[0] - self.orbit.offset[0]) / self.scale) * (self.width/2 - 1) + self.width/2
            y = ((obj[1] - self.orbit.offset[1]) / self.scale) * (self.height/2 - 1) + self.height/2

            # Record points to add to bg for path (and centers on circles)
            self.orbital_prev.append((x + self.obj_size/2, y + self.obj_size/2))
            # Draw circle (ellipse with equal length and width)
            painter.drawEllipse(x, y, self.obj_size, self.obj_size)


if __name__ == "__main__":
    width, height, obj_size = 800, 800, 10
    objs = [{'mass': 100.0, 'pos': [-0.1, -0.1], 'vel': [ 8,  -8], 'color': 'firebrick', 'show_path': False, 'centered': True},
            {'mass': 100.0, 'pos': [ 0.1,  0.1], 'vel': [-8,   8], 'color': 'indianred', 'show_path': False},
            {'mass':   0.1, 'pos': [ 0.5,  0.0], 'vel': [ 0, -18], 'color': 'oldlace'},
            {'mass':   0.2, 'pos': [ 0.0,  0.6], 'vel': [20,   0], 'color': 'mediumpurple'},
            {'mass':   1.2, 'pos': [ 1.0,  1.0], 'vel': [ 6,  -5], 'color': 'darkkhaki'},
            {'mass':   8.2, 'pos': [ 3.2,  3.2], 'vel': [ 2,  -5], 'color': 'green'},
            {'mass':   3.3, 'pos': [-4.1, -3.5], 'vel': [-2,   4], 'color': 'steelblue'},
            {'mass':  20.5, 'pos': [ 0.0, -2.0], 'vel': [-12,  -1], 'color': 'navajowhite'}]
    G = 1
    dt = 0.0003

    app = QApplication(sys.argv)
    window = Window(*objs, G=G, dt=dt, width=width, height=height, obj_size=obj_size)
    window.show()
    sys.exit(app.exec_())

    # Testing system
    # objs = [{'mass': 100, 'pos': [0, 0], 'vel': [0, 0], 'color':'orange', 'centered': True},
    #         {'mass':   3, 'pos': [5, 0], 'vel': [0, 2], 'color':'grey'}]
    # G = 1
    # dt = 0.003

    # The Solar System
    # objs = [{'mass': 1.99e30, 'pos': [0, 0], 'vel': [0, 0], 'color': 'red'}, # Sun
    #         {'mass': 3.30e23, 'pos': [69.82e9, 0], 'vel': [0, 47.36e3]}, # Mercury
    #         {'mass': 4.87e24, 'pos': [10.89e10, 0], 'vel': [0, 35.02e3]}, # Venus
    #         {'mass': 5.97e24, 'pos': [15.21e10, 0], 'vel': [0, 29.78e3], 'color': 'blue'}, # Earth
    #         {'mass': 6.42e23, 'pos': [24.92e10, 0], 'vel': [0, 24.01e3]}, # Mars
    #         {'mass': 1.90e27, 'pos': [81.66e10, 0], 'vel': [0, 13.07e3]}, # Juptier
    #         {'mass': 5.68e26, 'pos': [15.14e11, 0], 'vel': [0,  9.68e3]}, # Saturn
    #         {'mass': 8.68e25, 'pos': [30.08e11, 0], 'vel': [0,  6.80e3]}, # Uranus
    #         {'mass': 1.02e26, 'pos': [45.37e11, 0], 'vel': [0,  5.43e3]}] # Neptune
    # G = 6.67408e-11 # Gravitational constant
    # dt = 864000 # 10 days

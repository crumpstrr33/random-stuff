import numpy as np
from tkinter import Tk, Canvas, Menu

WIDTH = 1080
HEIGHT = 720
NUM_BALLS = 15
BALL_LIST = []
DT = 1/30
COLORS = np.load('all_tkinter_colors.npy')
FACES = np.load('CIA_faces.npy')

tk = Tk()
canvas = Canvas(tk, width=WIDTH, height=HEIGHT, bg='black')
tk.title('Bouncing Squares!')
canvas.pack()

menu = Menu(tk)
file = Menu(menu)
menu.add_cascade(label='File', menu=file)

file.add_separator()
file.add_command(label='Exit...', command=lambda: tk.destroy())

tk.config(menu=menu)


class Ball(object):
    def __init__(self, pos_x, pos_y, init_v, init_theta=0, energy_loss=0.1,
                 friction=0.02, mass=1, gravity=9.8, size=50, face='',
                 color=['blue', 'black', 'black']):
        # Constants
        self.time_scale = DT
        self.g = gravity
        self.energy_loss = energy_loss
        self.size = size
        self.friction = friction
        self.mass = mass
        self.face = face

        # Initial Conditions
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.angle = init_theta
        self.speed_x = init_v * np.cos(init_theta)
        self.speed_y = init_v * np.sin(init_theta)
        self.last_coll = NUM_BALLS + 1

        # Creates objects
        self.shape = canvas.create_rectangle(pos_x, pos_y, pos_x + self.size,
                                             pos_y + self.size, fill=color[0],
                                             outline=color[1])
        self.char = canvas.create_text(pos_x + 0.5*self.size,
                                       pos_y + 0.5*self.size,
                                       fill=color[2], text=self.face)

    def find_pos(self):
        return canvas.coords(self.shape)

    def update(self):
        canvas.move(self.shape, self.speed_x * self.time_scale,
                    self.speed_y * self.time_scale)
        canvas.move(self.char, self.speed_x * self.time_scale,
                    self.speed_y * self.time_scale)
        self.pos = self.find_pos()

        self.speed_y += self.g * DT

        if self.pos[0] <= 0 and self.speed_x < 0:
            self.speed_x *= -(1 - np.sqrt(self.energy_loss))
            self.speed_y *= (1 - self.friction)
        if self.pos[1] <= 0 and self.speed_y < 0:
            self.speed_y *= -(1 - np.sqrt(self.energy_loss))
            self.speed_x *= (1 - self.friction)
        if self.pos[2] >= WIDTH and self.speed_x > 0:
            self.speed_x *= -(1 - np.sqrt(self.energy_loss))
            self.speed_y *= (1 - self.friction)
        if self.pos[3] >= HEIGHT and self.speed_y > 0:
            self.speed_y *= -(1 - np.sqrt(self.energy_loss))
            self.speed_x *= (1 - self.friction)


def main():
    for i in range(NUM_BALLS):
        BALL_LIST.append(Ball(pos_x=np.random.uniform(0, WIDTH),
                              pos_y=np.random.uniform(0, HEIGHT),
                              init_v=np.random.uniform(10, 150),
                              init_theta=np.random.uniform(0, 2 * np.pi),
                              energy_loss=0.01,
                              friction=0.01,
                              mass=1,
                              gravity=9.8,
                              size=50,
                              face=np.random.choice(FACES),
                              color=np.random.choice(COLORS, 3)))

    while True:
        for ball in BALL_LIST:
            ball.update()

        tk.update()


if __name__ == "__main__":
    main()

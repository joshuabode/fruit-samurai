from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from random import randint, randrange, choice
from math import ceil

# Cheatcode adds a floor, 

sprite_sheet = Image.open("Fruit+.png")
fps = 120   # FPS of the game. A high value results in smooth motion
dt = 1/fps  # Time interval for the physics engine
ppm = 240   # Pixels per Metre
e = 0.3     # Coefficient of Restitution
g = 9.81    # Acceleration due to gravity in metres per second 
width, height = 960, 540    # Size of gameplay area in pixels
fruit_size = 48             # Fruit diameter in pixels
cheating = False            # Boolean value
interval = 2000             # Interval between new fruits in milliseconds
friut_indicies = [0, 1, 2, 9, 12,   # The indicies of the fruits from the sprite sheet which I want to use
                  13, 17, 18, 19, 
                  21, 22, 23, 26, 37]

class Game(Canvas):
    def __init__(self, w, h):
        super().__init__(width=w, height=h)
        self.m_x = None             # Holding previous mouse x-position
        self.m_y = None             # Holding previous mouse y-position
        self.m_vel = (None, None)   # Holding mouse velocity
        self.bind("<Motion>", self.mouse_velocity)

    def new_fruit(self):
        fruit = Fruit(  (choice(friut_indicies)*16, 16),
                        (randrange(fruit_size, width-fruit_size), height-fruit_size),
                        (randrange(-3, 3)*ppm, randrange(-7, -5)*ppm),
                        self)
        self.tag_bind(fruit.object, "<Enter>", fruit.delete)    # Delete fruit when mouse hovers over it

        # New fruit is projected at a random interval = INTERVAL +/- 0.5 seconds 
        self.after(randint(interval-500, interval+500), self.new_fruit)     

    def mouse_velocity(self, e):
        # Calculates the mouse velocity using numerical differentiation: v = dx/dt
        if self.m_x and self.m_y:
            self.m_vel = ((e.x - self.m_x)/dt, (e.y - self.m_y)/dt)
        self.m_x = e.x
        self.m_y = e.y

class Fruit:
    def __init__(self, sprite_coords, coords, velocity, canvas):
        self.s_x, s_y = sprite_coords
        self.sprite = sprite_sheet.crop((self.s_x, s_y, self.s_x+16, s_y+16)).resize((fruit_size, fruit_size), Image.Resampling.NEAREST)
        self.image = ImageTk.PhotoImage(self.sprite)
        self.x, self.y = coords
        self.v_x, self.v_y = velocity
        self.canvas = canvas
        self.object = canvas.create_image(self.x, self.y, image=self.image, anchor='center')
        self.bbox = self.canvas.bbox(self.object)
        self.deleted = False
        self.tick()

    def delete(self, event):
        self.deleted = True
        # Generates two halves of chopped fruit
        ChoppedFruit((self.s_x, 5*16),
                (self.canvas.coords(self.object)[0]-16, self.canvas.coords(self.object)[1]),
                (self.canvas.m_vel[0]-50, self.canvas.m_vel[1]),
                self.canvas, False)
        ChoppedFruit((self.s_x, 5*16),
                (self.canvas.coords(self.object)[0]+16, self.canvas.coords(self.object)[1]),
                (self.canvas.m_vel[0]+50, self.canvas.m_vel[1]),
                self.canvas, True)
        # Removes the old sprite from the canvas
        self.canvas.delete(self.object)
    
    def displace(self):
        # Main physics function which handles collisions with walls and calculates displacenet 
        # Uses SUVAT equations and Newton's law of restitution
        left, top, right, bottom = self.bbox
        grounded = bottom >= height
        dy, dx = 0, 0
        if left <= 0:
            self.v_x = -self.v_x*e
            dx = -left
        if right >= width:
            self.v_x = -self.v_x*e
            dx = -(right-width)
        if top <= 0:
            self.v_y = -self.v_y*e
            dy = -top
        if cheating and grounded:
            self.v_y = -self.v_y*e
            dy = -(bottom-height)
        if top >= height:
            self.deleted = True
        if not(grounded and cheating):
            self.v_y += g*ppm*dt
        dx += self.v_x*dt
        dy += self.v_y*dt
        return (dx, dy)


    def tick(self):
        # This function updates the positino of the fruit
        self.canvas.move(self.object, *self.displace())
        self.bbox = self.canvas.bbox(self.object)
        if not self.deleted:
            self.canvas.after(int(1000*dt), self.tick)


# Chopped fruit class is nearly identical to the fruit class but includes functionality to flip the image
class ChoppedFruit:
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image):
        self.s_x, s_y = sprite_coords
        self.sprite = sprite_sheet.crop((self.s_x, s_y, self.s_x+16, s_y+16)).resize((fruit_size, fruit_size), Image.Resampling.NEAREST)
        if flip_image:
            self.sprite = self.sprite.transpose(method=Image.FLIP_LEFT_RIGHT)
        self.image = ImageTk.PhotoImage(self.sprite)
        self.x, self.y = coords
        self.v_x, self.v_y = velocity
        self.canvas = canvas
        self.object = canvas.create_image(self.x, self.y, image=self.image, anchor='center')
        self.bbox = self.canvas.bbox(self.object)
        self.deleted = False
        self.tick()

# Driver code to initialise the window and start dispensing fruits
window = Tk()
window.title("Fruit Samurai")
window.resizable(False, False)
game = Game(width, height)
game.new_fruit()
game.pack()
window.mainloop()
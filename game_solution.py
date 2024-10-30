from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from random import randint
from math import ceil

# Cheatcode adds a floor, 

sprite_sheet = Image.open("Fruit+.png")
fps = 100
dt = 1/fps
ppm = 160    # Pixels per Metre
e = 0.3      # Coefficient of Restitution
width, height = 640, 360
fruit_size = 32
cheating = False

class Game(Canvas):
    def __init__(self, w, h):
        super().__init__(width=w, height=h)
        self.fruits = []

    def new_fruit(self):
        fruit = Fruit(  (randint(0, 37)*16, randint(0,2)*16),
                        (randint(fruit_size, width-fruit_size), height-fruit_size),
                        (randint(-10, 10)*ppm, randint(-10, -5)*ppm),
                        self)
        self.tag_bind(fruit.object, "<Enter>", fruit.delete)
        self.after(500, self.new_fruit)

class Fruit:
    def __init__(self, sprite_coords, coords, velocity, canvas):
        s_x, s_y = sprite_coords
        self.sprite = sprite_sheet.crop((s_x, s_y, s_x+16, s_y+16)).resize((fruit_size, fruit_size), Image.Resampling.NEAREST)
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
        print(self.object)
        self.canvas.delete(self.object)
    
    def displace(self):
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
            self.v_y += 9.81*ppm*dt
        dx += self.v_x*dt
        dy += self.v_y*dt
        return (dx, dy)


    def tick(self):
        self.canvas.move(self.object, *self.displace())
        self.bbox = self.canvas.bbox(self.object)
        if not self.deleted:
            self.canvas.after(int(1000*dt), self.tick)

# def tick(fruit):
#     game.move(fruit.object, *fruit.displace())
#     game.after(int(1000*dt), tick(fruit))

window = Tk()
window.title("Fruit Samurai")
game = Game(width, height)
game.new_fruit()
game.pack()
window.mainloop()
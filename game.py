from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from PIL import ImageTk, Image, ImageDraw
from random import randint, choice, uniform
from collections import deque
from fruit import Fruit, ChoppedFruit
from fonts import *

class Game(Canvas):
    def create_label(self, text, x, y, anchor):
        label = Label(self.window, text=text, font=self.font)
        self.object = self.create_window(x, y, anchor=anchor, window=label)
        return label

    def __init__(self, window,  w, h):
        self.window = window
        super().__init__(master=window, width=w, height=h, background="#f0d7a1")
        self.m_x = None             # Holding previous mouse x-position
        self.m_y = None             # Holding previous mouse y-position
        self.m_vel = (None, None)   # Holding mouse velocity
        fps = 120   # FPS of the game. A high value results in smooth motion
        self.dt = 1/fps  # Time interval for the physics engine
        self.ppm = 240   # Pixels per Metre
        self.e = 0.3     # Coefficient of Restitution
        self.sprite_sheet = Image.open("Fruit+.png")
        self.g = 9.81    # Acceleration due to gravity in metres per second 
        self.width, self.height = w, h   # Size of gameplay area in pixels
        self.fruit_size = 60             # Fruit diameter in pixels
        self.cheating = False            # Boolean values for game states
        self.paused = False
        self.boss_keyed = False
        self.game_ended = False
        self.interval = 2000             # Interval between new fruits in milliseconds
        self.fruit_indicies = [0, 1, 2, 9, 12,   # The indicies of the fruits from the sprite sheet which I want to use
                        13, 17, 18, 19, 
                        21, 22, 23, 26, 37]
        self.key_history = deque([], 8)      # Double-ended queue acting as memory to check for the cheatcode
        self.hit_or_miss = deque([], 50)    # Double-ended queue used to calculate rolling accuracy to dynamically update difficulty
        self.lives = 5
        self.score = 0
        self.streak = 0
        self.font = ("arcade.ttf", 20, 'bold')
        self.lv_content = Label(self, text=f"Lives: {self.lives}", bg="#f0d7a1", font=("ArcadeClassic", 24, 'bold'), fg='black')
        self.sc_content = Label(self, text=f"Score: {self.score}", bg="#f0d7a1", font=("ArcadeClassic", 24, 'bold'), fg='black')
        self.st_content = Label(self, text=f"Streak: {self.streak}", bg="#f0d7a1", font=("ArcadeClassic", 24, 'bold'), fg='black')
        self.lives_text = self.create_window(10, 10, anchor='nw', window=self.lv_content)         
        self.score_text = self.create_window(self.width/2, 10, anchor='n', window=self.sc_content)
        self.streak_text = self.create_window(self.width - 10, 10, anchor='ne', window=self.st_content)
        with open('controls.txt', 'r') as file:
            self.controls = eval(file.read())
        self.update()
        self.bind("<Motion>", self.mouse_velocity)

    def update(self):
        self.interval = 2000/(1+0.01*sum(self.hit_or_miss)**2)
        if not self.game_ended:
            if self.paused:
                pass
            else:
                self.lv_content.config(text=f"Lives: {self.lives}")
                self.sc_content.config(text=f"Score: {int(self.score)}")
                self.st_content.config(text=f"Streak: {self.streak}")
                if self.lives < 1:
                    self.game_over()
                
            self.after(500, self.update)

    def key_in(self, key):
        self.check_cheat(key)
        if key.char == self.controls['pause']:
            self.pause(key)
        elif key.char == self.controls['boss']:
            self.boss_key(key)


    def new_fruit(self):

        if not self.game_ended:
            if self.paused:
                pass
            else:
                fruit = Fruit(  (choice(self.fruit_indicies)*16, 16),
                (randint(self.fruit_size, self.width-self.fruit_size), self.height-self.fruit_size),
                (uniform(-3, 3)*self.ppm, uniform(-6.64, -4)*self.ppm), self)
                self.tag_bind(fruit.object, "<Enter>", fruit.delete)    # Delete fruit when mouse hovers over it
                # New fruit is projected at a random interval = INTERVAL +/- 0.1 seconds 
                
            self.after(max(0, randint(self.interval-100, self.interval+100)), self.new_fruit)     

    def mouse_velocity(self, event):
        # Calculates the mouse velocity using numerical differentiation: v = dx/dt
        if self.m_x and self.m_y:
            self.m_vel = ((event.x - self.m_x)/self.dt, (event.y - self.m_y)/self.dt)
        self.m_x = event.x
        self.m_y = event.y

    def check_cheat(self, key):
        self.key_history.append(key.keysym)
        if ''.join(self.key_history) == 'LeftRightLeftRightLeftRightDownDown':    # Cheatcode is floor
            self.cheating = not self.cheating

    def pause(self, key):
        self.paused = not self.paused
        if self.paused:
            self.pause_label = Label(self, text="Paused", font=("ArcadeClassic", 36, 'bold'), bg="#f0d7a1", fg='black')
            self.pause_text = self.create_window(self.width/2, self.height/2, anchor='center', window=self.pause_label)
        else:
            self.delete(self.pause_text)

    def boss_key(self, key):
        self.boss_keyed = not self.boss_keyed
        if self.boss_keyed:
            w = self.window.winfo_screenwidth()
            h = self.window.winfo_screenheight()
            self.boss_window = Toplevel()
            self.boss_window.title = "Macrohard Excel"
            self.boss_window.attributes('-fullscreen', True)
            canvas = Canvas(self.boss_window, 
                         width=w,
                         height=h)
            img = ImageTk.PhotoImage(master=canvas, 
                                     image=Image.open("boss.jpg").resize((w, h), Image.Resampling.BICUBIC))
            canvas.pack(expand=True)
            canvas.create_image(0, 0, image=img, anchor='nw')
            self.boss_window.bind("<Key-b>", self.boss_key)
            self.pause(key)
            self.boss_window.mainloop()
        else:
            self.boss_window.destroy()

    def game_over(self):
        self.game_ended = True
        game_over_label = Label(self, text="Game Over", font=("ArcadeClassic", 36, 'bold'), bg="#f0d7a1", fg='black')
        self.create_window(self.width/2, self.height/2, anchor='center', window=game_over_label)

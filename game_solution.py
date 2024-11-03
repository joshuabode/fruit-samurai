from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image, ImageDraw
from random import randint, choice, uniform
from collections import deque
from fruit import Fruit, ChoppedFruit


class App():
    # TODO: Add the initial game menu

    def __init__(self):
        start_window = Tk()
        start_window.title("Fruit Samurai")
        self.menu = start_window
        self.init_menu()

    def init_menu(self):
        root = self.menu
        title = Label(root, text="Fruit Samurai", font=("TkHeadingFont", 36, 'bold'))
        new_game = Button(root, text="New Game", command=self.new_game)
        title.pack()
        new_game.pack()
        root.mainloop()

    def new_game(self):
        self.menu.destroy()
        game_window = Tk()
        game_window.title("Fruit Samurai")
        game_window.resizable(False, False)
        self.main_game = Game(game_window, 960, 540)
        game_window.bind("<Key>", self.main_game.key_in)
        self.main_game.new_fruit() 
        self.main_game.pack()
        self.game_window = game_window
        game_window.mainloop()


class Game(Canvas):
    def create_label(self, text, x, y, anchor):
        label = Label(self.window, text=text, font=self.font)
        self.object = self.create_window(x, y, anchor=anchor, window=label)
        return label

    def __init__(self, window,  w, h):
        self.window = window
        super().__init__(master=window, width=w, height=h)
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
        self.interval = 2000             # Interval between new fruits in milliseconds
        self.fruit_indicies = [0, 1, 2, 9, 12,   # The indicies of the fruits from the sprite sheet which I want to use
                        13, 17, 18, 19, 
                        21, 22, 23, 26, 37]
        self.key_history = deque([], 9)      # Double-ended queue acting as memory to check for the cheatcode
        self.lives = 5
        self.score = 0
        self.streak = 0
        self.font = ("TkDefaultFont", 20, 'bold')
        self.lv_content = StringVar(master=self.window, value=f"Lives: {self.lives}")
        self.sc_content = StringVar(master=self.window, value=f"Score: {self.score}")
        self.st_content = StringVar(master=self.window, value=f"Streak: {self.streak}")
        self.lives_text = self.create_label(self.lv_content, 10, 10, 'nw')         
        self.score_text = self.create_label(self.sc_content, self.width/2, 10, 'n')
        self.streak_text = self.create_label(self.st_content, self.width - 10, 10, 'ne')
        self.controls = {}
        self.game_ended = False
        with open('controls.txt', 'r') as file:
            for bind in file.readlines():
                bind = bind.strip().split(",")
                self.controls[bind[0]] = bind[1]
        self.update()
        self.bind("<Motion>", self.mouse_velocity)
  
    def update(self):
        self.lives_text['textvariable'] = self.lv_content
        self.score_text['textvariable'] = self.sc_content
        self.streak_text['textvariable'] = self.st_content

        self.lv_content.set(f"Lives: {self.lives}")
        self.sc_content.set(f"Score: {int(self.score)}")
        self.st_content.set(f"Streak: {self.streak}")
        if self.streak:
            self.interval = min(2000, int(10000/self.streak))
        else:
            self.interval = 2000
        if self.lives < 1:
            self.game_over()
        if not self.game_ended and not self.paused:
            self.after(500, self.update)

    def key_in(self, key):
        print(self.controls)
        self.check_cheat(key)
        if key.char == self.controls['pause']:
            self.pause(key)
        elif key.char == self.controls['boss']:
            self.boss_key(key)


    def new_fruit(self):
        fruit = Fruit(  (choice(self.fruit_indicies)*16, 16),
                        (randint(self.fruit_size, self.width-self.fruit_size), self.height-self.fruit_size),
                        (uniform(-3, 3)*self.ppm, uniform(-6.64, -4)*self.ppm),
                        self)
        self.tag_bind(fruit.object, "<Enter>", fruit.delete)    # Delete fruit when mouse hovers over it

        # New fruit is projected at a random interval = INTERVAL +/- 0.5 seconds 
        if not self.game_ended and not self.paused:
            self.after(randint(self.interval-500, self.interval+500), self.new_fruit)     

    def mouse_velocity(self, event):
        # Calculates the mouse velocity using numerical differentiation: v = dx/dt
        if self.m_x and self.m_y:
            self.m_vel = ((event.x - self.m_x)/self.dt, (event.y - self.m_y)/self.dt)
        self.m_x = event.x
        self.m_y = event.y

    def check_cheat(self, key):
        self.key_history.append(key.char)
        if ''.join(self.key_history) == 'halfbrick':    # "Halfbrick", (the developers of the original game) is the cheat code
            self.cheating = True

    def pause(self, key):
        
        print("UOFJLIFIS")
        if key.char == self.controls['pause']:
            self.paused = not self.paused
            print(self.paused)
        if self.paused:
            pause_label = Label(self, text="Paused", font=("TkHeadingFont", 36, 'bold'))
            pause_text = self.create_window(self.width/2, self.height/2, anchor='center', window=pause_label)
            unpause = Button(self, text="Unpause", command=self.pause(key))
            unpause_button = self.create_window(self.width/2, self.height*4/7, anchor='center', window=unpause)
            print("PAUSE")
        if not self.paused:
            self.delete(pause_text)
            self.delete(unpause_button)

    def boss_key(self, key):
        if key.char == self.controls['boss']:
            self.boss_keyed = not self.boss_keyed
            print("BOSS")

    def game_over(self):
        self.game_ended = True
        game_over_label = Label(self, text="Game Over", font=("TkHeadingFont", 36, 'bold'))
        self.create_window(self.width/2, self.height/2, anchor='center', window=game_over_label)

# Driver code to initialise the app
app = App()

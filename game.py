"""
GAME.PY

Defines the Game object which inherits from Tkinter Canvas.
"""

from tkinter import *
from tkinter import font, filedialog, simpledialog
from PIL import ImageTk, Image
from random import randint, choice, uniform
from collections import deque
from fruit import Fruit
from bomb import Bomb
from leaderboard import leaderboard
import pickle

class Game(Canvas):
    def __init__(self, window, w, h, lives=5, score=0, streak=0, hit_or_miss=[None for _ in range(50)]):
        super().__init__(master=window, width=w, height=h, background="#f0d7a1", cursor="star")
        self.window = window
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
        self.fruits = []             # List holding the current fruits
        self.bombs = []
        self.cheating = False            # Boolean values for game states
        self.cheated = False            
        self.paused = False
        self.boss_keyed = False
        self.game_ended = False
        self.interval = 2000             # Interval between new fruits in milliseconds
        self.fruit_indicies = [0, 1, 2, 9, 12,   # The indicies of the fruits from the sprite sheet which I want to use
                        13, 17, 18, 19, 
                        21, 22, 23, 26, 37]
        self.key_history = deque([], 8)      # Double-ended queue acting as memory to check for the cheatcode
        self.hit_or_miss = deque(hit_or_miss, maxlen=50)    # Double-ended queue used to calculate rolling accuracy to dynamically update difficulty
        self.lives = lives
        self.score = score
        self.streak = streak
        self.retro_font = font.Font(family="ArcadeClassic", size=20)
        self.heading_font = font.Font(family='TkHeadingFont', size=36, weight='bold')
        self.heading_font
        self.lv_content = Label(self, text=f"Lives: {self.lives}", bg="#f0d7a1", font=self.retro_font, fg='black')
        self.sc_content = Label(self, text=f"Score: {self.score}", bg="#f0d7a1", font=self.retro_font, fg='black')
        self.st_content = Label(self, text=f"Streak: {self.streak}", bg="#f0d7a1", font=self.retro_font, fg='black')
        self.lives_text = self.create_window(10, 10, anchor='nw', window=self.lv_content)         
        self.score_text = self.create_window(self.width/2, 10, anchor='n', window=self.sc_content)
        self.streak_text = self.create_window(self.width - 10, 10, anchor='ne', window=self.st_content)
        with open('controls.txt', 'r') as file:
            self.controls = eval(file.read())
        self.update()
        self.bind("<Motion>", self.mouse_handler)

    def update(self):
        if not self.game_ended:
            self.interval = interval(self.streak)
        try:
            self.delete(min(self.find_withtag("mouse")))
        except ValueError:
            pass
        if not self.game_ended:
            if self.paused:
                pass
            else:
                self.lv_content.config(text=f"Lives: {self.lives}")
                self.sc_content.config(text=f"Score: {int(self.score)}")
                self.st_content.config(text=f"Streak: {self.streak}")
                if self.lives < 1:
                    self.game_over()
                
            self.after(20, self.update)

    def create_label(self, text, x, y, anchor):
        label = Label(self.window, text=text, font=self.font)
        self.object = self.create_window(x, y, anchor=anchor, window=label)
        return label

    def key_in(self, key):
        self.check_cheat(key)
        if key.char == self.controls['pause']:
            self.pause(key)
        elif key.char == self.controls['boss']:
            self.boss_key(key)

    def new_fruit(self):
        if self.paused:
            pass
        else:
            fruit = Fruit(  (choice(self.fruit_indicies)*16, 16),
            (randint(self.fruit_size, self.width-self.fruit_size), self.height-self.fruit_size),
            (uniform(-3, 3)*self.ppm, uniform(-6.64, -4)*self.ppm), self)
            self.fruits.append(fruit)
            if not self.game_ended:
                self.tag_bind(fruit.object, "<Enter>", fruit.delete)    # Delete fruit when mouse hovers over it
            # New fruit is projected at a random interval = INTERVAL +/- 0.1 seconds 
        self.after(max(0, randint(self.interval-100, self.interval+100)), self.new_fruit) 

    def new_bomb(self):
        if not self.game_ended:
            if self.paused:
                pass
            elif self.score > 1_000:  # Only spawn bombs if the player scores above 1,000
                bomb = Bomb((randint(self.fruit_size, self.width-self.fruit_size), self.height-self.fruit_size), (uniform(-3, 3)*self.ppm, uniform(-6.64, -4)*self.ppm), self)
                self.tag_bind(bomb.object, "<Enter>", bomb.delete)    # Delete fruit when mouse hovers over it
                # New bomb is projected approximately once per five fruits 
                
            self.after(max(0, 5*randint(self.interval-100, self.interval+100)), self.new_bomb) 


    def old_fruit(self, args):    
        fruit = Fruit(*args)
        self.fruits.append(fruit)
        self.tag_bind(fruit.object, "<Enter>", fruit.delete) 

    def old_bomb(self, args):
        bomb = Bomb(*args)
        self.bombs.append(bomb)
        self.tag_bind(bomb.object, "<Enter>", bomb.delete) 


    def mouse_handler(self, event):
        # Calculates the mouse velocity using numerical differentiation: v = dx/dt
        if self.m_x and self.m_y:
            self.m_vel = ((event.x - self.m_x)/self.dt, (event.y - self.m_y)/self.dt)
        self.m_x = event.x
        self.m_y = event.y
        self.create_oval(self.m_x, self.m_y, self.m_x+10, self.m_y+10, fill='#f5d38c', outline="#f5d38c", tags=("mouse"))
        while len(self.find_withtag("mouse")) > 25:
               self.delete(min(self.find_withtag("mouse")))

    def check_cheat(self, key):
        self.key_history.append(key.keysym)
        if ''.join(self.key_history) == 'LeftRightLeftRightLeftRightDownDown':
            self.cheating = not self.cheating
            self.cheated = True
        elif ''.join(self.key_history) == 'LeftUpRightUpUpUp':
            self.g = 4
            self.cheated = True

    def pause(self, key):
        self.paused = not self.paused
        if self.paused:
            self.pause_label = Label(self, text="Paused", font=self.heading_font, bg="#f0d7a1", fg='black')
            self.pause_text = self.create_window(self.width/2, self.height/2 -30, anchor='center', window=self.pause_label)
            self.save_button = Button(self, text="Save Game", command=self.save_game, bg="#f0d7a1", highlightbackground="#f0d7a1")
            self.save_window = self.create_window(self.width/2, self.height/2 , anchor='center', window=self.save_button)
            self.resume_button = Button(self, text="Resume", command=lambda: self.pause(None), bg="#f0d7a1", highlightbackground="#f0d7a1")
            self.resume_window = self.create_window(self.width/2, self.height/2 + 30 , anchor='center', window=self.resume_button)
            self.lead_button = Button(self, text="Leaderboard", command=leaderboard, highlightbackground='#f0d7a1')
            self.lead_window = self.create_window(self.width/2, self.height/2 + 60, anchor='center', window=self.lead_button)
        
        else:
            self.delete(self.pause_text)
            self.delete(self.save_window)
            self.delete(self.resume_window)
            self.delete(self.lead_window)


    def save_game(self):
        vars = (self.lives, self.score, self.streak, list(self.hit_or_miss), [f.pack() for f in self.fruits], [b.pack() for b in self.bombs])
        file = filedialog.asksaveasfile('wb', defaultextension=".sav")
        pickle.dump(vars, file)
        file.close()

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
        game_over_label = Label(self, text="Game Over", font=self.heading_font, bg="#f0d7a1", fg='black')
        self.create_window(self.width/2, self.height/2 - 30, anchor='center', window=game_over_label)
        leaderboard = Button(self, text="Leaderboard", command=leaderboard, highlightbackground='#f0d7a1')
        self.create_window(self.width/2, self.height/2 , anchor='center', window=leaderboard)
        save_score = Button(self, text="Save Score to Leaderboard", command=self.save_score, highlightbackground='#f0d7a1')
        self.create_window(self.width/2, self.height/2 + 30, anchor='center', window=save_score)
        restart = Button(self, text="Exit", command=self.window.destroy, highlightbackground='#f0d7a1')
        self.create_window(self.width/2, self.height/2+60, anchor='center', window=restart)
        self.interval = 200
        self.game_ended = True

    def save_score(self):
        username = simpledialog.askstring("Enter your username", "Username:")
        with open("leaderboard.csv", 'a') as f:
            f.write(f"{username.lower()}, {int(self.score)}, {self.cheated}\n")



def interval(streak):
    if streak==0:
        interval = 2000
    elif streak==1:
        interval = 1500
    elif streak==2:
        interval = 1000
    else:
        interval = 1000*2.72**(-0.02*(streak-3))
    return int(interval)

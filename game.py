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
from leaderboard import show_leaderboard
import pickle


class Game(Canvas):
    """
    Inherits from Tkinter Canvas and holds all the game logic,
    variables and rendering
    """
    def __init__(self, window, w, h, lives=5, score=0, streak=0,
                 hit_or_miss=None, cheated=False, floor_cheat=False, 
                 g=9.81, fruit_size=60):
        """
        Initialise game variables and initialise the canvas windows
        for variables lives, streak and score
        """
        self.background_color = "#f0d7a1"
        self.mouse_trail_color = "#eddfc5"
        self.retro_font = font.Font(family="ArcadeClassic", size=20)
        self.heading_font = font.Font(
            family="TkHeadingFont", size=36, weight='bold')
        super().__init__(master=window, width=w, height=h,
                         background=self.background_color, cursor="star")
        self.window = window
        # Constants for the game physics are defined here
        fps = 120
        self.dt = 1 / fps
        # ppm: pixels per meter
        # is used to convert the metres used in the equations back to
        # pixels for rendering.
        self.ppm = 240
        # e: coefficient of restitution
        # used in Newton's Law of Restitution used to find the velocity
        # after a collision.
        self.e = 0.3
        self.sprite_sheet = Image.open("Fruit+.png")
        # g: acceleration due to gravity in metres per second.
        self.g = g
        self.width, self.height = w, h
        # Fruit diameter in pixels i.e. the width and height of the images.
        self.fruit_size = fruit_size
        # These lists are used to track the objects on the game canvas
        # and are then pickled into the save files.
        self.fruits = []
        self.bombs = []
        # Boolean values for game states
        self.floor_cheat = floor_cheat
        self.cheated = cheated
        self.paused = False
        self.boss_keyed = False
        self.game_ended = False
        # Interval between new fruits spawning in milliseconds
        self.interval = 2000
        # The indicies of the fruits from the sprite sheet which are used
        self.fruit_indicies = [0, 1, 2, 9, 12, 13, 17, 18, 19, 21, 22,
                               23, 26, 37]
        # Double-ended queue acting as memory to check for cheatcodes
        self.key_history = deque([], 8)
        # Double-ended queue used to calculate rolling accuracy to
        # dynamically update difficulty
        if hit_or_miss is None:
            self.hit_or_miss = deque([None for _ in range(50)], maxlen=50)
        else:
            self.hit_or_miss = deque(hit_or_miss, maxlen=50)
        # Initialise game variables and fonts
        self.lives = lives
        self.score = score
        self.streak = streak
        self.lv_content = Label(
            self, text=f"Lives: {self.lives}", bg=self.background_color,
            font=self.retro_font, fg='black')
        self.sc_content = Label(
            self, text=f"Score: {self.score}", bg=self.background_color,
            font=self.retro_font, fg='black')
        self.st_content = Label(
            self, text=f"Streak: {self.streak}", bg=self.background_color,
            font=self.retro_font, fg='black')
        self.lives_text = self.create_window(
            10, 10, anchor='nw', window=self.lv_content)
        self.score_text = self.create_window(
            self.width / 2, 10, anchor='n', window=self.sc_content)
        self.streak_text = self.create_window(
            self.width - 10, 10, anchor='ne', window=self.st_content)
        self.retro_font = font.Font(family="ArcadeClassic", size=20)
        self.heading_font = font.Font(
            family='TkHeadingFont', size=36, weight='bold')
        # Set the game controls to match those on the file
        with open('controls.txt', 'r') as file:
            self.controls = eval(file.read())
        # Start the update loop
        self.update()
        # Here, the mouse position and velocity vairables initialised.
        # These are used to calculate the score multiplier and project
        # fruit objects after slicing. Position is needed to calculate
        # velocity based on numerical differentiation with dt (time step).
        self.m_x = None
        self.m_y = None
        self.m_vel = (None, None)
        # Start taking mouse input to calculate mouse velocity
        self.bind("<Motion>", self.mouse_handler)

    def update(self):
        """
        Increments the interval based on player performance
        Slowly fades out the mouse trail
        Updates the game carianles and draws the labels to canvas
        Repeats every 0.2s
        """
        if not self.game_ended:
            self.interval = interval(self.streak)

        # Pop from the mouse trail
        try:
            self.delete(min(self.find_withtag("mouse")))
        except ValueError:
            pass

        # Update the labels with the new values of the game variables
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

    def key_in(self, key):
        """
        The function which handles all keyboard inputs and calls relevant
        functions. A unified input is needed to work with the Tkinter bind
        method which cannot be called multiple times with the same event and
        different commands.
        """
        self.check_cheat(key)
        if key.char == self.controls['pause']:
            self.pause(key)
        elif key.char == self.controls['boss']:
            self.boss_key(key)

    def new_fruit(self):
        """
        Generates a new fruit assuming the game is not paused.
        The function loops every interval with some random variation.
        """
        if self.paused:
            pass
        else:
            # Fruit object created. The sprite coordinates are inputted and
            # we multiply by 16 since that is the width of each sprite on
            # the sprite sheet.
            fruit = Fruit(sprite_coords=(choice(self.fruit_indicies) * 16, 16),
                          coords=(randint(self.fruit_size,
                                          self.width - self.fruit_size),
                                  self.height - self.fruit_size),
                          velocity=(uniform(-3, 3) * self.ppm,
                                    uniform(-6, -3) * self.ppm),
                          canvas=self)
            # Start tracking the fruit in case of game save event
            self.fruits.append(fruit)
            if not self.game_ended:
                self.tag_bind(fruit.object, "<Enter>", fruit.delete)
        # Spawns a new fruit after some time based on the difficulty
        self.after(max(0,
                       randint(self.interval - 100, self.interval + 100)),
                   self.new_fruit)

    def new_bomb(self):
        """
        Generates a new bomb assuming the game is not paused.
        The function loops once every 5 times compared to new_fruit.
        """
        if not self.game_ended:
            if self.paused:
                pass
            # Only spawn bombs if the player scores above 5,000
            elif self.score > 5_000:
                bomb = Bomb(
                    (randint(self.fruit_size, self.width - self.fruit_size),
                     self.height - self.fruit_size),
                    (uniform(-3, 3) * self.ppm, uniform(-6, -4) * self.ppm),
                    self)
                # Delete bomb when mouse hovers over it
                self.tag_bind(bomb.object, "<Enter>", bomb.delete)
                # New bomb is projected approximately once per five fruits
            self.after(max(0, 5 * randint(self.interval - 100,
                       self.interval + 100)), self.new_bomb)

    def old_fruit(self, args):
        """
        Creates a fruit with data from a save file
        """
        fruit = Fruit(*args)
        # Start tracking the old fruit again
        self.fruits.append(fruit)
        self.tag_bind(fruit.object, "<Enter>", fruit.delete)

    def old_bomb(self, args):
        """
        Creates a bomb with data from a save file
        """
        bomb = Bomb(*args)
        # Start tracking the old bomb again
        self.bombs.append(bomb)
        self.tag_bind(bomb.object, "<Enter>", bomb.delete)

    def mouse_handler(self, event):
        """
        The function that is called whenever the mouse moves.
        It calculates the mouse velocity and maintains the mouse trail
        """
        # Calculates the mouse velocity using numerical differentiation:
        # v = dx/dt
        if self.m_x and self.m_y:
            self.m_vel = ((event.x - self.m_x) / self.dt,
                          (event.y - self.m_y) / self.dt)
        # Saves the current mouse position to the Game object
        self.m_x = event.x
        self.m_y = event.y
        # Creates a shape for the mouse trail
        random_int = randint(0, 1)
        if random_int:
            self.create_oval(self.m_x, self.m_y, self.m_x + 10,
                             self.m_y + 10,
                             fill=self.mouse_trail_color,
                             outline=self.mouse_trail_color,
                             tags=("mouse"))
        else:
            self.create_rectangle(self.m_x, self.m_y, self.m_x + 10,
                                  self.m_y + 10,
                                  fill=self.mouse_trail_color,
                                  outline=self.mouse_trail_color,
                                  tags=("mouse"))
        # If we just generated the 26th element of the mouse trial,
        # delete the oldest element.
        while len(self.find_withtag("mouse")) > 25:
            self.delete(min(self.find_withtag("mouse")))

    def check_cheat(self, key):
        """
        The command that accepts all keyboard input and determines which,
        if any, cheatcode(s) are being used
        """
        self.key_history.append(key.keysym)
        # This cheatcode adds a floor
        if ''.join(self.key_history) == 'LeftRightLeftRightLeftRightDownDown':
            self.floor_cheat = not self.floor_cheat
            self.cheated = True
            self.key_history.clear()
        # This cheatcode reduces gravity and scales down velocity to reduce
        # the number of fruits bouncing off of the ceiling
        elif ''.join(self.key_history)[-17:] == 'LeftUpRightUpUpUp':
            self.g = 1
            self.cheated = True
            self.key_history.clear()
        # This cheat reduces the size of the fruits
        elif ''.join(self.key_history)[-12:] == 'DownDownDown':
            self.fruit_size = 30
            self.cheated = True
            self.key_history.clear()
        # This cheat increases the size of the fruits
        elif ''.join(self.key_history)[-10:] == 'UpUpUpUpUp':
            self.fruit_size = 90
            self.cheated = True
            self.key_history.clear()
        # Bonus life cheat
        elif ''.join(self.key_history)[-10:] == 'UpLeftUpUp':
            self.lives += 1
            self.key_history.clear()

    def pause(self, key):
        """
        The function to pause and unpause the game. It draws/deletes the
        relevant labels and buttons to the screen
        """
        self.paused = not self.paused
        if self.paused:
            self.pause_label = Label(
                self, text="Paused", font=self.heading_font,
                bg=self.background_color, fg='black')
            self.pause_text = self.create_window(
                self.width / 2, self.height / 2 - 30, anchor='center',
                window=self.pause_label)
            self.save_button = Button(
                self, text="Save Game", command=self.save_game,
                bg=self.background_color,
                highlightbackground=self.background_color)
            self.save_window = self.create_window(
                self.width / 2, self.height / 2, anchor='center',
                window=self.save_button)
            self.resume_button = Button(
                self, text="Resume",
                command=lambda: self.pause(None),
                bg=self.background_color,
                highlightbackground=self.background_color)
            self.resume_window = self.create_window(
                self.width / 2, self.height / 2 + 30, anchor='center',
                window=self.resume_button)
            self.lead_button = Button(
                self, text="Leaderboard", command=show_leaderboard,
                highlightbackground='#f0d7a1')
            self.lead_window = self.create_window(
                self.width / 2, self.height / 2 + 60, anchor='center',
                window=self.lead_button)

        else:
            self.delete(self.pause_text)
            self.delete(self.save_window)
            self.delete(self.resume_window)
            self.delete(self.lead_window)

    def save_game(self):
        """
        Saves the game by pickling a list of variables including fruit
        and bomb data
        """
        vars = (self.lives, self.score, self.streak, list(self.hit_or_miss), 
                self.floor_cheat, self.g, self.fruit_size, self.cheated,
                [f.pack() for f in self.fruits],
                [b.pack() for b in self.bombs])
        file = filedialog.asksaveasfile('wb', defaultextension=".sav")
        pickle.dump(vars, file)
        file.close()

    def boss_key(self, key):
        """
        Function which is run once the boss key is pressed. It creates a new
        window and displays a screenshot of a spreadsheet.
        """
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
            screenshot = Image.open("boss.jpg")
            screenshot = screenshot.resize((w, h), Image.Resampling.BICUBIC)
            img = ImageTk.PhotoImage(master=canvas, image=screenshot)
            canvas.pack(expand=True)
            canvas.create_image(0, 0, image=img, anchor='nw')
            self.boss_window.bind("<Key-b>", self.boss_key)
            # Ensure the game is paused when the boss window is opened
            if not self.paused:
                self.pause(key)
            self.boss_window.mainloop()
        else:
            self.boss_window.destroy()

    def game_over(self):
        """
        Creates and draws all the buttons and labels for the game over screen.
        """
        game_over_label = Label(
            self, text="Game Over", font=self.heading_font,
            bg=self.background_color, fg='black')
        self.create_window(self.width / 2, self.height / 2 - 30,
                           anchor='center', window=game_over_label)
        lead_button = Button(self, text="Leaderboard",
                             command=show_leaderboard,
                             highlightbackground='#f0d7a1')
        self.create_window(self.width / 2, self.height / 2,
                           anchor='center', window=lead_button)
        save_score = Button(self, text="Save Score to Leaderboard",
                            command=self.save_score,
                            highlightbackground='#f0d7a1')
        self.create_window(self.width / 2, self.height / 2 + 30,
                           anchor='center', window=save_score)
        restart = Button(
            self, text="Exit", command=self.window.destroy,
            highlightbackground='#f0d7a1')
        self.create_window(self.width / 2, self.height / 2 + 60,
                           anchor='center', window=restart)
        self.interval = 200
        self.game_ended = True

    def save_score(self):
        """
        Asks the user for a name and saves information to the
        leaderboard.csv file
        """
        username = simpledialog.askstring("Save your Score",
                                          "Username:")
        with open("leaderboard.csv", 'a') as f:
            f.write(
                f"{username.lower()}, {int(self.score)}, {self.cheated}\n"
                )


def interval(streak):
    """
    A function which defines the interval from streak (player performance)
    """
    if streak == 0:
        interval = 2000
    elif streak == 1:
        interval = 1500
    elif streak == 2:
        interval = 1250
    else:
        # Uses an exponential decay function
        interval = 1250 * 2.72**(-0.02 * (streak - 3))
    return int(interval)

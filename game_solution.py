from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from random import randint, randrange, choice
from collections import deque


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
        self.main_game.new_fruit() 
        self.main_game.pack()
        game_window.bind("<Key>", self.main_game.pause)
        game_window.bind("<Key>", self.main_game.boss_key)
        game_window.bind("<Key>", self.main_game.check_cheat)
        self.game_window = game_window
        game_window.mainloop()


class Game(Canvas):
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
        self.fruit_size = 48             # Fruit diameter in pixels
        self.cheating = False            # Boolean value
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
        with open('controls.txt', 'r') as file:
            for bind in file.readlines():
                bind = bind.split(",")
                self.controls[bind[0]] = bind[1]
        self.update()
        # self.labels = [self.lives_text, self.score_text, self.streak_text]
        self.bind("<Motion>", self.mouse_velocity)

    def create_label(self, text, x, y, anchor):
        label = Label(self.window, text=text, font=self.font)
        self.object = self.create_window(x, y, anchor=anchor, window=label)
        return label

    def update(self):
        self.lives_text['textvariable'] = self.lv_content
        self.score_text['textvariable'] = self.sc_content
        self.streak_text['textvariable'] = self.st_content

        self.lv_content.set(f"Lives: {self.lives}")
        self.sc_content.set(f"Score: {self.score}")
        self.st_content.set(f"Streak: {self.streak}")
        if self.streak:
            self.interval = min(2000, int(10000/self.streak))
        else:
            self.interval = 2000
        self.after(500, self.update)

    def new_fruit(self):
        fruit = Fruit(  (choice(self.fruit_indicies)*16, 16),
                        (randrange(self.fruit_size, self.width-self.fruit_size), self.height-self.fruit_size),
                        (randrange(-3, 3)*self.ppm, randrange(-7, -4)*self.ppm),
                        self)
        self.tag_bind(fruit.object, "<Enter>", fruit.delete)    # Delete fruit when mouse hovers over it

        # New fruit is projected at a random interval = INTERVAL +/- 0.5 seconds 
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
            self.canvas.cheating = True

    def pause(self, key):
        if key.char == self.controls['pause']:
            self.paused = not self.paused
            print("PAUSE")

    def boss_key(self, key):
        if key.char == self.controls['boss']:
            self.boss_keyed = not self.boss_keyed
            print("BOSS")
class Fruit:
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image=False):
        self.canvas = canvas
        self.height, self.width = canvas.height, canvas.width
        self.s_x, s_y = sprite_coords
        self.x, self.y = coords
        self.v_x, self.v_y = velocity
        if self.s_x//16 == 26:
            scale = 1.5
        else:
            scale = 1
        self.sprite = canvas.sprite_sheet.crop((self.s_x, s_y, self.s_x+16, s_y+16))
        self.sprite = self.sprite.resize((int(self.canvas.fruit_size*scale), 
                                        int(self.canvas.fruit_size*scale)), 
                                        Image.Resampling.NEAREST)
        if flip_image:
            self.sprite = self.sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.image = ImageTk.PhotoImage(master=self.canvas, image=self.sprite)
        self.object = canvas.create_image(self.x, self.y, image=self.image, anchor='center')
        self.bbox = self.canvas.bbox(self.object)
        self.deleted = False
        self.tick()

    def delete(self, event):
        self.deleted = True
        self.canvas.streak += 1
        # Generates two halves of chopped fruit
        left = ChoppedFruit((self.s_x, 5*16),
                (self.canvas.coords(self.object)[0]-16, self.canvas.coords(self.object)[1]),
                (0.5*self.canvas.m_vel[0]-50, 0.5*self.canvas.m_vel[1]),
                self.canvas, False)
        right = ChoppedFruit((self.s_x, 5*16),
                (self.canvas.coords(self.object)[0]+16, self.canvas.coords(self.object)[1]),
                (0.5*self.canvas.m_vel[0]+50, 0.5*self.canvas.m_vel[1]),
                self.canvas, True)
        self.canvas.tag_bind(left.object, "<Enter>", left.delete) 
        self.canvas.tag_bind(right.object, "<Enter>", right.delete) 
        # Removes the old sprite from the canvas
        self.canvas.delete(self.object)
    
    def displace(self):
        # Main physics function which handles collisions with walls and calculates displacenet 
        # Uses SUVAT equations and Newton's law of restitution
        left, top, right, bottom = self.bbox
        self.grounded = bottom >= self.height
        dy, dx = 0, 0
        if left <= 0:
            self.v_x = -self.v_x*self.canvas.e
            dx = -left
        if right >= self.width:
            self.v_x = -self.v_x*self.canvas.e
            dx = -(right-self.width)
        if top <= 0:
            self.v_y = -self.v_y*self.canvas.e
            dy = -top
        if self.canvas.cheating and self.grounded:
            self.v_y = -self.v_y*self.canvas.e
            dy = -(bottom-self.height)
        if top >= self.height:
            self.deleted = True
            if self.__class__.__name__ == "Fruit":
                self.canvas.streak = 0
                self.canvas.lives -= 1
        if not(self.grounded and self.canvas.cheating):
            self.v_y += self.canvas.g*self.canvas.ppm*self.canvas.dt
        dx += self.v_x*self.canvas.dt
        dy += self.v_y*self.canvas.dt
        return (dx, dy)


    def tick(self):
        # This function updates the positino of the fruit
        self.canvas.move(self.object, *self.displace())
        self.bbox = self.canvas.bbox(self.object)
        if not self.deleted:
            self.canvas.after(int(1000*self.canvas.dt), self.tick)

class ChoppedFruit(Fruit):
    # Chopped fruit class has a redefined delete function as we dont want an infinite stream of fruit-halves
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image):
        super().__init__(sprite_coords, coords, velocity, canvas, flip_image)

    def delete(self, _):
        if self.grounded:
            self.deleted = True
            self.canvas.delete(self.object)

# Driver code to initialise the app
app = App()

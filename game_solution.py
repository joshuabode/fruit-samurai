from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from tkinter import font
from PIL import ImageTk, Image, ImageDraw
from random import randint, choice, uniform
from collections import deque
from fruit import Fruit, ChoppedFruit
from game import Game

"""
Free sprite sheet sourced from here: https://ninjikin.itch.io/fruit?download
Font from: https://www.dafont.com/arcade-classic-2.font 
Backgrounds from : https://limezu.itch.io/moderninteriors
https://limezu.itch.io/kitchen
"""



class App():
    # TODO: Add the initial game menu

    def __init__(self):
        start_window = Tk()
        self.retro_font = font.Font(family="ArcadeClassic", size=20)
        self.heading_font = font.Font(family="TkHeadingFont", size=36, weight='bold')
        start_window.title("Fruit Samurai")
        self.menu = start_window
        self.init_menu()

    def init_menu(self):
        root = self.menu
        img = ImageTk.PhotoImage(image=Image.open('background.png'))
        image_label = Label(master=root, image=img)
        image_label.place(x=0, y=0)
        title = Label(root, text="Fruit Samurai", font=self.heading_font, bg="#bbefe3", fg='black')
        buttons = [None for _ in range(6)]
        # b_images = [ImageTk.PhotoImage(image=Image.open("b1.png")),
        #             ImageTk.PhotoImage(image=Image.open("b2.png")),
        #             ImageTk.PhotoImage(image=Image.open("b3.png")),
        #             ImageTk.PhotoImage(image=Image.open("b4.png")),
        #             ImageTk.PhotoImage(image=Image.open("b5a.png")),]
        buttons[0] = Button(root, text="New Game", command=self.new_game, highlightbackground='#bbefe3')
        buttons[1] = Button(root, text="Load Game", command=self.load_game, highlightbackground='#bbefe3')
        buttons[2] = Button(root, text="Settings", command=self.settings, highlightbackground='#bbefe3')
        buttons[3] = Button(root, text="How to Play", command=self.tutorial, highlightbackground='#bbefe3')
        buttons[4] = Button(root, text="Quit", command=self.menu.destroy, highlightbackground='#bbefe3')
        buttons[5] = Button(root, text="Leaderboard", command=self.leaderboard, highlightbackground='#bbefe3')
        title.grid(column=0, row=0, padx=100)
        for i, button in enumerate(buttons):
            button.grid(column=0, row=i+1)
        root.mainloop()

    def new_game(self, game_data=None):
        game_window = Toplevel()
        game_window.title("Fruit Samurai")
        game_window.resizable(False, False)
        w, h = 960, 540
        if game_data:
            self.main_game = Game(game_window, w, h, *game_data[:-1])
            print(game_data[-1], type(game_data[-1]))
            for fruit in game_data[-1]:
               fruit = eval(fruit)
               print(fruit, type(fruit))
               fruit[3] = self.main_game
               self.main_game.old_fruit(fruit) 
        else:
            self.main_game = Game(game_window, w, h)
            self.main_game.new_fruit() 
        game_window.bind("<Key>", self.main_game.key_in)
        self.main_game.pack()
        self.game_window = game_window
        game_window.mainloop()

    def load_game(self):
        file = filedialog.askopenfile(mode='r')
        self.new_game(eval(file.read()))
    
    def settings(self):
        with open('controls.txt', 'r') as file:
            self.controls = eval(file.read())
        settings_window = Toplevel()
        settings_window.resizable(False, False)
        settings_window.title("Settings")
        title = Label(settings_window, text="Settings", font=self.heading_font)
        title.grid(column=0, row=0, columnspan=2, pady=15, padx=15)


        pause_var = StringVar(value=self.controls['pause'])
        self.pause_sel = ttk.Combobox(settings_window, textvariable=pause_var, width=2)
        pause_lab = Label(settings_window, text="Pause Keybind:")
        self.pause_sel['values'] = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
        pause_lab.grid(column=0, row=1)
        self.pause_sel.grid(column=1, row=1)
        
        boss_var = StringVar(value=self.controls['boss'])
        self.boss_sel = ttk.Combobox(settings_window, textvariable=boss_var, width=2)
        boss_lab = Label(settings_window, text="Boss Keybind:")
        self.boss_sel['values'] = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
        boss_lab.grid(column=0, row=2)
        self.boss_sel.grid(column=1, row=2)

        save_button = Button(settings_window, text="Save", command=self.save_binds)
        save_button.grid(row=3, columnspan=2)
        self.settings_window = settings_window
        settings_window.mainloop()
        
    def save_binds(self):
        pause = self.pause_sel.get()
        boss = self.boss_sel.get()
        if pause != boss:
            self.controls = {'pause': pause, 'boss': boss}
            with open('controls.txt', 'w') as file:
                file.write(str(self.controls))
            self.settings_window.destroy()
        else:
            messagebox.showerror("You cannot set the pause and boss key binds to the same key")

    def tutorial(self):
        tutorial = Toplevel()
        c = Tutorial(tutorial, 960, 540)
        c.pack()
        c.new_fruit()
        tutorial.mainloop()

    def leaderboard(self):
        leaderboard = Toplevel()
        leaderboard.mainloop()

    
# Driver code to initialise the app
app = App()
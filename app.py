"""
APP.PY

Defines the App object
"""

import pickle
from random import randint
from tkinter import Tk, Toplevel, Label, Button, StringVar
from tkinter import ttk, font, messagebox, filedialog
from PIL import ImageTk, Image
from game import Game
from leaderboard import show_leaderboard


class App():

    def __init__(self):
        """
        Outputs the skeleton of the main menu window
        """
        start_window = Tk()
        start_window.geometry("400x600")
        start_window.configure(background='#caaeba')
        start_window.resizable = (False, False)
        self.retro_font = font.Font(family="ArcadeClassic", size=20)
        self.heading_font = font.Font(
            family="TkHeadingFont", size=36, weight='bold')
        start_window.title("Fruit Samurai")
        self.menu = start_window
        # Holds the ID for the starting countdown screen
        self.countdown_window = None
        self.init_menu()

    def init_menu(self):
        """
        Draws the start screen
        """
        root = self.menu
        img = ImageTk.PhotoImage(image=Image.open(
            'assets/kitchen.png').resize((400, 400), Image.Resampling.NEAREST))
        image_label = Label(master=root, image=img,
                            highlightthickness=0, borderwidth=0)
        image_label.place(x=0, y=200)
        title = Label(root, text="Fruit Samurai",
                      font=self.heading_font, bg="#caaeba", fg='white')
        # Generate the buttons
        buttons = [
            Button(root, text="New Game", command=self.new_game,
                   highlightbackground='#caaeba'),
            Button(root, text="Load Game", command=self.load_game,
                   highlightbackground='#caaeba'),
            Button(root, text="Settings", command=self.settings,
                   highlightbackground='#caaeba'),
            Button(root, text="How to Play", command=self.tutorial,
                   highlightbackground='#caaeba'),
            Button(root, text="Quit", command=self.menu.destroy,
                   highlightbackground='#caaeba'),
            Button(root, text="Leaderboard", command=show_leaderboard,
                   highlightbackground='#caaeba')
        ]

        title.grid(column=0, row=0, padx=50)
        # Display the buttons
        for i, button in enumerate(buttons):
            button.grid(column=0, row=i+1)
        root.mainloop()

    def load_game(self):
        """
        Parses save file data and then passes it to the new_game function
        """
        file = filedialog.askopenfile(mode='rb')
        self.new_game(pickle.load(file))

    def new_game(self, game_data=None):
        """
        Initialises a game/canvas objects or loadsƒ a game from data
        """
        game_window = Toplevel()
        game_window.title("Fruit Samurai")
        w, h = 960, 540
        if not game_data:
            self.main_game = Game(game_window, w, h)
            # Spawn a new fruit after a 3 second delay with GUI countdown
            self.countdown(3, self.main_game.new_fruit)
            self.main_game.new_bomb()
        else:    # This block is executed when a game is loaded
            # Trim the fruits and bombs from the saved data and pass the rest
            # to the Game generator
            self.main_game = Game(game_window, w, h, *game_data[:-3])

            # game_data[-3] is the list of ChoppedFruit data from the game data
            for slice in game_data[-3]:
                slice[3] = self.main_game
                self.main_game.old_slice(slice)
            # game_data[-2] is the list of fruit data from the game data
            for fruit in game_data[-2]:
                fruit[3] = self.main_game
                self.main_game.old_fruit(fruit)
            # game_data[-1] is the list of bomb data from the game data
            for bomb in game_data[-1]:
                bomb[2] = self.main_game
                self.main_game.old_bomb(bomb)
            # Restart the spawn loops for fruits and bombs
            self.main_game.after(max(0, randint(
                self.main_game.interval-100, self.main_game.interval+100)),
                self.main_game.new_fruit)
            self.main_game.after(max(0, 5*randint(self.main_game.interval -
                                 100, self.main_game.interval+100)),
                                 self.main_game.new_fruit)
        game_window.bind("<Key>", self.main_game.key_in)
        self.main_game.pack()
        self.game_window = game_window
        game_window.mainloop()

    def countdown(self, n, command):
        self.main_game.delete(self.countdown_window)
        if n == 0:
            command()
        else:
            label = Label(self.main_game, text=str(n), font=(
                'ArcadeClassic', 144),
                background=self.main_game.background_color,
                foreground="black")
            self.countdown_window = self.main_game.create_window(
                self.main_game.width/2, self.main_game.height/2,
                anchor="center", window=label)
            self.main_game.after(1000, lambda: self.countdown(n-1, command))

    def settings(self):
        """
        Initialises the settings window
        """
        with open('controls.txt', 'r') as file:
            # Since the contents of the controls file is a string
            # representation of a dict, we can just unpack with eval
            self.controls = eval(file.read())
        settings_window = Toplevel()
        settings_window.resizable(False, False)  # Fix the size of the window
        settings_window.title("Settings")
        title = Label(settings_window, text="Settings", font=self.heading_font)
        title.grid(column=0, row=0, columnspan=2, pady=15, padx=15)

        # Initialise and show the combo-select boxes for the two customisable
        # controls

        pause_var = StringVar(value=self.controls['pause'])
        self.pause_sel = ttk.Combobox(
            settings_window, textvariable=pause_var, width=2)
        pause_lab = Label(settings_window, text="Pause Keybind:")
        self.pause_sel['values'] = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                    'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                    'q', 's', 't', 'u', 'v', 'w', 'x', 'y',
                                    'z')
        pause_lab.grid(column=0, row=1)
        self.pause_sel.grid(column=1, row=1)

        boss_var = StringVar(value=self.controls['boss'])
        self.boss_sel = ttk.Combobox(
            settings_window, textvariable=boss_var, width=2)
        boss_lab = Label(settings_window, text="Boss Keybind:")
        self.boss_sel['values'] = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                   'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                   'q', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')
        boss_lab.grid(column=0, row=2)
        self.boss_sel.grid(column=1, row=2)

        # Show the save button

        save_button = Button(settings_window, text="Save",
                             command=self.save_binds)
        save_button.grid(row=3, columnspan=2)
        # Save the window to allow for deletion after input validation
        self.settings_window = settings_window
        settings_window.mainloop()

    def save_binds(self):
        """
        Validates that keybinds are unique and if so, saves them to an
        external file
        """
        pause = self.pause_sel.get()
        boss = self.boss_sel.get()
        if pause != boss:
            self.controls = {'pause': pause, 'boss': boss}
            with open('controls.txt', 'w') as file:
                file.write(str(self.controls))
            self.settings_window.destroy()
        else:
            messagebox.showerror(
                "You cannot set the pause and boss key binds to the same key")

    def tutorial(self):
        """
        Shows text instructions from the tutorial.txt file
        """
        tutorial = Toplevel()
        tutorial.geometry("600x200")
        title = Label(tutorial, text="How to Play", font=self.heading_font)
        title.pack()
        with open("tutorial.txt", 'r') as f:
            lines = f.readlines()
            for line in lines:
                label = Label(tutorial, text=line)
                label.pack()

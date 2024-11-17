from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from tkinter import font
from PIL import ImageTk, Image
from random import randint
from game import Game
import pickle

class App():
    # TODO: Add the initial game menu

    def __init__(self):
        start_window = Tk()
        start_window.geometry("400x600")
        start_window.configure(background='white')
        self.retro_font = font.Font(family="ArcadeClassic", size=20)
        self.heading_font = font.Font(family="TkHeadingFont", size=36, weight='bold')
        start_window.title("Fruit Samurai")
        self.menu = start_window
        self.init_menu()

    def init_menu(self):
        root = self.menu
        img = ImageTk.PhotoImage(image=Image.open('background.png').resize((400, 400), Image.Resampling.NEAREST))
        image_label = Label(master=root, image=img, highlightthickness=0, borderwidth=0)
        image_label.place(x=0, y=200)
        title = Label(root, text="Fruit Samurai", font=self.heading_font, bg="white", fg='black')
        buttons = [None for _ in range(6)]
        # b_images = [ImageTk.PhotoImage(image=Image.open("b1.png")),
        #             ImageTk.PhotoImage(image=Image.open("b2.png")),
        #             ImageTk.PhotoImage(image=Image.open("b3.png")),
        #             ImageTk.PhotoImage(image=Image.open("b4.png")),
        #             ImageTk.PhotoImage(image=Image.open("b5a.png")),]
        buttons[0] = Button(root, text="New Game", command=self.new_game, highlightbackground='white')
        buttons[1] = Button(root, text="Load Game", command=self.load_game, highlightbackground='white')
        buttons[2] = Button(root, text="Settings", command=self.settings, highlightbackground='white')
        buttons[3] = Button(root, text="How to Play", command=self.tutorial, highlightbackground='white')
        buttons[4] = Button(root, text="Quit", command=self.menu.destroy, highlightbackground='white')
        buttons[5] = Button(root, text="Leaderboard", command=self.leaderboard, highlightbackground='white')
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
            self.main_game = Game(game_window, w, h, *game_data[:-2])
            for fruit in game_data[-2]:
               fruit[3] = self.main_game
               self.main_game.old_fruit(fruit) 
            self.main_game.after(max(0, randint(self.main_game.interval-100, self.main_game.interval+100)), self.main_game.new_fruit) 
            for bomb in game_data[-1]:
                bomb[2] = self.main_game
                self.main_game.old_bomb(bomb)
        else:
            self.main_game = Game(game_window, w, h)
            self.main_game.new_fruit()
            self.main_game.new_bomb() 
        game_window.bind("<Key>", self.main_game.key_in)
        self.main_game.pack()
        self.game_window = game_window
        game_window.mainloop()

    def load_game(self):
        file = filedialog.askopenfile(mode='rb')
        self.new_game(pickle.load(file))
    
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
        tutorial.geometry("600x200")
        title = Label(tutorial, text="How to Play", font=("TkHeaadingFont", 36))
        title.pack()
        with open("tutorial.txt", 'r') as f:
            lines = f.readlines()
            for line in lines:
                label = Label(tutorial, text=line)
                label.pack()


    def leaderboard(self):
        leaderboard = Toplevel()
        with open("leaderboard.csv", 'r') as f:
            scorelist = f.readlines()[1:]
        for i, entry in enumerate(scorelist):
            entry = entry.replace("\n", '').split(", ")
            entry[1] = int(entry[1])
            scorelist[i] = entry
        scorelist = [score for score in scorelist if score[2] != 'True']
        scorelist.sort(key=lambda x: x[1], reverse=True)
        title = Label(leaderboard, text="Leaderboard", font=("ArcadeClassic", 36))
        title.grid(row=0, column=0, columnspan=2)
        for i in range(10):
            try:
                name_l = Label(leaderboard, text=str(scorelist[i][0]), font=('ArcadeClassic', 20))
                name_l.grid(row=i+1, column=0, sticky='w', padx=20)
                score_l = Label(leaderboard, text=str(scorelist[i][1]), font=('ArcadeClassic', 20))
                score_l.grid(row=i+1, column=1, sticky='w', padx=20)
            except IndexError:
                pass
        leaderboard.mainloop()
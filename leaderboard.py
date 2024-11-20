"""
LEADERBOARD.PY

Contains the function for creating the leaderboard window.
Loads data from the csv file and parses it  into tkinter labels, filtering
out cheaters
"""

from tkinter import Toplevel, Label
from tkinter import font


def show_leaderboard():
    """
    Shows the leaderboard window
    """
    leaderboard = Toplevel()
    heading_font = font.Font(family="ArcadeClassic", size=36)
    retro_font = font.Font(family="ArcadeClassic", size=20)
    with open("leaderboard.csv", 'r', encoding='utf-8') as f:
        scorelist = f.readlines()[1:]       # Trims the csv header row

    # Parses the csv data to a list and converts the score values to integers
    for i, entry in enumerate(scorelist):
        entry = entry.replace("\n", '').split(", ")
        entry[1] = int(entry[1])
        scorelist[i] = entry

    scorelist = [score for score in scorelist if score[2] !=
                 'True']    # Removes cheaters from the leaderboard
    # Sort in descending order of score
    scorelist.sort(key=lambda x: x[1], reverse=True)
    title = Label(leaderboard, text="Leaderboard", font=heading_font)
    title.grid(row=0, column=0, columnspan=2)
    for i in range(10):
        try:
            name_l = Label(
                leaderboard, text=f"{i+1}. {scorelist[i][0]}", font=retro_font)
            name_l.grid(row=i+1, column=0, sticky='w', padx=20)
            score_l = Label(leaderboard, text=str(
                scorelist[i][1]), font=retro_font)
            score_l.grid(row=i+1, column=1, sticky='w', padx=20)
        except IndexError:
            break
    leaderboard.mainloop()

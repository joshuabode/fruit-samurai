from PIL import Image
from math import ceil

bg = Image.new('RGBA', (960, 540))
tile = Image.open("tile.png")
for i in range(ceil(960/48)):
    for j in range(ceil(540/48)):
        bg.paste(tile, (i*48, j*48))

bg.save("background.png")
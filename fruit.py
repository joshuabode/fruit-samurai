"""
FRUIT.PY

Defines the Fruit object
"""

from PIL import ImageTk, Image

class Fruit:
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image=False):
        """
        Saves input variables as properties and adds the fruit to canvas
        """
        self.grounded = False
        self.canvas = canvas
        self.height, self.width = canvas.height, canvas.width
        self.x, self.y = coords
        # Numbers encoding the position of the sprite on the sprite sheet
        self.s_x, self.s_y = sprite_coords 
        self.velocity_x, self.velocity_y = velocity
        self.flip_image = flip_image
        if self.s_x//16 == 26:      # If the fruit is a watermelon, scale the image up slightly
            scale = 1.5
        else:
            scale = 1
        self.sprite = canvas.sprite_sheet.crop((self.s_x, self.s_y, self.s_x+16, self.s_y+16))
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
        """
        Removes the base fruit from canvas and stops tracking it for the save file.
        Spawns two chopped fruit halves
        Alters the game variables lives and streak
        """
        self.deleted = True
        if not self.canvas.paused:
            self.canvas.streak += 1
            if self.s_x//16 == 2:
                self.canvas.lives += 1
            self.canvas.hit_or_miss.append(True)
            self.canvas.score += self.canvas.streak*0.2*max(10, (0.1*(self.canvas.m_vel[0]**2 + self.canvas.m_vel[1]**2)**0.5))
            # Generates two halves of chopped fruit
            left = ChoppedFruit((self.s_x, 5*16),       # The sprite's 
                    (self.canvas.coords(self.object)[0]-16, self.canvas.coords(self.object)[1]),
                    (0.2*self.canvas.m_vel[0]-50, 0.2*self.canvas.m_vel[1]),
                    self.canvas, False)
            right = ChoppedFruit((self.s_x, 5*16),
                    (self.canvas.coords(self.object)[0]+16, self.canvas.coords(self.object)[1]),
                    (0.2*self.canvas.m_vel[0]+50, 0.2*self.canvas.m_vel[1]),
                    self.canvas, True)
            # Start tracking the chopped halves in case of game save
            self.canvas.fruits.append(left)
            self.canvas.fruits.append(right)
            self.canvas.tag_bind(left.object, "<Enter>", left.delete) 
            self.canvas.tag_bind(right.object, "<Enter>", right.delete) 
            # Removes the old sprite from the canvas
            self.canvas.fruits.remove(self)
            self.canvas.delete(self.object)
    
    def displace(self):
        """
        Main physics function which handles collisions with walls and
        calculates displacement.
        Uses SUVAT equations and Newton's law of restitution.
        Deletes the object when it falls below the screen
        """
        left, top, right, bottom = self.bbox
        self.grounded = bottom >= self.height
        dy, dx = 0, 0
        # Left wall collision
        if left <= 0:
            self.velocity_x = -self.velocity_x * self.canvas.e
            dx = -left
        # Right wall collision
        if right >= self.width:
            self.velocity_x = -self.velocity_x * self.canvas.e
            dx = -(right - self.width)
        # Ceiling collision
        if top <= 0:
            self.velocity_y = -self.velocity_y * self.canvas.e
            dy = -top
        # Optional floor collision if the floor cheat is being used
        if self.canvas.floor_cheat and self.grounded:
            self.velocity_y = -self.velocity_y * self.canvas.e
            dy = -(bottom - self.height)
        # Delete the bomb if it exits the game screen
        if top >= self.height:
            # We only penalise the player if the object is a fruit
            # (rather than a chopped fruit half)
            if self.__class__.__name__ == "Fruit":
                self.canvas.streak = 0
                self.canvas.hit_or_miss.append(False)
                self.canvas.lives -= 1
                if not self.canvas.game_ended:
                    self.canvas.configure(bg="red")
                    self.canvas.after(
                        250, lambda: self.canvas.configure(bg="#f0d7a1")
                    )
            self.deleted = True
            self.canvas.fruits.remove(self)
        # Update vertical velocity based on acceleration
        if not (self.grounded and self.canvas.floor_cheat):
            self.velocity_y += self.canvas.g * self.canvas.ppm * self.canvas.dt
        # Update displalcement
        dx += self.velocity_x * self.canvas.dt
        dy += self.velocity_y * self.canvas.dt
        # Update position
        self.x += dx
        self.y += dy
        # Return displacement to be consumed by Canvas.move
        return dx, dy


    def tick(self):
        """
        This function updates the position of the object
        """
        if not self.deleted:
            if self.canvas.paused:
                pass
            else:
                self.canvas.move(self.object, *self.displace())
                # Update the collision box
                self.bbox = self.canvas.bbox(self.object)
            # Tick rate is set to the dt variable
            self.canvas.after(int(1000 * self.canvas.dt), self.tick)

    def pack(self):
        """
        This function returns a list of object properties to be pickled into
        the save file
        """
        return [(self.s_x, self.s_y), (self.x, self.y), (self.velocity_x, self.velocity_y),
                 None, self.flip_image]

class ChoppedFruit(Fruit):
    """
    Chopped fruit class has a redefined delete function as we don't want to
    keep spawning fruit halves
    """
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image):
        super().__init__(sprite_coords, coords, velocity, canvas, flip_image)

    def delete(self, _):
        if self.grounded:
            self.deleted = True
            self.canvas.fruits.remove(self)
            self.canvas.delete(self.object)
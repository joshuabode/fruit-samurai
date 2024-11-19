"""
BOMB.PY

Defines the Bomb object
"""

from PIL import Image, ImageTk
class Bomb:
    def __init__(self, coords, velocity, canvas):
        """
        Saves input variables as properties and adds the bomb to canvas
        """
        self.grounded = False
        self.canvas = canvas
        self.height, self.width = canvas.height, canvas.width
        self.x, self.y = coords
        self.velocity_x, self.velocity_y = velocity
        self.sprite = Image.open("bomb.png")
        self.sprite = self.sprite.resize((int(self.canvas.fruit_size), 
                                            int(self.canvas.fruit_size)), 
                                            Image.Resampling.NEAREST)
        self.image = ImageTk.PhotoImage(master=self.canvas, image=self.sprite)
        self.object = canvas.create_image(self.x, self.y, image=self.image, anchor='center')
        self.bbox = self.canvas.bbox(self.object)
        self.deleted = False
        self.canvas.bombs.append(self)      # Save the bomb to the game object so it can be retrieved from a save file
        self.tick()                         # Start the loop to move the bomb

    def delete(self, _):
        """
        Removes the bomb from canvas and stops tracking it for the save file.
        It also alters the game variables lives and streak
        """
        if not self.canvas.paused:
            self.canvas.configure(bg="red")
            self.canvas.after(250, 
                lambda: self.canvas.configure(bg="#f0d7a1"))  # Flash the screen red for 250ms to indicate life loss
            self.deleted = True
            self.canvas.streak = 0
            self.canvas.lives -= 1
            self.canvas.hit_or_miss.append(False)             # Record this event as negative on the player's performance deque
            self.canvas.bombs.remove(self)
            self.canvas.delete(self.object)

        
    def displace(self):
        """
        Main physics function which handles collisions with walls and calculates displacenet 
        Uses SUVAT equations and Newton's law of restitution. 
        Deletes the object when it falls below the screen
        """
        left, top, right, bottom = self.bbox
        self.grounded = bottom >= self.height
        dy, dx = 0, 0
        if left <= 0:
            self.velocity_x = -self.velocity_x*self.canvas.e
            dx = -left
        if right >= self.width:
            self.velocity_x = -self.velocity_x*self.canvas.e
            dx = -(right-self.width)
        if top <= 0:
            self.velocity_y = -self.velocity_y*self.canvas.e
            dy = -top
        if self.canvas.floor_cheat and self.grounded:
            self.velocity_y = -self.velocity_y*self.canvas.e
            dy = -(bottom-self.height)
        if top >= self.height:
            self.deleted = True
            self.canvas.delete(self.object)
        if not(self.grounded and self.canvas.floor_cheat):
            self.velocity_y += self.canvas.g*self.canvas.ppm*self.canvas.dt
        dx += self.velocity_x*self.canvas.dt
        dy += self.velocity_y*self.canvas.dt
        self.x += dx
        self.y += dy
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
                self.bbox = self.canvas.bbox(self.object)               # Update the collision box
            self.canvas.after(int(1000*self.canvas.dt), self.tick)      # Tick rate is set to the dt variable

    def pack(self):
        """
        This function returns a list of object properties to be pickled into the save file
        """
        return [(self.x, self.y), (self.velocity_x, self.velocity_y), None]

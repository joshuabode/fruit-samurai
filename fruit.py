from PIL import ImageTk, Image

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
        self.canvas.score += 5 * self.canvas.streak*0.2
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
        if self.canvas.paused:
            dx, dy = 0, 0
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
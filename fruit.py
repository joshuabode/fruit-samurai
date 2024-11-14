from PIL import ImageTk, Image
from random import choice

class Fruit:
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image=False, shape=False):
        self.canvas = canvas
        self.height, self.width = canvas.height, canvas.width
        self.x, self.y = coords
        self.s_x, self.s_y = sprite_coords
        self.v_x, self.v_y = velocity
        self.shape = shape
        self.flip_image = flip_image
        if not shape:
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
        else:
            fruit_shapes = [canvas.create_oval(self.x, self.y, self.x+50, self.y+50, fill="red", outline="red"),
                            canvas.create_oval(self.x, self.y, self.x+50, self.y+50, fill="yellow", outline="yellow"),
                            canvas.create_oval(self.x, self.y, self.x+50, self.y+50, fill="brown", outline="brown")]
            self.object = choice(fruit_shapes) 
        self.bbox = self.canvas.bbox(self.object)
        self.deleted = False
        self.tick()

    def delete(self, event):
        if not self.canvas.paused:
            self.deleted = True
            self.canvas.streak += 1
            if self.s_x//16 == 2:
                self.canvas.lives += 1
            self.canvas.hit_or_miss.append(True)
            self.canvas.score += self.canvas.streak*0.2*max(10, (0.1*(self.canvas.m_vel[0]**2 + self.canvas.m_vel[1]**2)**0.5))
            if not self.shape:
                # Generates two halves of chopped fruit
                left = ChoppedFruit((self.s_x, 5*16),
                        (self.canvas.coords(self.object)[0]-16, self.canvas.coords(self.object)[1]),
                        (0.2*self.canvas.m_vel[0]-50, 0.2*self.canvas.m_vel[1]),
                        self.canvas, False)
                self.canvas.fruits.append(left)
                right = ChoppedFruit((self.s_x, 5*16),
                        (self.canvas.coords(self.object)[0]+16, self.canvas.coords(self.object)[1]),
                        (0.2*self.canvas.m_vel[0]+50, 0.2*self.canvas.m_vel[1]),
                        self.canvas, True)
                self.canvas.fruits.append(right)
                self.canvas.tag_bind(left.object, "<Enter>", left.delete) 
                self.canvas.tag_bind(right.object, "<Enter>", right.delete) 
            # Removes the old sprite from the canvas
            self.canvas.fruits.remove(self)
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
            if self.__class__.__name__ == "Fruit":
                self.canvas.streak = 0
                self.canvas.hit_or_miss.append(False)
                self.canvas.lives -= 1
            self.deleted = True
            self.canvas.fruits.remove(self)
        if not(self.grounded and self.canvas.cheating):
            self.v_y += self.canvas.g*self.canvas.ppm*self.canvas.dt
        dx += self.v_x*self.canvas.dt
        dy += self.v_y*self.canvas.dt
        self.x += dx
        self.y += dy
        return (dx, dy)


    def tick(self):
        # This function updates the positino of the fruit
        if not self.deleted:
            if self.canvas.paused:
                pass
            else:
                self.canvas.move(self.object, *self.displace())
                self.bbox = self.canvas.bbox(self.object)
            self.canvas.after(int(1000*self.canvas.dt), self.tick)

    def pack(self) -> str:
        vars = [(self.s_x, self.s_y), (self.x, self.y), (self.v_x, self.v_y), None, self.flip_image, self.shape]
        return vars
            

class ChoppedFruit(Fruit):
    # Chopped fruit class has a redefined delete function as we dont want an infinite stream of fruit-halves
    def __init__(self, sprite_coords, coords, velocity, canvas, flip_image):
        super().__init__(sprite_coords, coords, velocity, canvas, flip_image)

    def delete(self, _):
        if self.grounded:
            self.deleted = True
            self.canvas.fruits.remove(self)
            self.canvas.delete(self.object)
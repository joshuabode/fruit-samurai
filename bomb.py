from PIL import Image, ImageTk
class Bomb:
    def __init__(self, coords, velocity, canvas):
        self.canvas = canvas
        self.height, self.width = canvas.height, canvas.width
        self.x, self.y = coords
        self.v_x, self.v_y = velocity
        self.sprite = Image.open("bomb.png")
        self.sprite = self.sprite.resize((int(self.canvas.fruit_size), 
                                            int(self.canvas.fruit_size)), 
                                            Image.Resampling.NEAREST)
        self.image = ImageTk.PhotoImage(master=self.canvas, image=self.sprite)
        self.object = canvas.create_image(self.x, self.y, image=self.image, anchor='center')
        self.bbox = self.canvas.bbox(self.object)
        self.deleted = False
        self.canvas.bombs.append(self)
        self.tick()

    def delete(self, event):
        if not self.canvas.paused:
            self.canvas.configure(bg="red")
            self.canvas.after(100, lambda: self.canvas.configure(bg="#f0d7a1"))
            self.deleted = True
            self.canvas.streak = 0
            self.canvas.lives -= 1
            self.canvas.hit_or_miss.append(False)
            self.canvas.bombs.remove(self)
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
            self.canvas.delete(self.object)
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
        vars = [(self.x, self.y), (self.v_x, self.v_y), None]
        return vars
            

import tkinter as tk

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 5
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 15
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#FF6347', 2: '#FF4500', 3: '#8B0000'}  # Warna default
    ALT_COLORS = {1: '#00BFFF', 2: '#1E90FF', 3: '#0000CD'}  # Warna alternatif

    def __init__(self, canvas, x, y, hits, single_color, level):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.level = level
        # Gunakan warna solid di level 1 dan 2
        if level < 3:
            self.color = single_color
        else:
            self.color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=self.color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        # Jika level 1 atau 2, brick langsung dihancurkan saat bola mengenai brick
        if self.level < 3:
            self.delete()
            game.score += 10
            game.update_hud()
        else:
            # Jika level lebih dari 2, baru mengurangi hits
            self.hits -= 1
            if self.hits == 0:
                self.delete()
                game.score += 10
                game.update_hud()


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.level = 1
        self.score = 0
        self.width = 800
        self.height = 600
        self.canvas = tk.Canvas(self, bg='black',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 500)
        self.items[self.paddle.item] = self.paddle

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(20))

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(self.width / 2, self.height / 2,
                                   f'Level {self.level}\nPress Space to Start',
                                   size=24)
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 480)
        self.paddle.set_ball(self.ball)

    def add_bricks(self):
        self.clear_bricks()
        rows = 2 if self.level == 1 else min(2 + self.level, 7)
        # Warna solid untuk level 1 dan 2
        single_color = '#FF6347' if self.level < 3 else None
        for row in range(rows):
            for col in range(10):
                x = 50 + col * 75
                y = 50 + row * 30
                hits = 1 + (row % 3)
                self.add_brick(x, y, hits, single_color)

    def clear_bricks(self):
        for item in self.canvas.find_withtag('brick'):
            self.canvas.delete(item)

    def add_brick(self, x, y, hits, single_color):
        brick = Brick(self.canvas, x, y, hits, single_color, self.level)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size=16):
        font = ('Arial', size, 'bold')
        return self.canvas.create_text(x, y, text=text, fill='white', font=font)

    def update_hud(self):
        if self.hud:
            self.canvas.delete(self.hud)
        hud_text = f'Lives: {self.lives}   Score: {self.score}'
        self.hud = self.draw_text(100, 30, hud_text, size=14)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.add_bricks()
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.level += 1
            self.score += 100
            self.setup_game()
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(self.width / 2, self.height / 2, 'Game Over!', size=24)
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            if self.level >= 3:
                self.ball.speed = 4
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:
            if isinstance(obj, Brick) and obj.hits == 0:
                self.score += 10
                self.update_hud()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()

# snake_game.py

from tkinter import *
import random

GAME_WIDTH = 700
GAME_HEIGHT = 700
SPEED = 200
SPACE_SIZE = 25
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"

class SnakeGame:
    def __init__(self):
        self.window = Tk()
        self.window.title("Snake game")
        self.window.resizable(False, False)

        self.score = 0
        self.is_game_over = False # Added to track game state for OpenCV integration
        self.direction = 'down'

        self.label = Label(self.window, text="Score:{}".format(self.score), font=('consolas', 40))
        self.label.pack()

        self.canvas = Canvas(self.window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
        self.canvas.pack()

        self.window.update()

        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = int((screen_width/2) - (window_width/2))
        y = int((screen_height/2) - (window_height/2)) - 40

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas, self.snake)

        self.window.after(SPEED, self.next_turn)

    def next_turn(self):
        x, y = self.snake.coordinates[0]

        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        self.snake.coordinates.insert(0, [x, y])

        square = self.canvas.create_rectangle(int(x), int(y), int(x) + SPACE_SIZE, int(y) + SPACE_SIZE, fill=SNAKE_COLOR)
        self.snake.squares.insert(0, square)

        if x == self.food.coordinates[0] and y == self.food.coordinates[1]:
            self.score += 1
            self.label.config(text="Score:{}".format(self.score))
            self.canvas.delete("food")
            self.food = Food(self.canvas, self.snake)
        else:
            del self.snake.coordinates[-1]
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]

        if self.check_collisions():
            self.game_over()
        else:
            self.window.after(SPEED, self.next_turn)

    def change_direction(self, new_direction):
        if new_direction == 'left' and self.direction != 'right':
            self.direction = new_direction
        elif new_direction == 'right' and self.direction != 'left':
            self.direction = new_direction
        elif new_direction == 'up' and self.direction != 'down':
            self.direction = new_direction
        elif new_direction == 'down' and self.direction != 'up':
            self.direction = new_direction

    def check_collisions(self):
        x, y = self.snake.coordinates[0]

        if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
            return True

        for body_part in self.snake.coordinates[1:]:
            if x == body_part[0] and y == body_part[1]:
                return True

        return False

    def game_over(self):
        self.canvas.delete(ALL)
        self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2-45,
                                font=('consolas', 70), text="GAME OVER", fill="red", tag="gameover") 
        self.is_game_over = True # Set game over state

    def restart(self):
        self.canvas.delete(ALL)
        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas, self.snake)
        self.is_game_over = False # Reset game over state
        self.score = 0
        self.direction = 'down'
        self.label.config(text="Score:{}".format(self.score))
        self.window.after(SPEED, self.next_turn)

class Snake:
    def __init__(self, canvas):
        self.body_size = BODY_PARTS
        self.coordinates = []
        self.squares = []
        self.canvas = canvas

        for i in range(0, BODY_PARTS):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:
            square = canvas.create_rectangle(int(x), int(y), int(x) + SPACE_SIZE, int(y) + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

class Food:
    def __init__(self, canvas, snake):
        self.canvas = canvas
        self.coordinates = self.generate_food_coordinates(snake)
        canvas.create_oval(int(self.coordinates[0]), int(self.coordinates[1]), int(self.coordinates[0])+ SPACE_SIZE, int(self.coordinates[1])+ SPACE_SIZE, fill=FOOD_COLOR, tag="food")

    def generate_food_coordinates(self, snake):
        while True:
            x = random.randint(0, (int(GAME_WIDTH / SPACE_SIZE) - 1)) * SPACE_SIZE
            y = random.randint(0, (int(GAME_HEIGHT / SPACE_SIZE) - 1)) * SPACE_SIZE

            if [x, y] not in snake.coordinates:
                return [x, y]

def start_game():
    game = SnakeGame()
    return game

from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeInSine
from multiprocessing import Pool, Manager
import win32api
from PIL import ImageGrab
import threading


# horizontal_ease_func = easeInSine
# vertical_ease_func = easeInSine

# horizontal_duration = 0.35
# vertical_duration = 0.35

# factor = 10000


# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 870  # 870 og $ 429 for lower screen

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = LEFT_PIXEL_Y

# Set the debounce delay (in seconds)
DEBOUNCE_DELAY = 0.05


a_pressed = False
s_pressed = False
k_pressed = False
l_pressed = False


class Command:
    def execute(self):
        pass


class MoveLeftCommand(Command):
    def __init__(self, mouse):
        self.mouse = mouse

    def execute(self):
        self.mouse.start()
        self.mouse.move_left()

    def stop(self):
        self.mouse.stop()


class MoveRightCommand(Command):
    def __init__(self, mouse):
        self.mouse = mouse

    def execute(self):
        self.mouse.start()
        self.mouse.move_right()

    def stop(self):
        self.mouse.stop()


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)
        self.duration = 1
        self.factor = 10000
        self.ease_func = easeInSine

    def move_left(self):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the left
        # check self.should_stop after each step and stop if it's True
        x = self.screen_width // 3 + random.randint(-25, 25)

        y_move = random.randint(175, 220)
        # y_middle = 775  # screen_height // 2 - 100
        y_middle = self.screen_height // 2 - 100
        if current_y > y_middle:
            y = current_y - y_move
        else:
            y = current_y + y_move

        total_steps = int(self.duration * self.factor)
        for t in range(total_steps):
            ratio = self.ease_func(t / total_steps)

            win32api.SetCursorPos(
                (
                    int(current_x + (x - current_x) * ratio),
                    int(current_y + (y - current_y) * ratio),
                )
            )
            if self.should_stop:
                break

    def move_right(self):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the right
        # check self.should_stop after each step and stop if it's True
        x = self.screen_width * 2 // 3 + random.randint(-25, 25)

        y_move = random.randint(175, 220)
        # y_middle = 775  # screen_height // 2 - 100
        y_middle = self.screen_height // 2 - 100
        if current_y > y_middle:
            y = current_y - y_move
        else:
            y = current_y + y_move

        total_steps = int(self.duration * self.factor)
        for t in range(total_steps):
            ratio = self.ease_func(t / total_steps)

            win32api.SetCursorPos(
                (
                    int(current_x + (x - current_x) * ratio),
                    int(current_y + (y - current_y) * ratio),
                )
            )
            if self.should_stop:
                break

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False


class Invoker:
    def __init__(self, mouse: Mouse):
        self.mouse = mouse
        self.command = None
        self.current_thread = None

    def set_command(self, command: Command):
        # If there is a current command being executed, stop it
        if self.command:
            self.command.stop()

        self.command = command

        # Start a new thread to execute the command
        self.current_thread = threading.Thread(target=self.execute_command)
        self.current_thread.start()

    def execute_command(self):
        if self.command:
            self.command.execute()


def print_detection(task):
    direction, h_speed, v_speed = task
    if direction == "left":
        print(f"{time.perf_counter()} | {direction} {h_speed} {v_speed}")
    else:
        print(
            f"{time.perf_counter()} |                          {direction} {h_speed} {v_speed}"
        )


def check_and_move(queue):
    global a_pressed, s_pressed, k_pressed, l_pressed

    while True:
        if keyboard.is_pressed("q"):
            print("Quitting.")
            quit()

        if keyboard.is_pressed("a") and not a_pressed:
            queue.put(("left",))
            a_pressed = True
        elif not keyboard.is_pressed("a"):
            a_pressed = False

        if keyboard.is_pressed("s") and not s_pressed:
            queue.put(("right",))
            s_pressed = True
        elif not keyboard.is_pressed("s"):
            s_pressed = False


if __name__ == "__main__":
    print("Running...")

    # Create an instance of Mouse and Invoker
    mouse = Mouse()
    invoker = Invoker(mouse)

    with Manager() as manager:
        task_queue = manager.Queue()
        with Pool(processes=4) as pool:  # Create a pool of 4 worker processes
            pool.apply_async(check_and_move, (task_queue,))
            while True:
                task = task_queue.get()
                direction = task[0]
                if direction == "left":
                    invoker.set_command(
                        MoveLeftCommand(mouse)
                    )  # Set the new command to move left
                elif direction == "right":
                    invoker.set_command(
                        MoveRightCommand(mouse)
                    )  # Set the new command to move right
                else:
                    print(f"Something went wrong: {task}")

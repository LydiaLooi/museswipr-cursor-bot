"""
This script combines the multiprocessing approach of note detection and the
multihreaded execution of movements with movement iterruption checks.

The multiprocesing approach adds movement commands to a queue where the 
main program will then execute each movement command (task) in a new thread.

Before execution of the new task, it will stop the previous task (which should force the previous
thread to break out of its loop), allowing the new task on the new Thread to begin.

"""


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
LEFT_PIXEL_Y = 840  # 870 og $ 429 for lower screen

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = LEFT_PIXEL_Y

# Set the debounce delay (in seconds)
DEBOUNCE_DELAY = 0.06


a_pressed = False
s_pressed = False
k_pressed = False
l_pressed = False


def check_pixel_color(x, y, threshold=20):
    # Get the pixel color at the given coordinates
    actual_color = pyautogui.pixel(x, y)

    # Check if any RGB value exceeds the threshold
    for value in actual_color:
        if value > threshold:
            return True

    return False


def check_pixel_color_range(start_x, start_y, end_x, end_y, num_pixels, threshold=20):
    # Grab the region of interest
    screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x + 1, end_y + 1))

    # Convert the screenshot to grayscale format
    screenshot = screenshot.convert("L")

    # Save the screenshot to an image file
    # screenshot.save("screenshot.png")

    # Iterate over the first num_pixels in the 0th and -1th columns
    for y in range(num_pixels):
        # Check the pixel at (0, y)
        if screenshot.getpixel((0, y)) > threshold:
            return True
        # Check the pixel at (-1, y), i.e., the last column
        if screenshot.getpixel((-1, y)) > threshold:
            return True

    return False


class Command:
    def execute(self):
        pass


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)

        self.y_middle = self.screen_height // 2 - 130

        self.duration = 50
        self.faster_duration = 15

        self.factor = 10000

        self.h_move_iteration = 100
        self.v_move_iteration = 100

        self.ease_func = easeInSine
        print("Mouse initialised.")

        print(f"Normal Duration Total steps: {int(self.duration * self.factor)}")
        print(f"Faster Duration Total steps: {int(self.faster_duration * self.factor)}")

        print(f"H Move iteration: {self.h_move_iteration}")
        print(f"V Move iteration: {self.h_move_iteration}")

    def move_left(self, faster=False):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the left
        x = self.screen_width // 3 + random.randint(-25, 50)

        y_move = random.randint(70, 120)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        if faster:
            duration = self.faster_duration
        else:
            duration = self.duration

        # Movement type
        if current_x < self.screen_width // 2:
            iteration = self.v_move_iteration
        else:
            iteration = self.h_move_iteration

        total_steps = int(duration * self.factor)
        for t in range(total_steps):
            if self.should_stop:
                # print("              Stop moving left")
                if t < total_steps // 2:
                    print("Stopped left too early")
                break

            # Attempt to reduce the performance impact of setting the cursor position every iteration
            if t % iteration == 0:
                ratio = self.ease_func(t / total_steps)

                win32api.SetCursorPos(
                    (
                        int(current_x + (x - current_x) * ratio),
                        int(current_y + (y - current_y) * ratio),
                    )
                )

    def move_right(self, faster=False):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the right
        # check self.should_stop after each step and stop if it's True
        x = self.screen_width * 2 // 3 + random.randint(-25, 25)

        y_move = random.randint(100, 150)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        if faster:
            duration = self.faster_duration
        else:
            duration = self.duration

        # Movement type
        if current_x < self.screen_width // 2:
            iteration = self.v_move_iteration
        else:
            iteration = self.h_move_iteration

        total_steps = int(duration * self.factor)

        for t in range(total_steps):
            if self.should_stop:
                # print("              Stop moving right")
                if t < total_steps // 2:
                    print("Stopped right too early")
                break
            # Attempt to reduce the performance impact of setting the cursor position every iteration
            if t % iteration == 0:
                ratio = self.ease_func(t / total_steps)

                win32api.SetCursorPos(
                    (
                        int(current_x + (x - current_x) * ratio),
                        int(current_y + (y - current_y) * ratio),
                    )
                )

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False


class MoveLeftCommand(Command):
    def __init__(self, mouse: Mouse, faster=False):
        self.mouse = mouse
        self.faster = faster

    def execute(self):
        self.mouse.start()
        self.mouse.move_left(self.faster)

    def stop(self):
        self.mouse.stop()


class MoveRightCommand(Command):
    def __init__(self, mouse: Mouse, faster=False):
        self.mouse = mouse
        self.faster = faster

    def execute(self):
        self.mouse.start()
        self.mouse.move_right(self.faster)

    def stop(self):
        self.mouse.stop()


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
    last_detection_time = {"left": 0, "right": 0}
    while True:
        if keyboard.is_pressed("q"):
            print("Quitting.")
            quit()

        current_time = time.perf_counter()

        for direction in ["left", "right"]:
            pixel_x = LEFT_PIXEL_X if direction == "left" else RIGHT_PIXEL_X
            pixel_y = LEFT_PIXEL_Y if direction == "left" else RIGHT_PIXEL_Y
            a = current_time - last_detection_time[direction]
            if check_pixel_color(pixel_x, pixel_y) and a >= DEBOUNCE_DELAY:
                faster = False
                if check_pixel_color_range(
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 200,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    140,
                ):
                    faster = True
                queue.put((direction, faster))
                last_detection_time[direction] = current_time


if __name__ == "__main__":
    print("Running...")

    # Create an instance of Mouse and Invoker
    mouse = Mouse()
    invoker = Invoker(mouse)

    with Manager() as manager:
        task_queue = manager.Queue()
        with Pool(processes=6) as pool:  # Create a pool of 4 worker processes
            pool.apply_async(check_and_move, (task_queue,))
            while True:
                task = task_queue.get()

                direction, faster = task
                if direction == "left":
                    invoker.set_command(MoveLeftCommand(mouse, faster))
                elif direction == "right":
                    invoker.set_command(MoveRightCommand(mouse, faster))
                else:
                    print(f"Something went wrong: {task}")

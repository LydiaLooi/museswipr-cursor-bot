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


def check_pixel_color_range(
    start_x, start_y, end_x, end_y, mid_swipe_threshold, threshold=20
):
    # Grab the region of interest
    screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x + 1, end_y + 1))

    # Convert the screenshot to grayscale format
    screenshot = screenshot.convert("L")

    # Save the screenshot to an image file
    # screenshot.save("screenshot.png")

    height = screenshot.height

    # Iterate over the range defined by mid_swipe_threshold to the top
    for y in range(
        height - 70, height - mid_swipe_threshold, -1
    ):  # 60 is so it doesn't detect the note that triggered it
        # Check the pixel at (0, y)
        if screenshot.getpixel((0, y)) > threshold:
            return "FAST"
        # Check the pixel at (-1, y), i.e., the last column
        if screenshot.getpixel((-1, y)) > threshold:
            return "FAST"

    # Iterate over the range defined by start_y to mid_swipe_threshold
    for y in range(0, height - mid_swipe_threshold):
        # Check the pixel at (0, y)
        if screenshot.getpixel((0, y)) > threshold:
            return "MID"
        # Check the pixel at (-1, y), i.e., the last column
        if screenshot.getpixel((-1, y)) > threshold:
            return "MID"

    return "SLOW"


class Command:
    def execute(self):
        pass


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)
        self.h_duration = 120
        self.v_duration = 80
        self.factor = 10000
        self.h_move_iteration = 900
        self.v_move_iteration = 5000
        self.ease_func = easeInSine

        self.y_middle = (
            self.screen_height // 2 - 130
        )  # Where the mouse will me roughly on the Y-axis

        print("Mouse initialised.")
        print(f"H Total steps: {int(self.h_duration * self.factor)}")
        print(f"V Total steps: {int(self.v_duration * self.factor)}")
        print(f"H Move iteration: {self.h_move_iteration}")
        print(f"V Move iteration: {self.v_move_iteration}")

    def move_left(self, h_speed=None, v_speed=None, last_direction=None):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the left
        x = self.screen_width // 3 + random.randint(-25, 50)

        y_move = random.randint(175, 250)

        if current_y > self.y_middle:
            y = current_y - y_move
        else:
            y = current_y + y_move

        middle_x = self.screen_width // 2

        # Detect move type - Horizontal vs Vertical. If on left side already, must be moving vertically then.
        if current_x < middle_x:
            # VERTICAL
            # print("/\\")
            duration = self.v_duration if v_speed is None else v_speed
            iteration = self.v_move_iteration
        else:
            # HORIZONTAL
            # print("<<--------")
            duration = self.h_duration if h_speed is None else h_speed
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

    def move_right(self, h_speed=None, v_speed=None, last_direction=None):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the right
        # check self.should_stop after each step and stop if it's True
        x = self.screen_width * 2 // 3 + random.randint(-25, 50)

        y_move = random.randint(175, 220)
        # y_middle = 775  # screen_height // 2 - 100
        y_middle = self.screen_height // 2 - 100
        if current_y > y_middle:
            y = current_y - y_move
        else:
            y = current_y + y_move

        middle_x = self.screen_width // 2

        # Detect move type - Horizontal vs Vertical. If on right side already, must be moving vertically then.
        if current_x > middle_x:
            # VERTICAL
            # print("              /\\")
            duration = self.v_duration if v_speed is None else v_speed
            iteration = self.v_move_iteration
        else:
            # HORIZONTAL
            # print("-------->>")
            duration = self.h_duration if h_speed is None else h_speed
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

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False


class MoveLeftCommand(Command):
    def __init__(self, mouse: Mouse, h_speed=None, v_speed=None, last_direction=None):
        self.mouse = mouse
        self.h_speed = h_speed
        self.v_speed = v_speed
        self.last_direction = last_direction

    def execute(self):
        self.mouse.start()
        # print_detection(("left", "", threading.get_ident()))
        self.mouse.move_left(
            h_speed=self.h_speed,
            v_speed=self.v_speed,
            last_direction=self.last_direction,
        )
        # self.mouse.dummy_move()

    def stop(self):
        self.mouse.stop()


class MoveRightCommand(Command):
    def __init__(self, mouse: Mouse, h_speed=None, v_speed=None, last_direction=None):
        self.mouse = mouse
        self.h_speed = h_speed
        self.v_speed = v_speed
        self.last_direction = last_direction

    def execute(self):
        self.mouse.start()
        # print_detection(("right", "", threading.get_ident()))
        self.mouse.move_right(
            h_speed=self.h_speed,
            v_speed=self.v_speed,
            last_direction=self.last_direction,
        )
        # self.mouse.dummy_move()

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
    memory = {
        "left": 0,
        "right": 0,
        "speed": "MID",
        "h_speed": 50,
        "v_speed": 50,
        "last_direction": None,
    }
    while True:
        if keyboard.is_pressed("q"):
            print("Quitting.")
            quit()

        current_time = time.perf_counter()

        for direction in ["left", "right"]:
            pixel_x = LEFT_PIXEL_X if direction == "left" else RIGHT_PIXEL_X
            pixel_y = LEFT_PIXEL_Y if direction == "left" else RIGHT_PIXEL_Y
            a = current_time - memory[direction]
            if check_pixel_color(pixel_x, pixel_y) and a >= DEBOUNCE_DELAY:
                h_speed = 50
                v_speed = None
                # if check_pixel_color_range(
                #     LEFT_PIXEL_X,
                #     LEFT_PIXEL_Y - 200,
                #     RIGHT_PIXEL_X,
                #     RIGHT_PIXEL_Y,
                #     130,
                # ):
                #     h_speed = 45  # 45 can do horizontal EWF but not vertical
                #     v_speed = 25
                speed = check_pixel_color_range(
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 350,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    250,
                )

                if memory["speed"] == "FAST":
                    h_speed = 45
                    v_speed = 25

                elif memory["speed"] == "MID":
                    h_speed = 70
                    v_speed = 50

                queue.put(
                    (
                        direction,
                        memory["h_speed"],
                        memory["v_speed"],
                        memory["last_direction"],
                    )
                )
                # print_detection((direction, a, ""))
                memory[direction] = current_time
                memory["h_speed"] = h_speed
                memory["v_speed"] = v_speed
                memory["speed"] = speed
                memory["last_direction"] = direction


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
                #     # print("Task received")

                direction, h_speed, v_speed, last_direction = task
                if direction == "left":
                    invoker.set_command(
                        MoveLeftCommand(
                            mouse,
                            h_speed=h_speed,
                            v_speed=v_speed,
                            last_direction=last_direction,
                        )
                    )  # Set the new command to move left
                elif direction == "right":
                    invoker.set_command(
                        MoveRightCommand(
                            mouse,
                            h_speed=h_speed,
                            v_speed=v_speed,
                            last_direction=last_direction,
                        )
                    )  # Set the new command to move right
                else:
                    print(f"Something went wrong: {task}")

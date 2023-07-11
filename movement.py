from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeInSine
from multiprocessing import Pool, Manager
import win32api
from PIL import ImageGrab


horizontal_ease_func = easeInSine
vertical_ease_func = easeInSine

horizontal_duration = 0.35
vertical_duration = 0.35

factor = 10000


last_left_detection_time = 0
last_right_detection_time = 0

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


def move_mouse(task):
    direction, h_speed, v_speed = task
    # print(f"moving {direction}")
    global last_left_detection_time, last_right_detection_time

    # print(f"{time.perf_counter()} Moving {direction}")

    current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

    # Move the mouse with non-linear movement from the current position to the middle of the left side of the screen with randomized y-coordinate
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)

    # Move the mouse with non-linear movement from the current posiqq

    if direction == "left":
        x = screen_width // 3 + random.randint(
            -25, 25
        )  # Move to the third position on the x-axis
    else:
        x = screen_width * 2 // 3 + random.randint(
            -25, 25
        )  # Move to the two third position on the x-axis

    y_move = random.randint(175, 220)
    # y_middle = 775  # screen_height // 2 - 100
    y_middle = screen_height // 2 - 100
    if current_y > y_middle:
        y = current_y - y_move
    else:
        y = current_y + y_move

    # Detect move type? Horizontal vs Vertical

    # Calculate the change in x and y
    delta_x = abs(x - current_x)
    delta_y = abs(y - current_y)

    # Determine the move type
    if delta_x > delta_y:
        ease_func = horizontal_ease_func
        duration = horizontal_duration if h_speed is None else h_speed
    else:
        ease_func = vertical_ease_func
        duration = vertical_duration if v_speed is None else v_speed
        # print("Vertical")
    # Calculate the duration of movement based on the distance
    # Perform easing on your own (pytweening's easeInCubic)
    total_steps = int(duration * factor)
    for t in range(total_steps):
        ratio = ease_func(t / total_steps)

        win32api.SetCursorPos(
            (
                int(current_x + (x - current_x) * ratio),
                int(current_y + (y - current_y) * ratio),
            )
        )


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
            queue.put(("left", None, None))
            a_pressed = True
        elif not keyboard.is_pressed("a"):
            a_pressed = False

        if keyboard.is_pressed("s") and not s_pressed:
            queue.put(("right", None, None))
            s_pressed = True
        elif not keyboard.is_pressed("s"):
            s_pressed = False


if __name__ == "__main__":
    print("Running...")
    print(f"Horizontal total steps is: {int(horizontal_duration * factor)}")
    print(f"Vertical total steps is: {int(vertical_duration * factor)}")

    with Manager() as manager:
        task_queue = manager.Queue()
        with Pool(processes=4) as pool:  # Create a pool of 4 worker processes
            pool.apply_async(check_and_move, (task_queue,))
            while True:
                task = task_queue.get()
                pool.apply_async(print_detection, (task,))

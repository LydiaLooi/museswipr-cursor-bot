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


def print_detection(_direction, h_speed=None, v_speed=None):
    direction, h_speed, v_speed = _direction
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

            if (
                check_pixel_color(pixel_x, pixel_y)
                and current_time - last_detection_time[direction] >= DEBOUNCE_DELAY
            ):
                h_speed = None
                v_speed = None
                if check_pixel_color_range(
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 200,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    20,
                ):
                    h_speed = 0.2
                    v_speed = 0.2
                # print(f"putting {direction}")
                queue.put((direction, h_speed, v_speed))
                last_detection_time[direction] = current_time


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
                pool.apply_async(move_mouse, (task,))

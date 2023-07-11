from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeInOutExpo, linear, easeInQuint, easeInSine, easeInOutPoly
import threading
import win32api

horizontal_ease_func = easeInOutPoly
vertical_ease_func = easeInSine

horizontal_duration = 4
vertical_duration = 4

factor = 5000


last_left_detection_time = 0
last_right_detection_time = 0

# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 870  # 870

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = 870  # 870

# Set the debounce delay (in seconds)
DEBOUNCE_DELAY = 0.05

OFFSET = 0.02


def check_pixel_color(x, y, threshold=20):
    # Get the pixel color at the given coordinates
    actual_color = pyautogui.pixel(x, y)

    # Check if any RGB value exceeds the threshold
    for value in actual_color:
        if value > threshold:
            return True

    return False


def move_mouse(direction):
    global last_left_detection_time, last_right_detection_time

    current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

    # Move the mouse with non-linear movement from the current position to the middle of the left side of the screen with randomized y-coordinate
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)

    # Move the mouse with non-linear movement from the current posiqq

    if direction == "left":
        x = screen_width // 3 + random.randint(
            -50, 50
        )  # Move to the third position on the x-axis
    else:
        x = screen_width * 2 // 3 + random.randint(
            -50, 50
        )  # Move to the two third position on the x-axis

    y_move = random.randint(125, 200)
    y_middle = screen_height // 2
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
        duration = horizontal_duration
        # print("Horizontal")
    else:
        ease_func = vertical_ease_func
        duration = vertical_duration
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
        # current_time = time.perf_counter()
        # a = check_pixel_color(LEFT_PIXEL_X, LEFT_PIXEL_Y)
        # b = check_pixel_color(RIGHT_PIXEL_X, RIGHT_PIXEL_Y)
        # c = current_time - last_left_detection_time >= DEBOUNCE_DELAY
        # d = current_time - last_right_detection_time >= DEBOUNCE_DELAY
        # if t > total_steps // 2 and ((a and c) or (b and d)):
        #     print(a and c)
        #     print(a and d)
        # break
        # time.sleep(0.0001)


# Create a function to run the pixel color checking and mouse moving in a separate thread
def check_and_move():
    global last_left_detection_time, last_right_detection_time
    start_pressed = False

    while True:
        if keyboard.is_pressed("q"):
            # Exit the script if the Q key is pressed
            print("Quitting.")
            break

        if keyboard.is_pressed("e"):
            start_pressed = True
            print("Activated!")

        if start_pressed:
            current_time = time.perf_counter()
            if (
                check_pixel_color(LEFT_PIXEL_X, LEFT_PIXEL_Y)
                and current_time - last_left_detection_time >= DEBOUNCE_DELAY
            ):
                # print(f"{time.perf_counter()} detected left pixel")
                threading.Thread(target=move_mouse("left")).start()
                last_left_detection_time = current_time

            if (
                check_pixel_color(RIGHT_PIXEL_X, RIGHT_PIXEL_Y)
                and current_time - last_right_detection_time >= DEBOUNCE_DELAY
            ):
                # print(f"{time.perf_counter()} detected right pixel")

                threading.Thread(target=move_mouse("right")).start()
                last_right_detection_time = current_time


if __name__ == "__main__":
    print("Running...")
    print(f"Horizontal total steps is: {int(horizontal_duration * factor)}")
    print(f"Vertical total steps is: {int(vertical_duration * factor)}")
    # Start the check_and_move function in a separate thread
    threading.Thread(target=check_and_move).start()

from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeInCubic


def check_pixel_color(x, y, threshold=20):
    # Get the pixel color at the given coordinates
    actual_color = pyautogui.pixel(x, y)

    # Check if any RGB value exceeds the threshold
    for value in actual_color:
        if value > threshold:
            return True

    return False


def move_mouse_left():
    # Move the mouse with non-linear movement from the current position to the middle of the left side of the screen with randomized y-coordinate
    screen_width, screen_height = pyautogui.size()
    x = screen_width // 3  # Move to the quarter position on the x-axis
    y = screen_height // 2 + random.randint(
        -200, 200
    )  # Randomize y-coordinate by +/- 100 pixels

    # Calculate the duration of movement based on the distance
    duration = 0.05
    # Move the mouse with easing
    pyautogui.moveTo(x, y, duration=duration, tween=easeInCubic)


def move_mouse_right():
    # Move the mouse with non-linear movement from the current position to the middle of the right side of the screen with randomized y-coordinate
    screen_width, screen_height = pyautogui.size()
    x = screen_width * 2 // 3  # Move to the three-quarter position on the x-axis
    y = screen_height // 2 + random.randint(
        -200, 200
    )  # Randomize y-coordinate by +/- 100 pixels

    duration = 0.05

    # Move the mouse with easing
    pyautogui.moveTo(x, y, duration=duration, tween=easeInCubic)


# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 870
LEFT_PIXEL_COLOR = (1, 153, 191)

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = 870
RIGHT_PIXEL_COLOR = (195, 31, 135)

print("Running...")

space_pressed = False  # Track the state of the space bar

while True:
    if keyboard.is_pressed("q"):
        # Exit the script if the Q key is pressed
        print("Quitting.")
        break

    if keyboard.is_pressed("space"):
        # Toggle the state of the space bar
        space_pressed = True
        print("Space bar activated!")

    if space_pressed:
        # Check the pixel colors when the space bar is active
        if check_pixel_color(LEFT_PIXEL_X, LEFT_PIXEL_Y):
            move_mouse_left()
            # time.sleep(0.01)

        if check_pixel_color(RIGHT_PIXEL_X, RIGHT_PIXEL_Y):
            move_mouse_right()
            # time.sleep(0.01)

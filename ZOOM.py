from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeInOutExpo, linear
import threading
import win32api


# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 870

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = 870

DURATION = 0.05


def check_pixel_color(x, y, threshold=20):
    # Get the pixel color at the given coordinates
    actual_color = pyautogui.pixel(x, y)

    # Check if any RGB value exceeds the threshold
    for value in actual_color:
        if value > threshold:
            return True

    return False


def move_mouse(direction):
    current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

    # Move the mouse with non-linear movement from the current position to the middle of the left side of the screen with randomized y-coordinate
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)

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

    # Calculate the duration of movement based on the distance
    # Perform easing on your own (pytweening's easeInCubic)
    total_steps = int(DURATION * 50)
    for t in range(total_steps):
        ratio = easeInOutExpo(t / total_steps)
        win32api.SetCursorPos(
            (
                int(current_x + (x - current_x) * ratio),
                int(current_y + (y - current_y) * ratio),
            )
        )


# Create a function to run the pixel color checking and mouse moving in a separate thread
def check_and_move():
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
            if check_pixel_color(LEFT_PIXEL_X, LEFT_PIXEL_Y):
                threading.Thread(target=move_mouse("left")).start()

            if check_pixel_color(RIGHT_PIXEL_X, RIGHT_PIXEL_Y):
                threading.Thread(target=move_mouse("right")).start()


if __name__ == "__main__":
    print("Running...")
    print(f"Total steps is: {int(DURATION * 50)}")
    # Start the check_and_move function in a separate thread
    threading.Thread(target=check_and_move).start()

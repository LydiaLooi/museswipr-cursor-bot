from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeOutExpo
import threading
import win32api

# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 870

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = 870

DURATION = 0.15

# Create a lock object to prevent concurrent access to shared resources
lock = threading.Lock()

# Create a variable to track the mouse movement
mouse_moving = False


def check_pixel_color(x, y, threshold=20):
    # Get the pixel color at the given coordinates
    actual_color = pyautogui.pixel(x, y)

    # Check if any RGB value exceeds the threshold
    for value in actual_color:
        if value > threshold:
            return True

    return False


def move_mouse(direction):
    global mouse_moving
    with lock:
        mouse_moving = True

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

    y_move = random.randint(100, 200)
    y_middle = screen_height // 2
    if current_y > y_middle:
        y = current_y - y_move
    else:
        y = current_y + y_move

    # Calculate the duration of movement based on the distance
    duration = DURATION
    # Perform easing on your own (pytweening's easeInCubic)
    for t in range(int(duration * 50)):
        ratio = easeOutExpo(t / (duration * 50))  # This might need to be adjusted
        win32api.SetCursorPos(
            (
                int(current_x + (x - current_x) * ratio),
                int(current_y + (y - current_y) * ratio),
            )
        )
        # time.sleep(0.001)  # Wait a little bit to emulate the duration
        # BUT, HAVING THIS HERE MEANS IT IS BLOCKING THE DETECTION!!!

    with lock:
        mouse_moving = False


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
            if not mouse_moving and check_pixel_color(LEFT_PIXEL_X, LEFT_PIXEL_Y):
                threading.Thread(target=move_mouse("left")).start()

            if not mouse_moving and check_pixel_color(RIGHT_PIXEL_X, RIGHT_PIXEL_Y):
                threading.Thread(target=move_mouse("right")).start()


if __name__ == "__main__":
    print("Running...")

    # Start the check_and_move function in a separate thread
    threading.Thread(target=check_and_move).start()

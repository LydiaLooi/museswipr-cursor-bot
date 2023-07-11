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

horizontal_duration = 0.2
vertical_duration = 0.15

# Constants for checking the hit pixels
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 870

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = 870

# Swipe configs


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


def check_interrupt():
    global a_pressed, s_pressed, k_pressed, l_pressed
    return a_pressed or s_pressed or k_pressed or l_pressed


def move_mouse(direction):
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

    y_move = random.randint(150, 250)
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
    else:
        ease_func = vertical_ease_func
        duration = vertical_duration

    # Calculate the duration of movement based on the distance
    # Perform easing on your own (pytweening's easeInCubic)
    total_steps = int(duration * 50)
    for t in range(total_steps):
        ratio = ease_func(t / total_steps)

        win32api.SetCursorPos(
            (
                int(current_x + (x - current_x) * ratio),
                int(current_y + (y - current_y) * ratio),
            )
        )


def check_and_move():
    global a_pressed, s_pressed, k_pressed, l_pressed

    while True:
        if keyboard.is_pressed("q"):
            # Exit the script if the Q key is pressed
            print("Quitting.")
            break

        if keyboard.is_pressed("a") and not a_pressed:
            threading.Thread(target=move_mouse, args=("left",)).start()
            a_pressed = True
        elif not keyboard.is_pressed("a"):
            a_pressed = False

        if keyboard.is_pressed("s") and not s_pressed:
            threading.Thread(target=move_mouse, args=("left",)).start()
            s_pressed = True
        elif not keyboard.is_pressed("s"):
            s_pressed = False

        if keyboard.is_pressed("k") and not k_pressed:
            threading.Thread(target=move_mouse, args=("right",)).start()
            k_pressed = True
        elif not keyboard.is_pressed("k"):
            k_pressed = False

        if keyboard.is_pressed("l") and not l_pressed:
            threading.Thread(target=move_mouse, args=("right",)).start()
            l_pressed = True
        elif not keyboard.is_pressed("l"):
            l_pressed = False


if __name__ == "__main__":
    print("Running...")
    # Start the check_and_move function in a separate thread
    threading.Thread(target=check_and_move).start()

from pyautogui import *
import pyautogui
import time
import keyboard
import random
from pytweening import easeInOutExpo, linear, easeInQuint, easeInSine, easeInOutPoly
import threading
import win32api
from PIL import ImageGrab

horizontal_ease_func = easeInOutPoly
vertical_ease_func = easeInSine

horizontal_duration = 3.75
vertical_duration = 3.75

factor = 5000


last_left_detection_time = 0
last_right_detection_time = 0

# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 850  # 870 og

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = 850  # 870

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


def move_mouse(direction, speed=None):
    global last_left_detection_time, last_right_detection_time

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

    y_move = random.randint(125, 200)
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
        duration = horizontal_duration if speed is None else speed
        # print("Horizontal")
    else:
        ease_func = vertical_ease_func
        duration = vertical_duration if speed is None else speed
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
                speed = None
                if check_pixel_color_range(
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 200,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    100,
                ):
                    speed = 1

                threading.Thread(target=move_mouse("left", speed)).start()
                last_left_detection_time = current_time

            if (
                check_pixel_color(RIGHT_PIXEL_X, RIGHT_PIXEL_Y)
                and current_time - last_right_detection_time >= DEBOUNCE_DELAY
            ):
                speed = None
                if check_pixel_color_range(
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 300,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    150,
                ):
                    speed = 1

                threading.Thread(target=move_mouse("right", speed)).start()
                last_right_detection_time = current_time


if __name__ == "__main__":
    print("Running...")
    print(f"Horizontal total steps is: {int(horizontal_duration * factor)}")
    print(f"Vertical total steps is: {int(vertical_duration * factor)}")
    # Start the check_and_move function in a separate thread
    threading.Thread(target=check_and_move).start()

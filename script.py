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

from main import move_mouse


# Create a function to run the pixel color checking and mouse moving in a separate thread
def check_and_move():
    while True:
        if keyboard.is_pressed("q"):
            # Exit the script if the Q key is pressed
            print("Quitting.")
            break

        if keyboard.is_pressed("a"):
            if not mouse_moving:
                threading.Thread(target=move_mouse("left")).start()

        if keyboard.is_pressed("d"):
            if not mouse_moving:
                threading.Thread(target=move_mouse("right")).start()


if __name__ == "__main__":
    print("Running...")
    # Start the check_and_move function in a separate thread
    threading.Thread(target=check_and_move).start()

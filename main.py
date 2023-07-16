from time import perf_counter
from keyboard import is_pressed
from multiprocessing import Pool, Manager
from screen_analysis import check_pixel_color, check_pixel_color_range
from mouse import Mouse
from mouse_invoker import MouseMoveInvoker
from commands.move import MoveLeftCommand, MoveRightCommand
from sys import exit
from win32api import GetCursorPos

from yaml import safe_load

with open("config.yaml") as config_file:
    config = safe_load(config_file)

# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = config["LEFT_PIXEL_X"]
LEFT_PIXEL_Y = config["LEFT_PIXEL_Y"]  # 870 og $ 429 for lower screen

RIGHT_PIXEL_X = config["RIGHT_PIXEL_X"]
RIGHT_PIXEL_Y = config["RIGHT_PIXEL_Y"]

# Set the debounce delay (in seconds)
DEBOUNCE_DELAY = config["DEBOUNCE_DELAY"]


def check_and_move(queue, local_mem):
    while True:
        current_time = perf_counter()
        local_mem["check_count"] += 1

        for direction in ["left", "right"]:
            pixel_x = LEFT_PIXEL_X if direction == "left" else RIGHT_PIXEL_X
            pixel_y = LEFT_PIXEL_Y if direction == "left" else RIGHT_PIXEL_Y
            a = current_time - local_mem[direction]
            if check_pixel_color(pixel_x, pixel_y) and a >= DEBOUNCE_DELAY:
                speed = check_pixel_color_range(  # Screenshot is W 508px x H 201px
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 200,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    140,
                )
                if speed > local_mem["speed"]:
                    # Overrides the last slow swipe if this next one is gonna be faster
                    local_mem["speed"] = speed
                queue.put((direction, local_mem["speed"]))
                local_mem[direction] = current_time

                # Update the speed in memory
                local_mem["speed"] = speed


if __name__ == "__main__":
    try:
        print("Starting... press 'e' to begin detecting.")
        # Create an instance of Mouse and Invoker
        mouse = Mouse()
        invoker = MouseMoveInvoker(mouse)
        set_command = invoker.set_command
        start = False
        while start is False:
            if is_pressed("e"):
                start = True
                print("Detection has begun.\n")

        start_time = perf_counter()

        with Manager() as manager:
            task_queue = manager.Queue()
            local_mem = manager.dict(
                {"left": 0, "right": 0, "speed": 0, "check_count": 0}
            )
            last_swipe_horizontal = True

            with Pool(processes=1) as pool:
                pool.apply_async(check_and_move, (task_queue, local_mem))
                while True:
                    if is_pressed("q"):
                        end_time = perf_counter()
                        time_ran = end_time - start_time
                        print(f"Quitting... Was detecting for {time_ran:.2f}s ")
                        checks_s = local_mem["check_count"] / time_ran
                        print(
                            f"Check count: {local_mem['check_count']} | Checks/s: {checks_s}"
                        )
                        exit(0)
                    elif is_pressed("e"):
                        print(local_mem)
                    task = task_queue.get()
                    direction, speed = task

                    current_x, _ = GetCursorPos()  # Get current mouse position

                    if direction == "left":
                        # Movement type
                        if current_x < mouse.x_middle:
                            # Vertical
                            is_horziontal = False
                        else:
                            is_horziontal = True
                        set_command(
                            MoveLeftCommand(mouse, speed, last_swipe_horizontal)
                        )
                    elif direction == "right":
                        # Movement type
                        if current_x > mouse.x_middle:
                            # Vertical
                            is_horziontal = False
                        else:
                            is_horziontal = True
                        set_command(
                            MoveRightCommand(mouse, speed, last_swipe_horizontal)
                        )
                    else:
                        print(f"Something went wrong: {task}")
                    last_swipe_horizontal = is_horziontal
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.")
        exit(0)  # Exit the program

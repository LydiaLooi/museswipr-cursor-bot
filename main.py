from time import perf_counter
from keyboard import is_pressed
from multiprocessing import Pool, Manager
from screen_analysis import check_pixel_color, check_pixel_color_range
from mouse import Mouse
from mouse_invoker import MouseMoveInvoker
from commands.move import MoveLeftCommand, MoveRightCommand
from sys import exit

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
                faster = False
                if check_pixel_color_range(
                    LEFT_PIXEL_X,
                    LEFT_PIXEL_Y - 200,
                    RIGHT_PIXEL_X,
                    RIGHT_PIXEL_Y,
                    140,
                ):
                    faster = True
                    # Overrides the last slow swipe if this next one is gonna be faster
                    if not local_mem["faster"]:
                        local_mem["faster"] = True

                queue.put((direction, local_mem["faster"]))
                local_mem[direction] = current_time
                local_mem["faster"] = faster


if __name__ == "__main__":
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

    try:
        with Manager() as manager:
            task_queue = manager.Queue()
            local_mem = manager.dict(
                {"left": 0, "right": 0, "faster": True, "check_count": 0}
            )

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
                    direction, faster = task
                    if direction == "left":
                        set_command(MoveLeftCommand(mouse, faster))
                    elif direction == "right":
                        set_command(MoveRightCommand(mouse, faster))
                    else:
                        print(f"Something went wrong: {task}")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.")
        exit(0)  # Exit the program

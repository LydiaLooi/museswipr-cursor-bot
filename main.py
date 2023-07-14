"""
This script combines the multiprocessing approach of note detection and the
multihreaded execution of movements with movement iterruption checks.

The multiprocesing approach adds movement commands to a queue where the 
main program will then execute each movement command (task) in a new thread.

Before execution of the new task, it will stop the previous task (which should force the previous
thread to break out of its loop), allowing the new task on the new Thread to begin.

"""


from time import perf_counter
from keyboard import is_pressed
from multiprocessing import Pool, Manager
from screen_analysis import check_pixel_color, check_pixel_color_range
from mouse import Mouse
from mouse_invoker import MouseMoveInvoker
from commands.move import MoveLeftCommand, MoveRightCommand

# Constants for pixel coordinates and expected colors
LEFT_PIXEL_X = 709
LEFT_PIXEL_Y = 840  # 870 og $ 429 for lower screen

RIGHT_PIXEL_X = 1216
RIGHT_PIXEL_Y = LEFT_PIXEL_Y

# Set the debounce delay (in seconds)
DEBOUNCE_DELAY = 0.0425  # 0.05 for 60fps # # 0.04 and less starts double detecting at 16.5 scroll at 144 fps


def print_detection(task):
    direction, h_speed, v_speed = task
    if direction == "left":
        print(f"{perf_counter()} | {direction} {h_speed} {v_speed}")
    else:
        print(
            f"{perf_counter()} |                          {direction} {h_speed} {v_speed}"
        )


def check_and_move(queue):
    last_detection_time = {"left": 0, "right": 0, "faster": True}
    while True:
        if is_pressed("q"):
            print("Quitting.")
            quit()

        current_time = perf_counter()

        for direction in ["left", "right"]:
            pixel_x = LEFT_PIXEL_X if direction == "left" else RIGHT_PIXEL_X
            pixel_y = LEFT_PIXEL_Y if direction == "left" else RIGHT_PIXEL_Y
            a = current_time - last_detection_time[direction]
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
                    if not last_detection_time[
                        "faster"
                    ]:  # Overrides the last slow swipe if this next one is gonna be faster
                        last_detection_time["faster"] = True
                queue.put((direction, last_detection_time["faster"]))
                last_detection_time[direction] = current_time
                last_detection_time["faster"] = faster


if __name__ == "__main__":
    print("Running...")

    # Create an instance of Mouse and Invoker
    mouse = Mouse()
    invoker = MouseMoveInvoker(mouse)
    set_command = invoker.set_command

    with Manager() as manager:
        task_queue = manager.Queue()
        with Pool(processes=6) as pool:  # Create a pool of 6 worker processes
            pool.apply_async(check_and_move, (task_queue,))
            while True:
                task = task_queue.get()

                direction, faster = task
                if direction == "left":
                    set_command(MoveLeftCommand(mouse, faster))
                elif direction == "right":
                    set_command(MoveRightCommand(mouse, faster))
                else:
                    print(f"Something went wrong: {task}")

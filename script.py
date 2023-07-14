from keyboard import is_pressed
from multiprocessing import Pool, Manager
from mouse import Mouse
from mouse_invoker import MouseMoveInvoker
from commands.move import MoveLeftCommand, MoveRightCommand


def check_and_move(queue):
    memory = {
        "a_pressed": False,
        "s_pressed": False,
        "k_pressed": False,
        "l_pressed": False,
        "faster": True,
    }
    while True:
        if is_pressed("q"):
            print("Quitting.")
            quit()

        if is_pressed("a") and not memory["a_pressed"]:
            queue.put(("left", memory["faster"]))
            memory["a_pressed"] = True
        elif not is_pressed("a"):
            memory["a_pressed"] = False

        if is_pressed("s") and not memory["s_pressed"]:
            queue.put(("left", memory["faster"]))
            memory["s_pressed"] = True
        elif not is_pressed("s"):
            memory["s_pressed"] = False

        if is_pressed("k") and not memory["k_pressed"]:
            queue.put(("right", memory["faster"]))
            memory["k_pressed"] = True
        elif not is_pressed("k"):
            memory["k_pressed"] = False

        if is_pressed("l") and not memory["l_pressed"]:
            queue.put(("right", memory["faster"]))
            memory["l_pressed"] = True
        elif not is_pressed("l"):
            memory["l_pressed"] = False


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

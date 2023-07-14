import random

from pytweening import easeInSine, easeInOutPoly

import win32api


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)

        self.y_middle = self.screen_height // 2 - 130

        self.duration = 100  # 70
        self.faster_duration = 60  # 50 # 35

        self.factor = 10000

        self.h_move_iteration = 500
        self.v_move_iteration = 1000

        self.ease_func = easeInOutPoly
        print("Mouse initialised.")

        print(f"Normal Duration Total steps: {int(self.duration * self.factor)}")
        print(f"Faster Duration Total steps: {int(self.faster_duration * self.factor)}")

        print(f"H Move iteration: {self.h_move_iteration}")
        print(f"V Move iteration: {self.v_move_iteration}")

    def move_left(self, faster=False):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the left
        x = self.screen_width // 3 + random.randint(-25, 50)

        y_move = random.randint(70, 120)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        if faster:
            duration = self.faster_duration
        else:
            duration = self.duration

        # Movement type
        if current_x < self.screen_width // 2:
            iteration = self.v_move_iteration
        else:
            iteration = self.h_move_iteration

        total_steps = int(duration * self.factor)
        for t in range(total_steps):
            if self.should_stop:
                # print("              Stop moving left")
                if t < total_steps // 2:
                    print("Stopped left too early")
                break

            # Attempt to reduce the performance impact of setting the cursor position every iteration
            if t % iteration == 0:
                ratio = self.ease_func(t / total_steps)

                win32api.SetCursorPos(
                    (
                        int(current_x + (x - current_x) * ratio),
                        int(current_y + (y - current_y) * ratio),
                    )
                )

    def move_right(self, faster=False):
        current_x, current_y = win32api.GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the right
        # check self.should_stop after each step and stop if it's True
        x = self.screen_width * 2 // 3 + random.randint(-25, 25)

        y_move = random.randint(100, 150)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        if faster:
            duration = self.faster_duration
        else:
            duration = self.duration

        # Movement type
        if current_x < self.screen_width // 2:
            iteration = self.v_move_iteration
        else:
            iteration = self.h_move_iteration

        total_steps = int(duration * self.factor)

        for t in range(total_steps):
            if self.should_stop:
                # print("              Stop moving right")
                if t < total_steps // 2:
                    print("Stopped right too early")
                break
            # Attempt to reduce the performance impact of setting the cursor position every iteration
            if t % iteration == 0:
                ratio = self.ease_func(t / total_steps)

                win32api.SetCursorPos(
                    (
                        int(current_x + (x - current_x) * ratio),
                        int(current_y + (y - current_y) * ratio),
                    )
                )

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False

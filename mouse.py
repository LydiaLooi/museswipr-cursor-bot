from random import randint

from pytweening import easeOutQuad
from math import sin, pi
from win32api import GetCursorPos, GetSystemMetrics, SetCursorPos
from yaml import safe_load


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = GetSystemMetrics(0)
        self.screen_height = GetSystemMetrics(1)

        with open("config.yaml") as config_file:
            config = safe_load(config_file)

        self.y_middle = config["y_middle"]
        self.duration = config["duration"]
        self.faster_h_duration = config["faster_h_duration"]
        self.faster_v_duration = config["faster_v_duration"]
        self.factor = config["factor"]
        self.h_move_iteration = config["h_move_iteration"]
        self.v_move_iteration = config["v_move_iteration"]

        self.ease_func = easeOutQuad
        print("Mouse initialised.")

        print(f"Normal Duration Total steps: {int(self.duration * self.factor)}")
        print(
            f"Faster Duration Total steps: {int(self.faster_h_duration * self.factor)}"
        )

        print(f"H Move iteration: {self.h_move_iteration}")
        print(f"V Move iteration: {self.v_move_iteration}")

    def _move_straight(
        self, current_x, current_y, x, y, iteration, total_steps, extra=False
    ):
        early_threshold = total_steps * 0.7
        amplitude = 200  # This controls the curve height

        for t in range(total_steps):
            if self.should_stop:
                if t < early_threshold:
                    ratio = self.ease_func(early_threshold / total_steps)
                    # Calculate the displacement for the curve
                    displacement = 0
                    if extra:
                        displacement = amplitude * sin(
                            pi * ratio
                        )  # A simple sine curve
                        # Reverse displacement if on left or top half of screen
                        if (
                            current_x < self.screen_width / 2
                            or current_y < self.y_middle
                        ):
                            displacement = -displacement

                    dx = abs(x - current_x)
                    dy = abs(y - current_y)
                    if dx > dy:
                        SetCursorPos(
                            (
                                int(current_x + (x - current_x) * ratio),
                                int(
                                    current_y + (y - current_y) * ratio + displacement
                                ),  # Add displacement to Y
                            )
                        )
                    else:
                        SetCursorPos(
                            (
                                int(
                                    current_x + (x - current_x) * ratio + displacement
                                ),  # Add displacement to X
                                int(current_y + (y - current_y) * ratio),
                            )
                        )
                break

            # Attempt to reduce the performance impact of setting the cursor position every iteration
            if t % iteration == 0:
                ratio = self.ease_func(t / total_steps)

                # Calculate the displacement for the curve
                displacement = 0
                if extra:
                    displacement = amplitude * sin(pi * ratio)  # A simple sine curve
                    # Reverse displacement if on left or top half of screen
                    if current_x < self.screen_width / 2 or current_y < self.y_middle:
                        displacement = -displacement

                # If the X distance is longer, modify the y values. Otherwise, modify the x values.
                dx = abs(x - current_x)
                dy = abs(y - current_y)
                if dx > dy:
                    SetCursorPos(
                        (
                            int(current_x + (x - current_x) * ratio),
                            int(
                                current_y + (y - current_y) * ratio + displacement
                            ),  # Add displacement to Y
                        )
                    )
                else:
                    SetCursorPos(
                        (
                            int(
                                current_x + (x - current_x) * ratio + displacement
                            ),  # Add displacement to X
                            int(current_y + (y - current_y) * ratio),
                        )
                    )

    def move_left(self, speed=0):
        current_x, current_y = GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the left
        x = self.screen_width // 3 + randint(-25, 50)

        y_move = randint(180, 220)

        # Determine whether the cursor should be moving up or down.
        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        duration = self.duration
        extra = False
        # Movement type
        if current_x < self.screen_width // 2:
            # Vertical
            iteration = self.v_move_iteration
            if speed >= 1:
                duration = self.faster_v_duration
            elif speed == 2:
                extra = True
        else:
            # Horizontal
            iteration = self.h_move_iteration
            if speed >= 1:
                duration = self.faster_h_duration
            elif speed == 2:
                extra = True
        total_steps = int(duration * self.factor)
        self._move_straight(current_x, current_y, x, y, iteration, total_steps, extra)

    def move_right(self, speed=0):
        current_x, current_y = GetCursorPos()  # Get current mouse position

        # check self.should_stop after each step and stop if it's True
        x = self.screen_width * 2 // 3 + randint(-25, 25)

        y_move = randint(180, 220)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        duration = self.duration
        extra = False
        # Movement type
        if current_x < self.screen_width // 2:
            # Vertical
            iteration = self.v_move_iteration
            if speed == 1:
                duration = self.faster_v_duration
            elif speed == 2:
                extra = True
        else:
            # Horizontal
            iteration = self.h_move_iteration
            if speed == 1:
                duration = self.faster_h_duration
            elif speed == 2:
                extra = True

        total_steps = int(duration * self.factor)
        self._move_straight(current_x, current_y, x, y, iteration, total_steps, extra)

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False

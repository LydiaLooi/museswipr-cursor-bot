from random import randint

from pytweening import easeOutQuad
from math import sin, pi
from win32api import GetCursorPos, GetSystemMetrics, SetCursorPos
from yaml import safe_load


# TODO: This currently roughly tries to get cool flowy curves but only for 3 stacks and if the horizontal swipes begin
# from the lower half of the screen... like the shape below
#   _  |   _
# |  \ |  / \
#  \___|___/
#      |
# To get it to always circle properly, it needs to know if the previous vertical swipe was negative displaced or not.
def is_negative_displacement(horizontal_last, current_x, current_y, x_middle, y_middle):
    if horizontal_last and current_x < x_middle:
        return True
    elif not horizontal_last and current_x > x_middle:
        return True
    return False


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = GetSystemMetrics(0)
        self.x_middle = self.screen_width // 2
        self.screen_height = GetSystemMetrics(1)

        with open("config.yaml") as config_file:
            config = safe_load(config_file)

        self.y_middle = config["y_middle"]

        self.y_lower_bound = self.y_middle - 200
        self.y_upper_bound = self.y_middle + 200

        self.duration = config["duration"]
        self.faster_h_duration = config["faster_h_duration"]
        self.faster_v_duration = config["faster_v_duration"]
        self.factor = config["factor"]
        self.h_move_iteration = config["h_move_iteration"]
        self.v_move_iteration = config["v_move_iteration"]

        self.left_h_move_true = config["left_h_move_true"]
        self.right_h_move_true = config["right_h_move_true"]
        self.y_bias = config["y_bias"]

        self.ease_func = easeOutQuad
        print("Mouse initialised.")

        print(f"Normal Duration Total steps: {int(self.duration * self.factor)}")
        print(
            f"Faster Duration Total steps: {int(self.faster_h_duration * self.factor)}"
        )

        print(f"H Move iteration: {self.h_move_iteration}")
        print(f"V Move iteration: {self.v_move_iteration}")

    def _move_straight(
        self,
        x,
        y,
        iteration,
        total_steps,
        swipe_type,
        extra=False,
        horizontal_last=True,
    ):
        current_x, current_y = GetCursorPos()  # Get current mouse position
        early_threshold = total_steps * 0.7
        amplitude = 150  # This controls the curve height

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
                        if swipe_type == "V":
                            if is_negative_displacement(
                                horizontal_last,
                                current_x,
                                current_y,
                                self.x_middle,
                                self.y_middle,
                            ):
                                displacement = -displacement

                        else:
                            # Reverse displacement if on top half of screen and is a horizontal swipe
                            # Always makes it curve outwards from the middle...
                            if current_y < self.y_middle:
                                displacement = -displacement

                    if swipe_type == "H":  # Horizontal movement
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
                    if swipe_type == "V":
                        # Is a vertical swipe....
                        # if the last swipe was horziontal... and in left of screen ... NEGATIVE
                        #                   and in right of screen ... POSITION
                        # Else....
                        #                   in left of screen .. POS
                        #                   in right of screen NEG
                        if is_negative_displacement(
                            horizontal_last,
                            current_x,
                            current_y,
                            self.x_middle,
                            self.y_middle,
                        ):
                            displacement = -displacement
                    else:
                        # Reverse displacement if on top half of screen and is a horizontal swipe
                        # Always makes it curve outwards from the middle...
                        if current_y < self.y_middle:
                            displacement = -displacement

                if swipe_type == "H":  # Horizontal movement
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

    def move_left(self, speed=0, last_swipe_horizontal=True):
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
        if current_x < self.x_middle:
            # Vertical
            swipe_type = "V"
            iteration = self.v_move_iteration
            if speed == 1:
                duration = self.faster_v_duration
            elif speed == 2:
                extra = True
        else:
            # Horizontal
            swipe_type = "H"
            if self.left_h_move_true:
                # No bias
                lower = self.y_lower_bound
                upper = self.y_upper_bound
                if self.y_bias == 1:
                    upper = self.y_lower_bound
                elif self.y_bias == 2:
                    lower = self.y_upper_bound
                y = max(
                    lower,
                    min(current_y, upper),
                ) + randint(-20, 20)
            iteration = self.h_move_iteration
            if speed == 1:
                duration = self.faster_h_duration
            elif speed == 2:
                extra = True

        total_steps = int(duration * self.factor)
        self._move_straight(
            x, y, iteration, total_steps, swipe_type, extra, last_swipe_horizontal
        )

    def move_right(self, speed=0, last_swipe_horizontal=True):
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
        if current_x > self.x_middle:
            # Vertical
            swipe_type = "V"
            iteration = self.v_move_iteration
            if speed == 1:
                duration = self.faster_v_duration
            elif speed == 2:
                extra = True
        else:
            # Horizontal
            swipe_type = "H"
            if self.right_h_move_true:
                # No bias
                lower = self.y_lower_bound
                upper = self.y_upper_bound
                if self.y_bias == 1:
                    upper = self.y_lower_bound
                elif self.y_bias == 2:
                    lower = self.y_upper_bound
                y = max(
                    lower,
                    min(current_y, upper),
                ) + randint(-20, 20)
            iteration = self.h_move_iteration
            if speed == 1:
                duration = self.faster_h_duration
            elif speed == 2:
                extra = True

        total_steps = int(duration * self.factor)
        self._move_straight(
            x, y, iteration, total_steps, swipe_type, extra, last_swipe_horizontal
        )

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False

from random import randint

from pytweening import easeInSine, easeInOutPoly, easeOutSine, linear

from win32api import GetCursorPos, GetSystemMetrics, SetCursorPos


class Mouse:
    def __init__(self):
        self.should_stop = False
        self.screen_width = GetSystemMetrics(0)
        self.screen_height = GetSystemMetrics(1)

        self.y_middle = self.screen_height // 2 - 130

        self.duration = 70  # 100 60fps
        self.faster_h_duration = 45  # 6 60 fps $ 4??fps 45 is good for horizontalGHOST but not enough for vertical
        self.faster_v_duration = 45
        self.factor = 10000

        self.h_move_iteration = 500
        self.v_move_iteration = 500

        self.ease_func = easeOutSine
        print("Mouse initialised.")

        print(f"Normal Duration Total steps: {int(self.duration * self.factor)}")
        print(
            f"Faster Duration Total steps: {int(self.faster_h_duration * self.factor)}"
        )

        print(f"H Move iteration: {self.h_move_iteration}")
        print(f"V Move iteration: {self.v_move_iteration}")

    def _move_straight(self, current_x, current_y, x, y, iteration, total_steps):
        early_threshold = total_steps // 2
        for t in range(total_steps):
            if self.should_stop:
                if t < early_threshold:
                    ratio = self.ease_func(early_threshold / total_steps)

                    SetCursorPos(
                        (
                            int(current_x + (x - current_x) * ratio),
                            int(current_y + (y - current_y) * ratio),
                        )
                    )
                break

            # Attempt to reduce the performance impact of setting the cursor position every iteration
            if t % iteration == 0:
                ratio = self.ease_func(t / total_steps)

                SetCursorPos(
                    (
                        int(current_x + (x - current_x) * ratio),
                        int(current_y + (y - current_y) * ratio),
                    )
                )

    def move_left(self, faster=False):
        current_x, current_y = GetCursorPos()  # Get current mouse position

        # implement the action of moving the mouse to the left
        x = self.screen_width // 3 + randint(-25, 50)

        y_move = randint(200, 230)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        if faster:
            duration = self.faster_h_duration
        else:
            duration = self.duration

        # Movement type
        if current_x < self.screen_width // 2:
            iteration = self.v_move_iteration
            if faster:
                duration = self.faster_v_duration
        else:
            iteration = self.h_move_iteration

        total_steps = int(duration * self.factor)
        self._move_straight(current_x, current_y, x, y, iteration, total_steps)

    def move_right(self, faster=False):
        current_x, current_y = GetCursorPos()  # Get current mouse position

        # check self.should_stop after each step and stop if it's True
        x = self.screen_width * 2 // 3 + randint(-25, 25)

        y_move = randint(100, 150)

        if current_y > self.y_middle:
            y = self.y_middle - y_move
        else:
            y = self.y_middle + y_move

        if faster:
            duration = self.faster_h_duration
        else:
            duration = self.duration

        # Movement type
        if current_x < self.screen_width // 2:
            iteration = self.v_move_iteration
            if faster:
                duration = self.faster_v_duration
        else:
            iteration = self.h_move_iteration

        total_steps = int(duration * self.factor)

        self._move_straight(current_x, current_y, x, y, iteration, total_steps)

    def stop(self):
        self.should_stop = True

    def start(self):
        self.should_stop = False

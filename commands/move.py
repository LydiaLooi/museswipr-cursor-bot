from commands.command import Command
from mouse import Mouse


class MoveLeftCommand(Command):
    def __init__(self, mouse: Mouse, speed=0, last_swipe_horizontal=True):
        self.mouse = mouse
        self.speed = speed
        self.last_swipe_horizontal = last_swipe_horizontal

    def execute(self):
        self.mouse.start()
        self.mouse.move_left(self.speed, self.last_swipe_horizontal)

    def stop(self):
        self.mouse.stop()


class MoveRightCommand(Command):
    def __init__(self, mouse: Mouse, speed=0, last_swipe_horizontal=True):
        self.mouse = mouse
        self.speed = speed
        self.last_swipe_horizontal = last_swipe_horizontal

    def execute(self):
        self.mouse.start()
        self.mouse.move_right(self.speed, self.last_swipe_horizontal)

    def stop(self):
        self.mouse.stop()

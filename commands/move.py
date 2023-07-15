from commands.command import Command
from mouse import Mouse


class MoveLeftCommand(Command):
    def __init__(self, mouse: Mouse, speed=0):
        self.mouse = mouse
        self.speed = speed

    def execute(self):
        self.mouse.start()
        self.mouse.move_left(self.speed)

    def stop(self):
        self.mouse.stop()


class MoveRightCommand(Command):
    def __init__(self, mouse: Mouse, speed=0):
        self.mouse = mouse
        self.speed = speed

    def execute(self):
        self.mouse.start()
        self.mouse.move_right(self.speed)

    def stop(self):
        self.mouse.stop()

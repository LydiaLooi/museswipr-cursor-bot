from commands.command import Command
from mouse import Mouse


class MoveLeftCommand(Command):
    def __init__(self, mouse: Mouse, faster=False):
        self.mouse = mouse
        self.faster = faster

    def execute(self):
        self.mouse.start()
        self.mouse.move_left(self.faster)

    def stop(self):
        self.mouse.stop()


class MoveRightCommand(Command):
    def __init__(self, mouse: Mouse, faster=False):
        self.mouse = mouse
        self.faster = faster

    def execute(self):
        self.mouse.start()
        self.mouse.move_right(self.faster)

    def stop(self):
        self.mouse.stop()

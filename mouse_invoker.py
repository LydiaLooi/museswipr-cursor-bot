from threading import Thread

from mouse import Mouse
from commands.command import Command


class MouseMoveInvoker:
    def __init__(self, mouse: Mouse):
        self.mouse = mouse
        self.command = None
        self.current_thread = None

    def set_command(self, command: Command):
        # If there is a current command being executed, stop it
        if self.command:
            self.command.stop()

        self.command = command

        # Start a new thread to execute the command
        self.current_thread = Thread(target=self.execute_command)
        self.current_thread.start()

    def execute_command(self):
        if self.command:
            self.command.execute()

import os

class Signal:
    """
    simple IPC mechanism to signal the other process once when forked
    (either parent to child or child to parent)
    """
    def __init__(self):
        self.pipe = os.pipe()
        pid = os.fork()

        self.CHILD = pid == 0
        self.PARENT = pid != 0

    def signal(self):
        os.close(self.pipe[0])
        os.close(self.pipe[1])

    def wait(self):
        os.close(self.pipe[1])
        with os.fdopen(self.pipe[0], "r") as f:
            f.read()

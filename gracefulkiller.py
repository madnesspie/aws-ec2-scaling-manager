import signal


class GracefulKiller:
    def __init__(self):
        self.pardoned = True
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.pardoned = False

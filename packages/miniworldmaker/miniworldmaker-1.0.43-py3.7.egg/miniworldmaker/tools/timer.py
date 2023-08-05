from miniworldmaker.app import app

class Timed():
    def __init__(self):
        self.board = app.App.board
        self.board.timed_objects.append(self)

    def tick(self):
        self.time = self.time - 1

    def unregister(self):
        self.board.timed_objects.remove(self)
        del(self)

class Timer(Timed):
    def __init__(self, time):
        super().__init__()
        self.time = time
        self.actual_time = 0

    def tick(self):
        self.actual_time += 1
        if self.actual_time % self.time == 0:
            self.act()

    def act(self):
        pass


class ZeroTimer(Timed):
    def __init__(self, time):
        super().__init__()
        self.time = time

    def tick(self):
        self.time -= 1
        if self.time == 0:
            self.act()
            self.unregister()

    def act(self):
        pass


class ActionTimer(ZeroTimer):

    def __init__(self, time, method, parameters):
        super().__init__(time)
        self.method = method
        self.parameters = parameters

    def act(self):
        self.method(self.parameters)


class LoopActionTimer(Timer):

    def __init__(self, time, method, parameters):
        super().__init__(time)
        self.method = method
        self.parameters = parameters

    def act(self):
        self.method(self.parameters)


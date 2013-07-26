from hsmpy import Event


class Mouse_Event(Event):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.data = (x, y)

class Mouse_Down(Mouse_Event): pass
class Mouse_Up(Mouse_Event): pass
class Mouse_Move(Mouse_Event): pass

class Tool_Changed(Event): pass

class Commit_To_Model(Event): pass
class Model_Changed(Event): pass

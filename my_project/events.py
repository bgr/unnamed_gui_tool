from hsmpy import Event

PATH_TOOL = 'path tool'
COMBO_TOOL = 'combo tool'
ELLIPSE_TOOL = 'ellipse tool'


class Mouse_Event(Event):
    def __init__(self, *args):
        if len(args) == 1:  # single argument is original MouseEvent
            self.orig = args[0]  # remember original event, might need it
            self.x = self.orig.x
            self.y = self.orig.y
        elif len(args) == 2:  # two arguments are x y coordinates
            self.orig = None
            self.x = args[0]
            self.y = args[1]
        self.data = (self.x, self.y)

class Mouse_Down(Mouse_Event): pass
class Mouse_Up(Mouse_Event): pass
class Mouse_Move(Mouse_Event): pass

class Tool_Changed(Event): pass

class Commit_To_Model(Event): pass
class Model_Changed(Event): pass

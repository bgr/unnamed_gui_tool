from hsmpy import Event

PATH_TOOL = 'path tool'
COMBO_TOOL = 'combo tool'
ELLIPSE_TOOL = 'ellipse tool'
LINK_TOOL = 'link tool'


class WrappedEvent(Event):
    def __init__(self, original_event):
        self.orig = original_event

    def __getattr__(self, name):
        return getattr(self.orig, name)


class Tool_Changed(Event): pass

class Model_Changed(Event): pass

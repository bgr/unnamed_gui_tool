from javax.swing import SwingUtilities
from java.lang import Runnable


class Run(Runnable):
    def __init__(self, func, *args, **kwargs):
        """Python wrapper for Java Runnable"""
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        assert SwingUtilities.isEventDispatchThread(), "not on EDT"
        self.func(*self.args, **self.kwargs)


def invokeLater(func):
    """Decorator for running functions on Swing's Event Dispatch Thread"""
    def wrapped(*args, **kwargs):
        SwingUtilities.invokeLater(Run(func, *args, **kwargs))
    return wrapped

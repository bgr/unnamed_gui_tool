import java.lang
from javax.swing import SwingUtilities
from javax.swing import JButton, ImageIcon


class Runnable(java.lang.Runnable):
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
        SwingUtilities.invokeLater(Runnable(func, *args, **kwargs))
    return wrapped


def make_button(label, tooltip_text, icon_file_path=None):
    """Returns a JButton"""
    button = JButton()
    button.actionCommand = label
    button.toolTipText = tooltip_text
    if icon_file_path:
        button.icon = ImageIcon(icon_file_path, tooltip_text.upper())
    else:
        button.text = label
    return button

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


def make_button(icon_filename, action_cmd_str, tooltip_text, alt_text):
    """Returns a JButton"""
    button = JButton()
    button.actionCommand = action_cmd_str
    button.toolTipText = tooltip_text
    if icon_filename:
        button.icon = ImageIcon(icon_filename, alt_text)
    else:
        button.text = alt_text
        print "Resource not found: " + icon_filename
    return button

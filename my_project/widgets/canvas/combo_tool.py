import logging
_log = logging.getLogger(__name__)

from javax.swing import SwingUtilities

from hsmpy import Initial, T, Choice, Internal

from ...app import S
from ... import model
from ...util import fseq
from ...events import Commit_To_Model



def make(eb, view, Canvas_Down, Canvas_Up, Canvas_Move, Tool_Done):
    """
        Returns separate states dicts and trans dict for idle and engaged tool
        behaviors as a tuple:
            (idle_state_dict, engaged_state_dict, transitions_dict)
        so that they can be integrated within parent states by simple dict
        joining, performed in widgets.canvas.main.make function.
    """

    idle = {
        'combo_idle': S(),
    }

    engaged = {
        'combo_engaged': S(on_enter=lambda h: eb.dispatch(Tool_Done())),
    }

    trans = {
        'combo_idle': {
            Canvas_Down: T('combo_engaged'),
        },
    }

    return (idle, engaged, trans)

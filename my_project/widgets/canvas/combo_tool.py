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
        'combo_idle': S({
            'combo_over_background': S(),
            #'combo_over_unselected_element': S(),
            #'combo_over_selected_element': S(),
        }),
    }

    engaged = {
        'combo_engaged': S({
            'combo_dragging_marquee': S(),
            #'combo_dragging_selection': S(),
        }),
    }

    def whats_under_cursor(evt, hsm):
        el = next(iter(view.elements_at(evt.x, evt.y)), None)
        _log.info('under cursor is {0}'.format(el))


    hover_choice = Choice({
        None: 'combo_over_background',
        'unselected': 'combo_over_unselected_element',
        #'selected': 'combo_over_selected_element',
    }, key=whats_under_cursor, default='combo_over_background')

    def printer(msg):
        def func(e, h):
            _log.info(msg)
            _log.info(e)
        return func


    trans = {
        'combo_idle': {
            Initial: T('combo_over_background'),
            #Canvas_Move: hover_choice,
            Canvas_Move: Internal(whats_under_cursor)
        },
        'combo_engaged': {
            Initial: T('combo_dragging_marquee', action=lambda _, __: 1 / 0),
            Canvas_Up: Internal(lambda _, __: eb.dispatch(Tool_Done())),
        },

        'combo_over_background': {
            Canvas_Down: T('combo_dragging_marquee'),
        },
        #'combo_over_unselected_element': {
            #Canvas_Down: T('combo_dragging_selection'),
        #},

        'combo_dragging_marquee': {
            Canvas_Move: Internal(printer("I'm dragging marquee")),
        },
        #'combo_dragging_selection': {
            #Canvas_Move: Internal(printer("I'm dragging some elements")),
        #}
    }

    return (idle, engaged, trans)

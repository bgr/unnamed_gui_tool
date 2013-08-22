import logging
_log = logging.getLogger(__name__)

from hsmpy import Event, Initial, T, Internal
from ... import model
from ...app import S
from ...events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                       Commit_To_Model, Model_Changed)

import canvas

# tool behaviors are defined using sub-HSMs in separate modules:
import shape_tool



# interaction with model

def commit_to_model(evt, hsm):
    """Creates a changelist and dispatches event that'll cause model update."""
    el = hsm.data.canvas_temp_elem
    if el.width == 0 and el.height == 0:
        _log.info("not commiting {0} (0 dimensions)".format(el))
        1 / 0
        return
    _log.info("committing to model {0}".format(el))
    # dispatch event to add to model
    hsm.eb.dispatch(Commit_To_Model( [model.Insert(el)] ))



# 'top' state actions

def set_up(evt, hsm):
    hsm.data.canvas_tool = model.Rectangle
    _log.info("HSM tool set to {0}".format(hsm.data.canvas_tool))


def remember_selected_tool(evt, hsm):
    hsm.data.canvas_tool = evt.data
    _log.info('remembered selected tool {0}'.format(hsm.data.canvas_tool))



def make(eventbus):
    # declaring events here in order to make sure that each view-controller
    # pair has their own unique events, to prevent one controller responding
    # to other's view's events
    class Canvas_Down(Mouse_Down): pass
    class Canvas_Up(Mouse_Up): pass
    class Canvas_Move(Mouse_Move): pass
    class Tool_Done(Event): pass

    view = canvas.CanvasView(300, 300)
    view.mouseReleased = lambda e: eventbus.dispatch(Canvas_Up(e.x, e.y))
    view.mouseMoved = lambda e: eventbus.dispatch(Canvas_Move(e.x, e.y))
    view.mouseDragged = view.mouseMoved
    view.mousePressed = lambda e: eventbus.dispatch(Canvas_Down(e.x, e.y))

    shape_states, shape_trans = shape_tool.make(eventbus, view, Canvas_Down,
                                                Canvas_Up, Canvas_Move,
                                                Tool_Done)

    states = {
        'top': S(on_enter=set_up, states={
            'tools_idle': S({
                'shape_tool': S([ (shape_states, shape_trans) ]),
            }),
        })
    }


    update_view = lambda evt, _: view.draw_changes(evt.data)

    trans = {
        'top': {
            Initial: T('tools_idle'),
            Tool_Changed: Internal(action=remember_selected_tool),
            Model_Changed: Internal(action=update_view),
        },
        'tools_idle': {
            Initial: T('shape_tool'),
            Tool_Done: T('tools_idle'),  # loop, maybe tool was changed
        },
    }

    return (view, states, trans)

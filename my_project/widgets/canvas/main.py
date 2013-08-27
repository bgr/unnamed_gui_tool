import logging
_log = logging.getLogger(__name__)

from hsmpy import Event, Initial, T, Internal
from ... import model
from ...app import S
from ...events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                       Model_Changed)

from CanvasView import CanvasView

# tool behaviors are defined using sub-HSMs in separate modules:
import shape_tool



# HSM state/transition actions:

def set_up(evt, hsm):
    hsm.data.canvas_tool = model.Rectangle
    _log.info("HSM tool set to {0}".format(hsm.data.canvas_tool))


def remember_selected_tool(evt, hsm):
    hsm.data.canvas_tool = evt.data
    _log.info('remembered selected tool {0}'.format(hsm.data.canvas_tool))



def make(eventbus):
    """
        Main function that creates the view instance wired up with HSM states
        and transitions that this function returns, which are ready to be used
        as a standalone HSM or assembled into larger HSM hierarchy as
        submachines.
    """
    # declaring events here in order to make sure that each view-controller
    # pair has their own unique events, to prevent one controller responding
    # to other's view's events
    class Canvas_Down(Mouse_Down): pass
    class Canvas_Up(Mouse_Up): pass
    class Canvas_Move(Mouse_Move): pass
    class Tool_Done(Event): pass

    view = CanvasView(300, 300)
    view.mouseReleased = lambda evt: eventbus.dispatch(Canvas_Up(evt))
    view.mouseMoved = lambda evt: eventbus.dispatch(Canvas_Move(evt))
    view.mouseDragged = view.mouseMoved
    view.mousePressed = lambda evt: eventbus.dispatch(Canvas_Down(evt))

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
            Tool_Done: T('tools_idle'),  # reenter, tool may have changed
        },
    }

    return (view, states, trans)

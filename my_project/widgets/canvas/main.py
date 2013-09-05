import logging
_log = logging.getLogger(__name__)

from hsmpy import Event, Initial, T, Internal, Choice
from ...app import S
from ...util import join_dicts
from ...events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                       Model_Changed, PATH_TOOL, COMBO_TOOL)
from CanvasView import CanvasView

# tool behaviors are defined using sub-HSMs in separate modules:
import path_tool
import combo_tool



def make(eventbus, model_query):
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

    view = CanvasView(300, 300, model_query)
    view.mouseReleased = lambda evt: eventbus.dispatch(Canvas_Up(evt))
    view.mouseMoved = lambda evt: eventbus.dispatch(Canvas_Move(evt))
    view.mouseDragged = view.mouseMoved
    view.mousePressed = lambda evt: eventbus.dispatch(Canvas_Down(evt))

    def set_up(hsm):
        hsm.data.canvas_tool = COMBO_TOOL
        _log.info("HSM tool set to {0}".format(hsm.data.canvas_tool))

    def remember_selected_tool(evt, hsm):
        hsm.data.canvas_tool = evt.data
        _log.info('remembered selected tool {0}'.format(hsm.data.canvas_tool))


    path_idle, path_engaged, path_trans = path_tool.make(
        eventbus, view, Canvas_Down, Canvas_Up, Canvas_Move, Tool_Done)

    combo_idle, combo_engaged, combo_trans = combo_tool.make(
        eventbus, view, Canvas_Down, Canvas_Up, Canvas_Move, Tool_Done)


    states = {
        'top': S(on_enter=set_up, states={
            'idle': S(join_dicts(
                path_idle,
                combo_idle,
            )),
            'engaged': S(join_dicts(
                path_engaged,
                combo_engaged,
            )),
        })
    }


    update_view = lambda evt, _: view.draw_changes(evt.data)
    get_tool = lambda _, hsm: hsm.data.canvas_tool or COMBO_TOOL


    trans = join_dicts(
        path_trans,
        combo_trans,
        {
            'top': {
                Initial: T('idle'),
                Model_Changed: Internal(action=update_view),
            },
            'idle': {
                Initial: Choice(
                    {
                        COMBO_TOOL: 'combo_idle',
                        PATH_TOOL: 'path_idle',
                        # TODO: reorganize code, referencing state name that's
                        # not specified in this file = ugly
                    },
                    default='path_idle',
                    key=get_tool),
                # tool is idle, safe to change to another tool by reentering
                Tool_Changed: T('idle', action=remember_selected_tool),
            },
            'engaged': {
                # should never be called since substates are always
                # transitioned to directly
                Initial: T('path_engaged', action=lambda _, __: 1 / 0),
                # tool is engaged, remember new tool for later, don't change
                Tool_Changed: Internal(action=remember_selected_tool),
                Tool_Done: T('idle'),
            },
        }
    )

    return (view, states, trans)

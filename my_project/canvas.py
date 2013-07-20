from javax.swing import JPanel
from java.awt import Color
from model import Rectangle, Circle
from hsmpy import State, Initial
from hsmpy import Transition as T
from hsmpy import InternalTransition as Internal
import logging

from events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                    Commit_To_Model, Model_Changed)


_log = logging.getLogger(__name__)

from collections import namedtuple


class LoggingState(State):
    def enter(self, evt, hsm):
        _log.debug('entering {0}'.format(self.name))

    def exit(self, evt, hsm):
        _log.debug('exiting {0}'.format(self.name))


# alias class so that it can easily be switched
S = LoggingState


def draw_rectangle(el, g):
    g.drawRect(el.x, el.y, el.radius, el.radius)


def draw_circle(el, g):
    g.drawOval(el.x, el.y, el.radius, el.radius)


element_components = {
    Circle: draw_circle,
    Rectangle: draw_rectangle,
}


class CanvasView(JPanel):

    def __init__(self, width, height, eb):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self.mousePressed = lambda e: eb.dispatch(Mouse_Down(e.x, e.y))
        self.mouseReleased = lambda e: eb.dispatch(Mouse_Up(e.x, e.y))
        self.mouseMoved = lambda e: eb.dispatch(Mouse_Move(e.x, e.y))

        self._elems = []
        self._selected_ids = set([])

    @property
    def elems(self):
        return self._elems

    @elems.setter
    def elems(self, new_elems):
        self._elems = new_elems
        for el in new_elems:
            comp = element_components[el.__class__](el)
            self.add(comp)
        #self.repaint()

    def add_elem(self, elem):
        self._elems.append(elem)
        self.repaint()

    @property
    def selection(self):
        return self._selected_ids

    @selection.setter
    def selection(self, elem_id_set):
        self._selected_ids = elem_id_set
        self.repaint()


    def paintComponent(self, g):
        # TODO: repaint only changed regions
        for el in self.elems:
            self.draw_handlers[el.__class__](el, g)


def make(eventbus):
    view = CanvasView(300, 300, eventbus)

    def set_active_tool(self, evt, hsm):
        _log.info("set tool to rect")
        hsm.data.tool = 'rectangle'

    states = {
        'top': S(on_enter=set_active_tool, states={
            'idle': S(),
            'drawing': S({
                'drawing_rectangle': S(),
                'drawing_circle': S(),
            })
        })
    }

    #tool_is_combo = lambda e, hsm: hsm.data.tool == 'combo'
    #tool_is_rectangle = lambda e, hsm: hsm.data.tool == 'rectangle'
    #tool_is_circle = lambda e, hsm: hsm.data.tool == 'circle'

    def print_tool(e, h):
        _log.info('event {0}'.format(e))
        _log.info('current tool {0}'.format(h.data.tool))

    def remember_tool(evt, hsm):
        hsm.data.tool = evt.data
        _log.info('remembered selected tool {0}'.format(hsm.data.tool))

    def draw_added_element(evt, hsm):
        _log.info('draw added element {0}'.format(evt.data))
        view.add(evt.data)


    trans = {
        'top': {
            Initial: T('idle'),
            Tool_Changed: Internal(action=remember_tool),
            Model_Changed: Internal(action=draw_added_element),
        },
        'idle': {
            Mouse_Down: T('drawing_rectangle', action=print_tool),  # guard!
        },
        'drawing': {
            Initial: T('drawing_circle'),
            Mouse_Up: T('idle', action=commit_to_model),
        },
        'drawing_rectangle': {
            Mouse_Move: Internal(action=on_move),
        },
        'drawing_circle': {
            Mouse_Move: Internal(action=on_move),
        },
    }

    return (view, states, trans)


def commit_to_model(evt, hsm):
    _log.info("committing to model {0}".format(hsm.data.element))
    # dispatch event to add to model
    hsm.eb.dispatch(Commit_To_Model(hsm.data.element))
    hsm.data.element = None

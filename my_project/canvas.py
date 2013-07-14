from javax.swing import JPanel
from java.awt import Color
from model import Rectangle, Circle
from hsmpy import State, CompositeState, Initial
from hsmpy import Transition as T
from hsmpy import InternalTransition as Internal
import logging

from events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                    Commit_To_Model, Model_Changed)


_log = logging.getLogger(__name__)


class Top(CompositeState):
    def enter(self, evt, hsm):
        hsm.data.tool = 'rectangle'
        _log.debug('entered Top, set tool to {0}'.format(hsm.data.tool))

    def exit(self, evt, hsm):
        _log.debug('exiting Top')


class Drawing(CompositeState):
    def enter(self, evt, hsm):
        _log.debug('entered Drawing superstate')

    def exit(self, evt, hsm):
        _log.debug('exiting Drawing superstate')


class Idle(State):
    def enter(self, evt, hsm):
        _log.debug('entered Idle')

    def exit(self, evt, hsm):
        _log.debug('exiting Idle')


def on_move(evt, hsm):
    _log.debug('move {0}'.format(evt))


class DrawingRectangle(State):
    def enter(self, mouse_evt, hsm):
        _log.debug('entered Drawing_Rectangle')
        self.start_x = mouse_evt.x
        self.start_y = mouse_evt.y

    def exit(self, mouse_evt, hsm):
        _log.debug('exiting Drawing_Rectangle')
        w = mouse_evt.x - self.start_x
        h = mouse_evt.y - self.start_y
        hsm.data.element = Rectangle(self.start_x, self.start_y, w, h)


class DrawingCircle(State):
    def enter(self, mouse_evt, hsm):
        _log.debug('entered Drawing_Circle')

    def exit(self, mouse_evt, hsm):
        _log.debug('exiting Drawing_Circle')



class CanvasView(JPanel):

    def __init__(self, width, height, eb):
        super(CanvasView, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self.mousePressed = lambda e: eb.dispatch(Mouse_Down(e.x, e.y))
        self.mouseReleased = lambda e: eb.dispatch(Mouse_Up(e.x, e.y))
        self.mouseMoved = lambda e: eb.dispatch(Mouse_Move(e.x, e.y))

        self.draw_handlers = {
            Circle: self.draw_circle,
            Rectangle: self.draw_rectangle,
        }

    @property
    def elems(self):
        return self._elems

    @elems.setter
    def elems(self, new_elems):
        self._elems = new_elems
        self.repaint()

    def add(self, elem):
        self._elems.append(elem)
        self.repaint()

    def paintComponent(self, g):
        g.setColor(Color(255, 255, 255))
        g.fillRect(0, 0, self.preferredSize.width, self.preferredSize.height)

        g.setColor(Color(25, 25, 25))
        for el in self.elems:
            self.draw_handlers[el.__class__](g, el)

    def draw_circle(self, g, el):
        g.drawOval(el.x, el.y, el.radius, el.radius)

    def draw_rectangle(self, g, el):
        g.drawRect(el.x, el.y, el.width, el.height)

    def add_circle(self, g, el):
        g.drawOval(el.x, el.y, el.radius, el.radius)

    def add_rectangle(self, g, el):
        g.drawRect(el.x, el.y, el.width, el.height)


def make(eventbus):
    view = CanvasView(300, 300, eventbus)

    states = {
        'top': Top({
            'idle': Idle(),
            'drawing': Drawing({
                'drawing_rectangle': DrawingRectangle(),
                'drawing_circle': DrawingCircle(),
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

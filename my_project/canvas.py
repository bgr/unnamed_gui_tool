from javax.swing import JPanel
from java.awt import Color
from model import Rectangle, Ellipse
from hsmpy import State, Initial
from hsmpy import Transition as T
from hsmpy import InternalTransition as Internal
import logging

from events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                    Commit_To_Model, Model_Changed)
from model import Modify, Insert, Remove


_log = logging.getLogger(__name__)


class LoggingState(State):
    def enter(self, evt, hsm):
        _log.debug('entering {0}'.format(self.name))

    def exit(self, evt, hsm):
        _log.debug('exiting {0}'.format(self.name))


# alias class so that it can easily be switched
S = LoggingState


class CanvasView(JPanel):

    def __init__(self, width, height, drawing_handlers):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self._elems = []
        self._selected = set([])
        self.drawing_handlers = drawing_handlers
        self._background_color = Color.WHITE
        self._stroke_color = Color.BLACK

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.repaint()

    def add_elem(self, elem, repaint=False):
        self._elems += [elem]
        if repaint:
            self.repaint()

    def remove_elem(self, elem, repaint=False):
        self._elems.remove(elem)
        if repaint:
            self.repaint()

    @property
    def selection(self):
        return self._selected

    @selection.setter
    def selection(self, elems):
        self._selected = set(elems)
        self.repaint()

    def paintComponent(self, g):
        # TODO: repaint only changed regions
        g.color = self.background_color
        g.fillRect(0, 0, self.width, self.height)
        g.color = self._stroke_color
        for el in self._elems:
            self.drawing_handlers[el.__class__](el, g)



# top state

def set_up(evt, hsm):
    hsm.data.canvas_tool = Rectangle
    _log.info("HSM tool set to {0}".format(hsm.data.canvas_tool))


def remember_tool(evt, hsm):
    hsm.data.canvas_tool = evt.data
    _log.info('HSM remembered selected tool {0}'.format(hsm.data.canvas_tool))


# idle

def reset_temp_elem(evt, hsm):
    hsm.data.canvas_elem_type = None
    hsm.data.canvas_temp_elem = None


# guard for selected tool
# TODO: won't suffice, requires conditional transition support

def tool_is(element):
    return lambda _, hsm: hsm.data.canvas_tool == element


# drawing

def remember_coordinates(evt, hsm):
    hsm.data.canvas_start_x = evt.x
    hsm.data.canvas_start_y = evt.y


def make_temp_rectangle(evt, hsm):
    hsm.data.canvas_elem_type = Rectangle


def make_temp_ellipse(evt, hsm):
    hsm.data.canvas_elem_type = Ellipse


# drawing - interaction with CanvasView

def draw_rectangle(el, g):
    #_log.info("Draw rectangle {0}".format(el))
    g.drawRect(*map(int, el))


def draw_ellipse(el, g):
    #_log.info("Draw ellipse {0}".format(el))
    g.drawOval(el.x, el.y, el.width, el.height)


drawing_handlers = {
    Ellipse: draw_ellipse,
    Rectangle: draw_rectangle,
}


def fseq(functions, *args, **kwargs):
    return lambda *args, **kwargs: [f(*args, **kwargs) for f in functions]


def draw_changes(changes, view):
    switch = {
        Insert: lambda ch: view.add_elem(ch.elem),
        Remove: lambda ch: view.remove_elem(ch.elem),
        Modify: fseq([
            lambda ch: view.remove_elem(ch.elem),
            lambda ch: view.add_elem(ch.modified)
        ]),
    }
    [switch[ch.__class__](ch) for ch in changes]
    view.repaint()


# interaction with model

def commit_to_model(evt, hsm):
    _log.debug("committing to model {0}".format(hsm.data.canvas_temp_elem))
    # dispatch event to add to model
    hsm.eb.dispatch(Commit_To_Model( [Insert(hsm.data.canvas_temp_elem)] ))



def make(eventbus):
    # creating here so that each view-controller pair has their unique events
    class Canvas_Down(Mouse_Down): pass
    class Canvas_Up(Mouse_Up): pass
    class Canvas_Move(Mouse_Move): pass

    view = CanvasView(300, 300, drawing_handlers)
    view.mouseReleased = lambda e: eventbus.dispatch(Canvas_Up(e.x, e.y))
    view.mouseMoved = lambda e: eventbus.dispatch(Canvas_Move(e.x, e.y))
    view.mouseDragged = view.mouseMoved
    view.mousePressed = lambda e: eventbus.dispatch(Canvas_Down(e.x, e.y))

    states = {
        'top': S(on_enter=set_up, states={
            'idle': S(on_enter=reset_temp_elem),
            'drawing': S(on_enter=remember_coordinates, states={
                'drawing_rectangle': S(on_enter=make_temp_rectangle),
                'drawing_ellipse': S(on_enter=make_temp_ellipse),
            })
        })
    }

    def mock_model_changes(evt, hsm):
        x = hsm.data.canvas_start_x
        y = hsm.data.canvas_start_y
        width = evt.x - x
        height = evt.y - y
        if width == 0 or height == 0:
            return

        cls = hsm.data.canvas_elem_type
        new = cls(x, y, width, height)
        if hsm.data.canvas_temp_elem:
            mock_change = Modify(hsm.data.canvas_temp_elem, new)
        else:
            mock_change = Insert(new)
        hsm.data.canvas_temp_elem = new
        draw_changes([mock_change], view)

    trans = {
        'top': {
            Initial: T('idle'),
            Tool_Changed: Internal(action=remember_tool),
            Model_Changed: Internal(action=lambda e, h: draw_changes(e.data,
                                                                     view)),
        },
        'idle': {
            Canvas_Down: T('drawing_rectangle'),
        },
        'drawing': {
            Initial: T('drawing_ellipse'),
            Canvas_Up: T('idle', action=commit_to_model),
        },
        'drawing_rectangle': {
            Canvas_Move: Internal(action=mock_model_changes),
        },
        'drawing_ellipse': {
            Canvas_Move: Internal(action=mock_model_changes),
        },
    }

    return (view, states, trans)

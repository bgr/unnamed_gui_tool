from javax.swing import JPanel
from java.awt import Color
from hsmpy import Initial
from hsmpy import Transition as T
from hsmpy import InternalTransition as Internal

from model import Rectangle, Ellipse
from app import S
from events import (Mouse_Down, Mouse_Up, Mouse_Move, Tool_Changed,
                    Commit_To_Model, Model_Changed)
from model import Modify, Insert, Remove


import logging
_log = logging.getLogger(__name__)


class CanvasView(JPanel):

    def __init__(self, width, height, drawing_handlers):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self._elems = []
        self._draw_once_elems = []
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

    def draw_once(self, elems):
        self._draw_once_elems = elems
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
        for el in self._elems + self._draw_once_elems:
            self.drawing_handlers[el.__class__](el, g)



# top state

def set_up(evt, hsm):
    hsm.data.canvas_tool = Rectangle
    _log.info("HSM tool set to {0}".format(hsm.data.canvas_tool))


def remember_tool(evt, hsm):
    tool_map = {
        'rectangle': Rectangle,
        'ellipse': Ellipse,
    }
    hsm.data.canvas_tool = tool_map[evt.data]
    _log.info('HSM remembered selected tool {0}'.format(hsm.data.canvas_tool))


# idle

def reset_temp_elem(evt, hsm):
    hsm.data.canvas_elem_type = None
    hsm.data.canvas_temp_elem = None


# guard for selected tool
# TODO: won't suffice, requires conditional transition support

def tool_is(element):
    return lambda _, hsm: hsm.data.canvas_tool == element


# drawin/

def prepare_for_drawing(evt, hsm):
    hsm.data.canvas_start_x = evt.x
    hsm.data.canvas_start_y = evt.y
    if hsm.data.canvas_tool not in [Ellipse, Rectangle]:
        raise ValueError("Invalid tool "
                         "selected {0}".format(hsm.data.canvas_tool))
    # remember elem type since tool could change during drawing
    hsm.data.canvas_elem_type = hsm.data.canvas_tool


# drawing - interaction with CanvasView

def draw_rectangle(el, g):
    g.drawRect(*map(int, el))


def draw_ellipse(el, g):
    g.drawOval(*map(int, el))


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


def draw_temp_elem(evt, hsm, view):
    x = hsm.data.canvas_start_x
    y = hsm.data.canvas_start_y
    width = evt.x - x
    height = evt.y - y

    cls = hsm.data.canvas_elem_type
    hsm.data.canvas_temp_elem = cls(x, y, width, height)
    view.draw_once([hsm.data.canvas_temp_elem])


# interaction with model

def commit_to_model(evt, hsm):
    el = hsm.data.canvas_temp_elem
    if el.width == 0 and el.height == 0:
        _log.info("not commiting {0} (0 dimensions)".format(el))
        return
    _log.info("committing to model {0}".format(el))
    # dispatch event to add to model
    hsm.eb.dispatch(Commit_To_Model( [Insert(el)] ))



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
            'drawing': S(on_enter=prepare_for_drawing, states={
                'wait_for_drag_element': S(),
                'dragging_element': S(),
            }),
        })
    }

    act_draw_changes = lambda evt, hsm: draw_changes(evt.data, view)
    act_draw_temp_elem = lambda evt, hsm: draw_temp_elem(evt, hsm, view)

    trans = {
        'top': {
            Initial: T('idle'),
            Tool_Changed: Internal(action=remember_tool),
            Model_Changed: Internal(action=act_draw_changes),
        },
        'idle': {
            Canvas_Down: T('drawing'),
        },
        'drawing': {
            Initial: T('wait_for_drag_element'),
        },
            'wait_for_drag_element': {
                Canvas_Move: T('dragging_element', action=act_draw_temp_elem),
                Canvas_Up: T('idle'),  # don't commit 0 width & height
            },
            'dragging_element': {
                Canvas_Move: Internal(action=act_draw_temp_elem),
                Canvas_Up: T('idle', action=commit_to_model),
            },
    }

    return (view, states, trans)

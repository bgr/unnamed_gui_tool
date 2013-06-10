from javax.swing import JPanel
from java.awt import Color
from model import Rectangle, Circle, Add_element, Element_added
from statemachine import StateMachine, State
from statemachine import Transition as T
import logging


_log = logging.getLogger(__name__)


class Idle(State):
    def __init__(self, eventbus):
        self.eb = eventbus
        self._interests = {
            'mouse_down': self.on_mouse_down,
        }

    def enter(self):
        _log.debug('entered Idle')

    def exit(self):
        _log.debug('exiting Idle')

    def on_mouse_down(self, evt, aux):
        _log.debug('Idle mouse down')
        _log.debug(evt)
        # switch state
        self.eb.dispatch('draw_rectangle')


class Drawing_Rectangle(State):
    def __init__(self):
        self._interests = {
            'mouse_down': self.on_mouse_down,
            'mouse_up': self.on_mouse_up,
        }

    def enter(self):
        _log.debug('entered Drawing_Rectangle')

    def exit(self):
        _log.debug('exiting Drawing_Rectangle')

    def on_mouse_down(self, evt, aux):
        _log.debug('Drawing_Rectangle mouse down')
        _log.debug(evt)

    def on_mouse_up(self, evt, aux):
        _log.debug('Drawing_Rectangle mouse up')
        _log.debug(evt)


class Drawing_Circle(State):
    def __init__(self):
        self._interests = {
            'mouse_down': self.on_mouse_down,
            'mouse_up': self.on_mouse_up,
            'mouse_move': self.on_mouse_move,
        }

    def enter(self):
        _log.debug('entered Drawing_Circle')

    def exit(self):
        _log.debug('exiting Drawing_Circle')

    def on_mouse_down(self, evt, aux):
        _log.debug('Drawing_Circle mouse down')
        _log.debug(evt)

    def on_mouse_up(self, evt, aux):
        _log.debug('Drawing_Circle mouse up')
        _log.debug(evt)

    def on_mouse_move(self, evt, aux):
        _log.debug('Drawing_Circle mouse move')
        _log.debug(evt)


class CanvasView(JPanel):

    def __init__(self, width, height, eb):
        super(CanvasView, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self.mousePressed = lambda e: eb.dispatch('mouse_down', (e.x, e.y))
        self.mouseReleased = lambda e: eb.dispatch('mouse_up', (e.x, e.y))
        self.mouseMoved = lambda e: eb.dispatch('mouse_move', (e.x, e.y))

        idle = Idle(eb)
        drawing_rectangle = Drawing_Rectangle()
        drawing_circle = Drawing_Circle()

        transition_map = {
            idle: [
                T('draw_rectangle', drawing_rectangle,
                  self._on_drawing_rectangle_trans),
                T('draw_circle', drawing_circle,
                  self._on_drawing_circle_trans), ],
            drawing_rectangle: [
                T('commit', idle, self._on_commit),
                T('cancel', idle, self._on_cancel), ],
            drawing_circle: [
                T('commit', idle, self._on_commit),
                T('cancel', idle, self._on_cancel), ],
        }

        self.fsm = StateMachine(transition_map, idle, eb)
        self.fsm.start()

    def _on_drawing_rectangle_trans(self):
        _log.debug('transition to drawing_rectangle')

    def _on_drawing_circle_trans(self):
        _log.debug('transition to drawing_circle')

    def _on_commit(self, evt, aux=None):
        _log.debug('commit')

    def _on_cancel(self, evt, aux=None):
        _log.debug('cancel')

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

    def set_circle_tool(self):
        _log.debug('Set circle tool')
        self.tool = Circle

    def set_rectangle_tool(self):
        _log.debug('Set rectangle tool')
        self.tool = Rectangle

    def paintComponent(self, g):
        g.setColor(Color(255, 255, 255))
        g.fillRect(0, 0, self.preferredSize.width, self.preferredSize.height)

        g.setColor(Color(25, 25, 25))
        #for el in self.elems:
            #self.draw_handlers[el.__class__](g, el)

    def draw_circle(self, g, el):
        g.drawOval(el.x, el.y, el.radius, el.radius)

    def draw_rectangle(self, g, el):
        g.drawRect(el.x, el.y, el.width, el.height)

    def add_circle(self, g, el):
        g.drawOval(el.x, el.y, el.radius, el.radius)

    def add_rectangle(self, g, el):
        g.drawRect(el.x, el.y, el.width, el.height)


class CanvasController():
    def __init__(self, canvas, model, eventbus):
        self.view = canvas
        self.model = model
        self.eb = eventbus
        canvas.elems = model.elems
        eventbus.register(Element_added, self.on_added)

    def on_added(self, elem):
        self.view.add(elem)

    def add_new(self, elem):
        "Re-dispatches to eventbus when view dispatches newly added element"
        self.eb.dispatch(Add_element, elem)

    def set_circle_tool(self, _):
        self.view.set_circle_tool()

    def set_rectangle_tool(self, _):
        self.view.set_rectangle_tool()

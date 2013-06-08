from javax.swing import JPanel
from java.awt import Color
from model import Rectangle, Circle, Add_element, Element_added


class CanvasView(JPanel):

    def __init__(self, width, height):
        super(CanvasView, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self.draw_handlers = {
            Circle: self.draw_circle,
            Rectangle: self.draw_rectangle,
        }

        self.tool_handlers = {
            Circle: self.add_circle,
            Rectangle: self.add_rectangle,
        }

        self.tool = Circle

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
        print 'Set circle tool'
        self.tool = 'circle'

    def set_rect_tool(self):
        print 'Set rect tool'
        self.tool = 'rect'

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


class CanvasController():
    def __init__(self, canvas, model, eventbus):
        self.view = canvas
        self.model = model
        self.eb = eventbus
        canvas.elems = model.elems
        canvas.mousePressed = self.add_new
        eventbus.register(Element_added, self.on_added)

    def on_added(self, elem):
        self.view.add(elem)

    def add_new(self, elem):
        "Re-dispatches to eventbus when view dispatches newly added element"
        self.eb.dispatch(Add_element, elem)

    def set_circle_tool(self, _):
        self.view.set_circle_tool()

    def set_rect_tool(self, _):
        self.view.set_rect_tool()

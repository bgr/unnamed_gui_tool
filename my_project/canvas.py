from javax.swing import JPanel, JFrame, JButton, BoxLayout
from java.awt import Color

from util import invokeLater

from model import (PaintingModel, Rectangle, Circle, Add_element,
                   Element_Added)
from eventbus import EventBus


class Canvas(JPanel):

    def __init__(self, width, height):
        super(Canvas, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self.elems = []

    def set_elems(self, elems):
        self.elems = elems
        self.repaint()

    def paintComponent(self, g):
        g.setColor(Color(120, 50, 10))
        g.fillRect(0, 0, self.preferredSize.width, self.preferredSize.height)


class CanvasController():
    def __init__(self, canvas, model, eventbus):
        self.canvas = canvas
        self.model = model
        self.eb = eventbus
        canvas.mousePressed = self.add_new
        eventbus.register(Element_Added, self.on_added)

    def on_added(self, elem):
        print 'Controller saw added {0}'.format(elem)

    def add_new(self, e):
        self.eb.dispatch(Add_element, Circle(e.x, e.y, 20))


class App(JFrame):
    def __init__(self):
        super(App, self).__init__()
        self.setup_gui()
        self.wire_up()

    def setup_gui(self):
        self.title = "Colors"
        self.layout = BoxLayout(self.contentPane, BoxLayout.PAGE_AXIS)
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        self.size = (500, 400)
        self.locationRelativeTo = None
        self.visible = True

        def pack_frame(e):
            self.pack()

        self.button = JButton('Pack', actionPerformed=pack_frame)
        self.c_1 = Canvas(200, 100)
        self.c_2 = Canvas(300, 200)
        self.add(self.c_1)
        self.add(self.c_2)
        self.add(self.button)

    def wire_up(self):
        eb = EventBus()
        model = PaintingModel(eb)
        model.elems = [Circle(20, 30, 40), Rectangle(30, 40, 10, 20)]

        CanvasController(self.c_1, model, eb)
        CanvasController(self.c_2, model, eb)

        eb.register(Add_element, model.add)



@invokeLater
def run_app():
    App()

if __name__ == '__main__':
    #invokeLater(lambda: App())()
    run_app()

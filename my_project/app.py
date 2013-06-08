from javax.swing import JFrame, JButton, BoxLayout
from util import invokeLater
from model import PaintingModel, Rectangle, Circle, Add_element
from eventbus import EventBus
from canvas import CanvasView, CanvasController


class PaintFrame(JFrame):
    def __init__(self, model, eventbus):
        super(PaintFrame, self).__init__()
        self.title = "Colors"
        self.layout = BoxLayout(self.contentPane, BoxLayout.PAGE_AXIS)
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        self.size = (500, 400)
        self.visible = True

        canvas = CanvasView(300, 200)
        canvas_ctrl = CanvasController(canvas, model, eventbus)

        btn_circle = JButton('Circle',
                             actionPerformed=canvas_ctrl.set_circle_tool)
        btn_rect = JButton('Rectangle',
                           actionPerformed=canvas_ctrl.set_rect_tool)
        self.add(canvas)
        self.add(btn_circle)
        self.add(btn_rect)
        eventbus.register(Add_element, model.add)


@invokeLater
def run_app():
    eb = EventBus()
    model = PaintingModel(eb)
    model.elems = [Circle(20, 30, 40), Rectangle(30, 40, 10, 20)]
    PaintFrame(model, eb).locationRelativeTo = None
    PaintFrame(model, eb)


if __name__ == '__main__':
    run_app()

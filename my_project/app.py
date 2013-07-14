from javax.swing import JFrame, JButton, BoxLayout
from util import invokeLater
import canvas
from model import PaintingModel, Rectangle, Circle
from hsmpy import HSM, EventBus
from events import Commit_To_Model


class PaintFrame(JFrame):
    def __init__(self, model, eventbus):
        super(PaintFrame, self).__init__()
        self.title = "Colors"
        self.layout = BoxLayout(self.contentPane, BoxLayout.PAGE_AXIS)
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        self.size = (500, 400)
        self.visible = True

        canvas_view, canvas_states, canvas_trans = canvas.make(eventbus)

        canvas_hsm = HSM(canvas_states, canvas_trans)
        canvas_hsm.start(eventbus)

        #btn_circle = JButton('Circle',
        # actionPerformed=canvas_ctrl.set_circle_tool)
        #btn_rect = JButton('Rectangle',
                           #actionPerformed=canvas_ctrl.set_rectangle_tool)
        self.add(canvas_view)
        #self.add(btn_circle)
        #self.add(btn_rect)


@invokeLater
def run():
    eventbus = EventBus()
    model = PaintingModel(eventbus)
    model.elems = [Circle(20, 30, 40), Rectangle(30, 40, 10, 20)]
    PaintFrame(model, eventbus).locationRelativeTo = None
    PaintFrame(model, eventbus)

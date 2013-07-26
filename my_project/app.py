from java.awt import Color
from javax.swing import JFrame, JButton, BoxLayout
from javautils import invokeLater
import canvas
from model import CanvasModel, Rectangle, Ellipse
from events import Tool_Changed
from hsmpy import HSM, EventBus, State, Initial
from hsmpy import Transition as T
import logging


logging.basicConfig(level=logging.INFO)


class LoggingState(State):
    def enter(self, evt, hsm):
        logging.getLogger('HSM.{0}'.format(self.name)).info('entering')

    def exit(self, evt, hsm):
        logging.getLogger('HSM.{0}'.format(self.name)).info('exiting')

# alias class so that it can easily be switched
S = LoggingState



class AppFrame(JFrame):
    def __init__(self, eventbus):
        super(self.__class__, self).__init__()
        self.title = "Canvases"
        self.layout = BoxLayout(self.contentPane, BoxLayout.PAGE_AXIS)
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        self.visible = True

        btn_ellipse = JButton('Ellipse',
                              actionPerformed=lambda evt:
                              eventbus.dispatch(Tool_Changed('ellipse')))
        btn_rectangle = JButton('Rectangle',
                                actionPerformed=lambda evt:
                                eventbus.dispatch(Tool_Changed('rectangle')))
        self.add(btn_ellipse)
        self.add(btn_rectangle)


@invokeLater
def run():
    eventbus = EventBus()
    model = CanvasModel(eventbus)
    model.elems = [Ellipse(20, 30, 40, 50), Rectangle(30, 40, 10, 20)]

    canvas_view_1, canvas_states_1, canvas_trans_1 = canvas.make(eventbus)
    canvas_view_2, canvas_states_2, canvas_trans_2 = canvas.make(eventbus)

    app_states = {
        'top': {
            'canvas_displayed': State([
                (canvas_states_1, canvas_trans_1),
                (canvas_states_2, canvas_trans_2),
                #(toolbar_states, toolbar_trans),
            ]),
        }
    }

    app_trans = {
        'top': {
            Initial: T('canvas_displayed'),
        }
    }

    hsm = HSM(app_states, app_trans)
    hsm.start(eventbus)

    app_frame = AppFrame(eventbus)
    app_frame.add(canvas_view_1)
    app_frame.add(canvas_view_2)
    canvas_view_2.background_color = Color.GRAY
    app_frame.size = (500, 700)


if __name__ == "__main__":
    run()

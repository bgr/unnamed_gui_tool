from java.awt import Color, BorderLayout
from javax.swing import JFrame, JPanel, BoxLayout
from javautils import invokeLater
import widgets
from model import CanvasModel, Rectangle, Ellipse
from hsmpy import HSM, EventBus, State, Initial, T
import logging


"""
Code is still in very experimental shape since it's serving as a playground for
testing hsmpy features. Once hsmpy is feature-ready I'll try to put this
project in a good shape.
"""

logging.basicConfig(level=logging.INFO)


class LoggingState(State):
    def enter(self, hsm):
        logging.getLogger('HSM.{0}'.format(self.name)).info('entering')

    def exit(self, hsm):
        logging.getLogger('HSM.{0}'.format(self.name)).info('exiting')

# alias class so that it can easily be switched
S = LoggingState



class AppFrame(JFrame):
    def __init__(self, eventbus):
        super(self.__class__, self).__init__()
        self.title = "Canvases"
        # will use BorderLayout by default
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        self.visible = True

        toolbar, _, _ = widgets.tool_picker.make(eventbus)
        self.add(toolbar, BorderLayout.NORTH)



@invokeLater
def run():
    eventbus = EventBus()
    canvas_model = CanvasModel(eventbus)
    canvas_model.elems = [Ellipse(20, 30, 40, 50), Rectangle(30, 40, 10, 20)]

    cvs_view_1, cvs_states_1, cvs_trans_1 = widgets.canvas.make(eventbus,
                                                                canvas_model)
    cvs_view_2, cvs_states_2, cvs_trans_2 = widgets.canvas.make(eventbus,
                                                                canvas_model)

    app_states = {
        'top': {
            'canvas_displayed': State([
                (cvs_states_1, cvs_trans_1),
                (cvs_states_2, cvs_trans_2),
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

    canvases = JPanel()
    canvases.layout = BoxLayout(canvases, BoxLayout.PAGE_AXIS)

    canvases.add(cvs_view_1)
    canvases.add(cvs_view_2)
    app_frame.add(canvases, BorderLayout.CENTER)

    cvs_view_2.background = Color.GRAY

    app_frame.size = (1100, 1000)


if __name__ == "__main__":
    run()

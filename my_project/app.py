from java.awt import Color
from javax.swing import JFrame, JButton, BoxLayout
from javautils import invokeLater
import widgets.canvas
from model import CanvasModel, Rectangle, Ellipse
from events import Tool_Changed
from hsmpy import HSM, EventBus, State, Initial
from hsmpy import Transition as T
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
        self.layout = BoxLayout(self.contentPane, BoxLayout.PAGE_AXIS)
        self.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        self.visible = True

        def btn(tool_name):
            return JButton(tool_name, actionPerformed=lambda evt:
                           eventbus.dispatch(Tool_Changed(tool_name)))

        self.add(btn('combo'))
        self.add(btn('path'))


@invokeLater
def run():
    eventbus = EventBus()
    model = CanvasModel(eventbus)
    model.elems = [Ellipse(20, 30, 40, 50), Rectangle(30, 40, 10, 20)]

    cvs_view_1, cvs_states_1, cvs_trans_1 = widgets.canvas.make(eventbus)
    cvs_view_2, cvs_states_2, cvs_trans_2 = widgets.canvas.make(eventbus)

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
    app_frame.add(cvs_view_1)
    app_frame.add(cvs_view_2)
    cvs_view_2.background_color = Color.GRAY
    app_frame.size = (500, 700)


if __name__ == "__main__":
    run()

import logging
_log = logging.getLogger(__name__)

from javax.swing import SwingUtilities

from hsmpy import Initial, T, Choice, Internal

from ...app import S
from ... import model
from ...util import fseq
from ...events import Commit_To_Model



def make(eb, view, Canvas_Down, Canvas_Up, Canvas_Move, Tool_Done):

    idle = {
        'ellipse_idle': S(),
    }

    engaged = {
        'ellipse_engaged': S(),
    }

    temp_elem_data = None


    def remember_start_coords(evt, _):
        global temp_elem_data
        temp_elem_data = model.Ellipse(evt.x, evt.y, 0, 0)

    def update_ellipse(evt, _):
        global temp_elem_data
        x, y = temp_elem_data.x, temp_elem_data.y
        temp_elem_data = model.Ellipse(x, y, evt.x - x, evt.y - y)

    def redraw_ellipse(*_, **__):
        global temp_elem_data
        view.draw_once([temp_elem_data])
        view.repaint()

    def commit_and_finish(evt, _):
        global temp_elem_data
        assert temp_elem_data is not None
        _log.info('about to commit ellipse {0}'.format(temp_elem_data))
        eb.dispatch(Commit_To_Model( [model.Insert(temp_elem_data)] ))
        eb.dispatch(Tool_Done())
        temp_elem_data = None


    trans = {
        'ellipse_idle': {
            Canvas_Down: T('ellipse_engaged', remember_start_coords),
        },
        'ellipse_engaged': {
            Canvas_Move: Internal(fseq(
                update_ellipse,
                redraw_ellipse)),
            Canvas_Up: Internal(commit_and_finish),
        }
    }

    return (idle, engaged, trans)

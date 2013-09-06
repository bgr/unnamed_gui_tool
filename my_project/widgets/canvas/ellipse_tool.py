import logging
_log = logging.getLogger(__name__)

from hsmpy import Initial, T, Internal

from ...app import S
from ... import model
from ...util import fseq



def make(eb, view, event_pack, model_commit):
    (Canvas_Down, Canvas_Up, Canvas_Right_Down, Canvas_Right_Up,
     Canvas_Middle_Down, Canvas_Middle_Up, Canvas_Move, Canvas_Wheel,
     Tool_Done) = event_pack

    idle = {
        'ellipse_idle': S(),
    }

    engaged = {
        'ellipse_engaged': S({
            'ellipse_wait_for_drag': S(),
            'ellipse_dragging': S(),
        }),
    }

    temp_elem_data = []

    def remember_start_coords(evt, _):
        temp_elem_data[:] = [evt.x, evt.y]

    def update_dimensions(evt, _):
        x, y = view.transformed(*temp_elem_data)
        x2, y2 = view.transformed(evt.x, evt.y)
        view.draw_once = [model.Ellipse(x, y, x2 - x, y2 - y)]

    def redraw_view(*_):
        view.repaint()

    def commit_to_model(evt, _):
        x, y = view.transformed(*temp_elem_data)
        x2, y2 = view.transformed(evt.x, evt.y)
        w, h = x2 - x, y2 - y
        if (w, h) == (0, 0):
            _log.info('not committing ellipse, 0 dimensions')
        else:
            el = model.Ellipse(x, y, w, h)
            _log.info('about to commit ellipse {0}'.format(el))
            model_commit([model.Insert(el)])
        temp_elem_data[:] = []

    def dispatch_Tool_Done(*_):
        eb.dispatch(Tool_Done())


    trans = {
        'ellipse_idle': {
            Canvas_Down: T('ellipse_wait_for_drag', remember_start_coords),
        },
        'ellipse_engaged': {
            Initial: T('ellipse_wait_for_drag'),
        },
        'ellipse_wait_for_drag': {
            Canvas_Move: T('ellipse_dragging'),
            Canvas_Up: Internal(dispatch_Tool_Done),
        },
        'ellipse_dragging': {
            Canvas_Move: Internal(fseq(
                update_dimensions,
                redraw_view)),
            Canvas_Up: Internal(fseq(
                commit_to_model,
                dispatch_Tool_Done,
                redraw_view)),
        }
    }

    return (idle, engaged, trans)

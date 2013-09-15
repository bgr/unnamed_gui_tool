import logging
_log = logging.getLogger(__name__)

from hsmpy import Initial, T, Internal

from ...app import S
from ... import model
from ...util import fseq, Dummy
from elements import EllipseCE



def make(eb, view, event_pack, elem_map, canvas_model):
    (Canvas_Down, Canvas_Up, Canvas_Right_Down, Canvas_Right_Up,
     Canvas_Middle_Down, Canvas_Middle_Up, Canvas_Move, Canvas_Wheel,
     Tool_Done) = event_pack

    data = Dummy(start_x=None,
                 start_y=None,
                 preview=None)

    def remember_start_coords(evt, _):
        data.start_x, data.start_y = evt.x, evt.y

    def update_preview(evt, _):
        x, y = view.transformed(data.start_x, data.start_y)
        x2, y2 = view.transformed(evt.x, evt.y)
        ellipse = model.Ellipse(x, y, x2 - x, y2 - y)
        if data.preview:
            data.preview.elem = ellipse
        else:
            data.preview = EllipseCE(ellipse, view)
            view.add(data.preview)

    def remove_preview(*_):
        view.remove(data.preview) if data.preview else ''
        data.preview = None

    def redraw_view(*_):
        view.repaint()

    def commit_to_model(evt, _):
        x, y = view.transformed(data.start_x, data.start_y)
        x2, y2 = view.transformed(evt.x, evt.y)
        w, h = x2 - x, y2 - y
        if (w, h) == (0, 0):
            _log.info('not committing ellipse, 0 dimensions')
        else:
            el = model.Ellipse(x, y, w, h)
            _log.info('about to commit ellipse {0}'.format(el))
            canvas_model.commit([model.Insert(el)])

    def signalize_finished(*_):
        eb.dispatch(Tool_Done())

    def clean_up(*_):
        remove_preview()
        data.reset()


    idle = {
        'ellipse_idle': S(),
    }

    engaged = {
        'ellipse_engaged': S(on_exit=clean_up, states={
            'ellipse_wait_for_drag': S(),
            'ellipse_dragging': S(),
        }),
    }


    trans = {
        'ellipse_idle': {
            Canvas_Down: T('ellipse_wait_for_drag', remember_start_coords),
        },
        'ellipse_engaged': {
            Initial: T('ellipse_wait_for_drag'),
        },
        'ellipse_wait_for_drag': {
            Canvas_Move: T('ellipse_dragging'),
            Canvas_Up: Internal(signalize_finished),
        },
        'ellipse_dragging': {
            Canvas_Move: Internal(fseq(
                update_preview,
                redraw_view)),
            Canvas_Up: Internal(fseq(
                remove_preview,
                commit_to_model,
                signalize_finished)),
        }
    }

    return (idle, engaged, trans)

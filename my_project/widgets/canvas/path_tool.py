import logging
_log = logging.getLogger(__name__)

from hsmpy import T, Internal

from ...app import S
from ... import model
from ...util import fseq, Dummy
from elements import PathCE



def make(eb, view, event_pack, elem_map, canvas_model):
    """
        Returns separate states dicts and trans dict for idle and engaged tool
        behaviors as a tuple:
            (idle_state_dict, engaged_state_dict, transitions_dict)
        so that they can be integrated within parent states by simple dict
        joining, performed in widgets.canvas.main.make function.
    """

    (Canvas_Down, Canvas_Up, Canvas_Right_Down, Canvas_Right_Up,
     Canvas_Middle_Down, Canvas_Middle_Up, Canvas_Move, Canvas_Wheel,
     Tool_Done) = event_pack

    data = Dummy(vertices=(),
                 preview=None)


    def add_vertex(evt, hsm):
        new = view.transformed(evt.x, evt.y)
        data.vertices = data.vertices + (new,)
        _log.info('added vertex {0}, all: {1}'.format(data.vertices[-1],
                                                      data.vertices))
        # TODO: make sure that no two successive vertices have same coords

    def move_last_vertex(evt, _):
        new = view.transformed(evt.x, evt.y)
        data.vertices = data.vertices[:-1] + (new,)

    def update_preview(*_):
        path = model.Path(data.vertices)
        if data.preview:
            data.preview.elem = path
        else:
            data.preview = PathCE(path, view)
            view.add(data.preview)

    def redraw_view(*_):
        view.repaint()

    def commit_to_model(*_):
        path = model.Path(data.vertices)
        _log.info('about to commit path {0}'.format(path))
        canvas_model.commit([model.Insert(path)])

    def signalize_finished(*_):
        eb.dispatch(Tool_Done())

    def clean_up(*_):
        view.remove(data.preview) if data.preview else ''
        data.reset()


    idle = {
        'path_idle': S(),
    }

    engaged = {
        'path_engaged': S(on_exit=clean_up),
    }

    trans = {
        'path_idle': {
            Canvas_Down: T('path_engaged',   # add 2 vertices to make a segment
                           action=fseq(add_vertex, add_vertex)),
        },
        'path_engaged': {
            Canvas_Move: Internal(fseq(
                move_last_vertex,
                update_preview,
                redraw_view)),
            Canvas_Down: Internal(add_vertex),
            Canvas_Right_Down: Internal(fseq(
                add_vertex,
                commit_to_model,
                signalize_finished))
        },
    }

    return (idle, engaged, trans)

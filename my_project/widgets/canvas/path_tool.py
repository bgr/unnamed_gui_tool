import logging
_log = logging.getLogger(__name__)

from hsmpy import Initial, T, Internal

from ...app import S
from ... import model
from ...util import fseq



def make(eb, view, event_pack, canvas_model):
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

    # temporary holder objects used while the path is still being drawn
    vertices = []

    def add_vertex(evt, hsm):
        vertices.append( view.transformed(evt.x, evt.y) )
        _log.info('added vertex {0}, all: {1}'.format(vertices[-1], vertices))
        # TODO: make sure that no two successive vertices have same coords

    def update_last_segment(evt, hsm):
        vertices[-1] = view.transformed(evt.x, evt.y)

    def commit_and_finish(hsm):
        # work around "TypeError: unhashable type list" that arrises in
        # util.duplicates when model.parse checks for duplicate elements since
        # vertices list is unhashable and also makes model safer since tuple
        # is immutable
        path = model.Path(tuple(vertices))
        _log.info('about to commit path {0}'.format(path))
        canvas_model.commit([model.Insert(path)])
        eb.dispatch(Tool_Done())
        vertices[:] = []  # clear

    def redraw_path(evt, hsm):
        path = model.Path(tuple(vertices))
        view.draw_once = [path]
        view.repaint()


    idle = {
        'path_idle': S(),
    }

    engaged = {
        'path_engaged': S({
            'path_drawing': S(),
            'path_finished': S(on_enter=commit_and_finish),
        }),
    }

    trans = {
        'path_idle': {
            Canvas_Down: T('path_drawing',   # add 2 vertices to make a segment
                           action=fseq(add_vertex, add_vertex)),
        },
        'path_engaged': {
            Initial: T('path_drawing'),
        },
        'path_drawing': {
            Canvas_Move: Internal(fseq( update_last_segment, redraw_path )),
            Canvas_Down: T('path_drawing', add_vertex),
            Canvas_Right_Down: T('path_finished', add_vertex),
        },
    }

    return (idle, engaged, trans)

import logging
_log = logging.getLogger(__name__)

from javax.swing import SwingUtilities

from hsmpy import Initial, T, Choice, Internal

from ...app import S
from ... import model
from ...util import fseq
from ...events import Commit_To_Model



def make(eventbus, view, Canvas_Down, Canvas_Up, Canvas_Move, Tool_Done):

    # temporary holder objects used while the shape is still being drawn
    vertices = []

    def add_vertex(evt, hsm):
        vertices.append( (evt.x, evt.y) )
        _log.info('added vertex {0}, all: {1}'.format(vertices[-1], vertices))
        # TODO: make sure that no two successive vertices have same coords

    def update_last_segment(evt, hsm):
        vertices[-1] = (evt.x, evt.y)

    def commit_and_finish(evt, hsm):
        # work around "TypeError: unhashable type list" that arrises in
        # util.duplicates when model.parse checks for duplicate elements since
        # vertices list is unhashable and also makes model safer since tuple
        # is immutable
        path = model.Path(tuple(vertices))
        _log.info('about to commit path {0}'.format(path))
        eventbus.dispatch(Commit_To_Model( [model.Insert(path)] ))
        eventbus.dispatch(Tool_Done())
        vertices[:] = []  # clear

    def redraw_path(evt, hsm):
        path = model.Path(tuple(vertices))
        view.draw_once([path])


    states = {
        'top': S({
            'path_tool': S({
                'path_hovering': S(),
                'path_drawing': S(on_enter=add_vertex),
                'path_finished': S(on_enter=commit_and_finish),
            }),
        })
    }

    trans = {
        'top': {
            Initial: T('path_tool'),
        },
        'path_tool': {
            Initial: T('path_hovering'),
        },
        'path_hovering': {
            Canvas_Down: T('path_drawing', action=add_vertex),
        },
        'path_drawing': {
            Canvas_Move: Internal(action=fseq(
                update_last_segment,
                redraw_path)),
            Canvas_Down: Choice({
                False: 'path_drawing',
                True: 'path_finished' },
                key=lambda e, _: SwingUtilities.isRightMouseButton(e.orig)),
        },
    }

    return (states, trans)

import logging
_log = logging.getLogger(__name__)

from javax.swing import SwingUtilities

from hsmpy import Initial, T, Choice, Internal

from ...app import S
from ... import model





def bounding_box_around_points(point_list):
    def expand_box(current_box, new_point):
        min_x, min_y, max_x, max_y = current_box
        x, y = new_point
        return (min(min_x, x), min(min_y, y), max(max_x, x), max(max_y, y))
    neg_inf = float("-inf")
    pos_inf = float("inf")
    return reduce(expand_box, point_list, (pos_inf, pos_inf, neg_inf, neg_inf))



def make(eventbus, view, Canvas_Down, Canvas_Up, Canvas_Move, Tool_Done):

    path_elements = []

    def add_segment(evt, hsm):
        _log.info('add segment')
        _log.info(evt)

    def update_segment_preview(evt, hsm):
        _log.info('update segment preview')
        _log.info(evt)

    def commit_and_finish(evt, hsm):
        _log.info(path_elements)
        _log.info('done')

    def draw_path(evt, hsm):
        verts = [(0, 0), (20, 0), (20, 20), (30, 30)]
        bounds = bounding_box_around_points(verts)
        x1, y1, x2, y2 = bounds
        elem = model.Path(x1 + evt.x, y1 + evt.y, x2 - x1, y2 - y1, verts)
        view.draw_once([elem])


    states = {
        'top': S({
            'path_tool': S({
                'path_hovering': S(),  # wait for mouse down
                #'path_wait_for_move': S(on_enter=add_segment),
                #'path_drawing_next_segment': S(),
                #'path_finished': S(on_enter=commit_and_finish),
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
            #Canvas_Down: T('path_wait_for_move'),
            Canvas_Down: Internal(draw_path),
        },
        #'path_wait_for_move': {
            #Canvas_Move: T('path_drawing_next_segment',
                           #action=update_segment_preview),
        #},
        #'path_drawing_next_segment': {
            #Canvas_Move: Internal(action=update_segment_preview),
            #Canvas_Down: Choice({
                #False: 'path_wait_for_move',
                #True: 'path_finished' },
                #key=lambda e, _: SwingUtilities.isRightMouseButton(e)),
        #},
    }

    return (states, trans)

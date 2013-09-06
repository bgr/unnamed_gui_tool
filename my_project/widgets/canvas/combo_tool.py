import logging
_log = logging.getLogger(__name__)

from hsmpy import Initial, T, Choice, Internal

from ...app import S
from ... import model
from ...util import fseq



def make(eb, view, event_pack, model_commit):
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


    idle = {
        'combo_idle': S({
            'combo_over_background': S(),
            'combo_over_selected_element': S(),
            'combo_over_unselected_element': S(),
        }),
    }

    engaged = {
        'combo_engaged': S({
            'combo_dragging_marquee': S(),
            'combo_wait_for_drag_selection': S(),
            'combo_dragging_selection': S(),
        }),
    }


    mouse_coords = []

    def remember_mouse_coords(evt, _):
        mouse_coords[:] = [evt.x, evt.y]

    def elem_at(x, y):
        elems = view.elements_at(x, y)
        # sort so that already selected elements are at the beginning of list
        # that's useful when trying to click already selected element which
        # happens to be under unselected elem
        elems = sorted(elems, key=lambda el: 0 if el in view.selection else 1)
        return next(iter(elems), None)

    def whats_at_mouse_coords(*_):
        if not mouse_coords:
            return 'bg'
        el = elem_at(*mouse_coords)
        if el is None:
            return 'bg'
        elif el in view.selection:
            return 'sel'
        else:
            return 'unsel'

    def select_elem_under_cursor(evt, hsm):
        view.selection = [elem_at(evt.x, evt.y)]

    def deselect_all(*_):
        view.selection = []

    def set_marquee(evt, _):
        x, y = mouse_coords
        view.marquee = (x, y, evt.x, evt.y)

    def clear_marquee(*_):
        view.marquee = None

    def redraw_view(*_):
        view.repaint()

    def simulate_fake_move(evt, hsm):
        x, y = mouse_coords
        dx, dy = evt.x - x, evt.y - y
        moved = [el.move(dx / view.zoom, dy / view.zoom)
                 for el in view.selection]
        view.draw_once = moved

    def commit_real_move(evt, hsm):
        x, y = mouse_coords
        dx, dy = evt.x - x, evt.y - y
        if (dx, dy) == (0, 0):
            _log.info('nothing to commit, moved by 0 px')
            return
        changes = [model.Modify(el, el.move(dx / view.zoom, dy / view.zoom))
                   for el in view.selection]
        model_commit(changes)

    def select_overlapped_elements(evt, hsm):
        assert view.marquee is not None
        elems = view.elements_overlapping(*view.marquee)
        _log.info('marquee overlapped {0} elements'.format(len(elems)))
        view.selection = elems

    def dispatch_Tool_Done(*_):
        eb.dispatch(Tool_Done())


    trans = {
        'combo_idle': {
            Initial: Choice({
                'bg': 'combo_over_background',
                'sel': 'combo_over_selected_element',
                'unsel': 'combo_over_unselected_element',
            }, key=whats_at_mouse_coords, default='combo_over_background'),

            Canvas_Move: T('combo_idle', remember_mouse_coords),
        },
        'combo_engaged': {
            # never called, should always transition directly to substates
            Initial: T('combo_dragging_marquee', action=lambda _, __: 1 / 0),
        },

        'combo_over_background': {
            Canvas_Down: T('combo_dragging_marquee', fseq(
                deselect_all,
                remember_mouse_coords,
                set_marquee,
                redraw_view)),
        },
        'combo_over_unselected_element': {
            Canvas_Down: T('combo_wait_for_drag_selection', fseq(
                select_elem_under_cursor,
                remember_mouse_coords,
                redraw_view)),
        },
        'combo_over_selected_element': {
            Canvas_Down: T('combo_wait_for_drag_selection'),
        },

        'combo_dragging_marquee': {
            Canvas_Move: Internal(fseq(
                set_marquee,
                redraw_view)),
            Canvas_Up: Internal(fseq(
                select_overlapped_elements,
                clear_marquee,
                redraw_view,
                dispatch_Tool_Done)),
        },

        'combo_wait_for_drag_selection': {
            Canvas_Move: T('combo_dragging_selection'),
            Canvas_Up: Internal(dispatch_Tool_Done),  # nothing done, cancel
        },
        'combo_dragging_selection': {
            Canvas_Move: Internal(fseq(
                simulate_fake_move,
                redraw_view)),
            Canvas_Up: Internal(fseq(
                commit_real_move,
                redraw_view,
                remember_mouse_coords,  # so that next Initial can detect under
                dispatch_Tool_Done)),
        }
    }

    return (idle, engaged, trans)

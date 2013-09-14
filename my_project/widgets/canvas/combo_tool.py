import logging
_log = logging.getLogger(__name__)

import java.awt as awt
from hsmpy import Initial, T, Choice, Internal

from ...app import S
from ... import model
from ...util import fseq, Dummy
from elements import RectangleCE


#MARQUEE_STROKE_COLOR = awt.Color.BLUE
MARQUEE_FILL_COLOR = awt.Color(100, 100, 255, 40)


class MarqueeCE(RectangleCE):
    @property
    def fill_color(self):
        return MARQUEE_FILL_COLOR

    @property
    def stroke_color(self):
        return None



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

    # use infinity to make sure no element matches by accident
    data = Dummy(start_x=float('inf'),
                 start_y=float('inf'),
                 marquee=None,
                 moved=())

    selection = []  # this one keeps elements after tool has finished

    def set_selection(canvas_elems):
        assert isinstance(canvas_elems, (list, tuple))
        for cel in selection:
            cel.is_selected = False
        selection[:] = canvas_elems
        for cel in selection:
            assert cel.elem in canvas_model.elems, cel
            cel.is_selected = True

    def remember_start_coords(evt, _):
        data.start_x, data.start_y = evt.x, evt.y

    def elem_at(x, y):
        celems = view.elements_at(x, y)
        # sort so that already selected elements are at the beginning of list
        # that's useful when trying to click already selected element which
        # happens to be under unselected elem
        celems = sorted(celems, key=lambda cel: 0 if cel.is_selected else 1)
        return next(iter(celems), None)

    def whats_at_start_coords(*_):
        cel = elem_at(data.start_x, data.start_y)
        # FIXME: not working after commit since data has been reset
        if cel is None:
            return 'bg'
        elif cel.is_selected:
            return 'sel'
        else:
            return 'unsel'

    def select_elem_under_cursor(evt, hsm):
        cel = elem_at(evt.x, evt.y)
        set_selection([cel])

    def deselect_all(*_):
        set_selection([])

    def set_marquee(evt, _):
        x, y = view.transformed(data.start_x, data.start_y)
        ex, ey = view.transformed(evt.x, evt.y)
        rect = model.Rectangle(x, y, ex - x, ey - y + 1)  # prevents 0 w/h err
        if data.marquee is not None:
            data.marquee.elem = rect
        else:
            data.marquee = MarqueeCE(rect, view)
            view.add(data.marquee)

    def clear_marquee(*_):
        if data.marquee:
            view.remove(data.marquee)
            data.marquee = None

    def redraw_view(*_):
        view.repaint()

    def simulate_move(evt, hsm):
        x, y = data.start_x, data.start_y
        dx, dy = evt.x - x, evt.y - y
        if not data.moved:
            data.moved = tuple((cel.elem, cel) for cel in selection)
        for orig_el, cel in data.moved:
            cel.elem = orig_el.move(dx / view.zoom, dy / view.zoom)

    def undo_simulated_move(*_):
        for orig_el, cel in data.moved:
            cel.elem = orig_el
        data.moved = ()

    def commit_real_move(evt, hsm):
        x, y = data.start_x, data.start_y
        dx, dy = evt.x - x, evt.y - y
        if (dx, dy) == (0, 0):
            _log.info('nothing to commit, moved by 0 px')
            return
        changes = canvas_model.move([cel.elem for cel in selection],
                                    dx / view.zoom, dy / view.zoom)
        canvas_model.commit(changes)

    def select_overlapped_elements(evt, hsm):
        x, y = data.start_x, data.start_y
        ex, ey = evt.x, evt.y
        elems = view.elements_overlapping(x, y, ex, ey)
        elems.remove(data.marquee) if data.marquee in elems else ''
        set_selection(elems)
        _log.info('marquee overlapped {0} elems'.format(len(selection)))

    def signalize_finished(*_):
        eb.dispatch(Tool_Done())

    def clean_up(*_):
        undo_simulated_move()
        clear_marquee()
        data.reset()


    idle = {
        'combo_idle': S({
            'combo_over_background': S(),
            'combo_over_selected_element': S(),
            'combo_over_unselected_element': S(),
        }),
    }

    engaged = {
        'combo_engaged': S(on_exit=clean_up, states={
            'combo_dragging_marquee': S(),
            'combo_wait_for_drag_selection': S(),
            'combo_dragging_selection': S(),
        }),
    }


    trans = {
        'combo_idle': {
            Initial: Choice({
                'bg': 'combo_over_background',
                'sel': 'combo_over_selected_element',
                'unsel': 'combo_over_unselected_element',
            }, key=whats_at_start_coords, default='combo_over_background'),

            Canvas_Move: T('combo_idle', remember_start_coords),
        },
        'combo_engaged': {
            # never called, should always transition directly to substates
            Initial: T('combo_dragging_marquee', action=lambda _, __: 1 / 0),
        },

        'combo_over_background': {
            Canvas_Down: T('combo_dragging_marquee', fseq(
                deselect_all,
                remember_start_coords,
                set_marquee,
                redraw_view)),
        },
        'combo_over_unselected_element': {
            Canvas_Down: T('combo_wait_for_drag_selection', fseq(
                select_elem_under_cursor,
                remember_start_coords,
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
                signalize_finished)),
        },

        'combo_wait_for_drag_selection': {
            Canvas_Move: T('combo_dragging_selection'),
            Canvas_Up: Internal(signalize_finished),  # nothing done, cancel
        },
        'combo_dragging_selection': {
            Canvas_Move: Internal(fseq(
                simulate_move,
                redraw_view)),
            Canvas_Up: Internal(fseq(
                undo_simulated_move,
                commit_real_move,
                redraw_view,
                remember_start_coords,  # so that next Initial can detect under
                signalize_finished)),
        }
    }

    return (idle, engaged, trans)

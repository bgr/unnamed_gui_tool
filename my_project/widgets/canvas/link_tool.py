import logging
_log = logging.getLogger(__name__)

from hsmpy import Initial, T, Internal, Choice

from ...app import S
from ... import model
from ...util import fseq, Dummy
from elements import LinkCE, PathCE



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
                 end_x=float('inf'),
                 end_y=float('inf'),
                 start_elem=None,
                 end_elem=None,
                 preview=None)

    def remember_start_coords_and_elem(evt, _):
        data.start_x, data.start_y = evt.x, evt.y
        data.start_elem = elem_at(evt.x, evt.y)

    def remember_end_coords_and_elem(evt, _):
        data.end_x, data.end_y = evt.x, evt.y
        data.end_elem = elem_at(evt.x, evt.y)

    def whats_at_start_coords(*_):
        return 'el' if data.start_elem is not None else 'bg'

    def whats_at_end_coords(*_):
        return 'el' if data.end_elem is not None else 'bg'

    def elem_at(x, y):
        elems = view.elements_at(x, y)
        cel = next(iter(elems), None)
        # prevent linking Link to another Link or fake preview element
        if cel is None or cel is data.preview or isinstance(cel, LinkCE):
            return None
        else:
            return cel.elem

    def update_preview(evt, hsm):
        # remove old preview if it exists, since new might not be same type
        view.remove(data.preview) if data.preview else ''
        # preview is a link if mouse is over element
        if data.end_elem:
            elem = model.Link(data.start_elem, data.end_elem)
            start_cel = elem_map[data.start_elem]
            end_cel = elem_map[data.end_elem]
            data.preview = LinkCE(elem, start_cel, end_cel, view)
        # otherwise it's a straight line
        else:
            verts = (view.transformed(data.start_x, data.start_y),
                     view.transformed(data.end_x, data.end_y))
            elem = model.Path(verts)
            data.preview = PathCE(elem, view)
        view.add(data.preview)

    def remove_preview(*_):
        view.remove(data.preview) if data.preview else ''
        data.preview = None

    def redraw_view(*_):
        view.repaint()

    def commit_to_model(*_):
        link = model.Link(data.start_elem, data.end_elem)
        _log.info('about to commit link {0}'.format(link))
        canvas_model.commit([model.Insert(link)])

    def signalize_finished(*_):
        eb.dispatch(Tool_Done())

    def clean_up(*_):
        remove_preview()
        data.reset()


    idle = {
        'link_idle': S({
            'link_hover_over_background': S(),
            'link_hover_over_element': S(),
        }),
    }

    engaged = {
        'link_engaged': S(on_exit=clean_up, states={
            'link_wait_for_move': S(),
            'link_drawing': S({
                'link_drawing_over_background': S(),
                'link_drawing_over_element': S(),
            })
        }),
    }

    trans = {
        'link_idle': {
            Initial: Choice({
                'bg': 'link_hover_over_background',
                'el': 'link_hover_over_element', },
                key=whats_at_start_coords,
                default='link_hover_over_background'),

            Canvas_Move: T('link_idle', remember_start_coords_and_elem),
        },
        'link_hover_over_background': {
            # do nothing
        },
        'link_hover_over_element': {
            Canvas_Down: T('link_wait_for_move',
                           remember_start_coords_and_elem)
        },

        'link_engaged': {
            # never called, should always transition directly to substates
            Initial: T('link_wait_for_move', action=lambda _, __: 1 / 0),
            Canvas_Right_Down: Internal(fseq(
                signalize_finished,
                redraw_view)),
        },
        'link_wait_for_move': {
            Canvas_Move: T('link_drawing', remember_end_coords_and_elem),
        },
        'link_drawing': {
            Initial: Choice({
                'bg': 'link_drawing_over_background',
                'el': 'link_drawing_over_element',
            }, key=whats_at_end_coords, default='link_drawing_over_element'),
            Canvas_Move: T('link_drawing', fseq(
                remember_end_coords_and_elem,
                update_preview,
                redraw_view)),
        },
        'link_drawing_over_background': {
            # do nothing
        },
        'link_drawing_over_element': {
            Canvas_Up: Internal(fseq(
                remove_preview,
                commit_to_model,
                signalize_finished))
        },
    }

    return (idle, engaged, trans)

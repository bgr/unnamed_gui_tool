import logging
_log = logging.getLogger(__name__)

from hsmpy import Event, Initial, T, Internal, Choice

from ...app import S
from ...util import join_dicts, fseq, Dummy, keydefaultdict
from ...events import (WrappedEvent, Tool_Changed, Model_Changed,
                       PATH_TOOL, COMBO_TOOL, ELLIPSE_TOOL, LINK_TOOL)
from ... import model
from view import CanvasView
from elements import PathCE, LinkCE, RectangleCE, EllipseCE
# tool behaviors are defined using sub-HSMs in separate modules:
from . import path_tool, combo_tool, ellipse_tool, link_tool


DEFAULT_TOOL = COMBO_TOOL
ZOOM_IN_FACTOR = 1.15


def make(eventbus, canvas_model):
    """
        Main function that creates the view instance wired up with HSM states
        and transitions that this function returns, which are ready to be used
        as a standalone HSM or assembled into larger HSM hierarchy as
        submachines.
    """
    # declaring events here in order to make sure that each view-controller
    # pair has their own unique events, to prevent one controller responding
    # to other's view's events
    class Canvas_Down(WrappedEvent): pass
    class Canvas_Up(WrappedEvent): pass
    class Canvas_Right_Down(WrappedEvent): pass
    class Canvas_Right_Up(WrappedEvent): pass
    class Canvas_Middle_Down(WrappedEvent): pass
    class Canvas_Middle_Up(WrappedEvent): pass
    class Canvas_Move(WrappedEvent): pass
    class Canvas_Wheel(WrappedEvent): pass
    class Tool_Done(Event): pass

    def make_dispatcher(button_up_or_down):
        clsmap = {
            ('down', 1): Canvas_Down,
            ('down', 2): Canvas_Middle_Down,
            ('down', 3): Canvas_Right_Down,
            ('up', 1): Canvas_Up,
            ('up', 2): Canvas_Middle_Up,
            ('up', 3): Canvas_Right_Up,
        }

        def dispatcher(evt):
            Cls = clsmap.get( (button_up_or_down, evt.button) )
            if Cls:
                eventbus.dispatch(Cls(evt))

        return dispatcher


    view = CanvasView(300, 300)
    view.mousePressed = make_dispatcher('down')
    view.mouseReleased = make_dispatcher('up')
    view.mouseMoved = lambda evt: eventbus.dispatch(Canvas_Move(evt))
    view.mouseDragged = view.mouseMoved
    view.mouseWheelMoved = lambda evt: eventbus.dispatch(Canvas_Wheel(evt))

    # this dict will be used by HSMs to get CanvasElement instance for any
    # model element
    elem_map = keydefaultdict()

    def get_cel(el):
        """Returns CanvasElement instance for given model element."""
        factory = {
            model.Rectangle: lambda: RectangleCE(el, view),
            model.Ellipse: lambda: EllipseCE(el, view),
            model.Path: lambda: PathCE(el, view),
            model.Link: lambda: LinkCE(el, elem_map[el.a],
                                       elem_map[el.b], view),
        }
        cel = factory[el.__class__]()
        return cel

    elem_map.default_factory = get_cel
    # had to assign default_factory here since get_cel needs reference to
    # existing elem_map instance in order to be able to get link targets


    def apply_changes(changes):
        def insert(ch):
            new_cel = elem_map[ch.elem]  # will instantiate
            view.add(new_cel)

        def remove(ch):
            cel = elem_map[ch.elem]
            view.remove(cel)
            del elem_map[ch.elem]
            # TODO: remove from selected list in combo_tool.py

        def modify(ch):
            cel = elem_map[ch.elem]
            del elem_map[ch.elem]
            elem_map[ch.modified] = cel
            cel.elem = ch.modified
            # line above will make CanvasElement return new Shape to be
            # rendered once its shape property gets accessed next time

        switch = {
            model.Insert: insert,
            model.Remove: remove,
            model.Modify: modify,
        }

        # sort changes so that links are at the end, to ensure that
        # CanvasModelElements they are linked to are already
        # instantiated/updated before instantiating/updating LinkCE
        is_link = lambda chg: isinstance(chg.elem, model.Link)
        changes = sorted(changes, key=lambda chg: 0 if not is_link(chg) else 1)
        for ch in changes:
            switch[ch.__class__](ch)
        assert len(elem_map) == len(canvas_model._elems), "elem_map not synced"
        assert len(view._elems) == len(canvas_model._elems), "view not synced"


    # draw elements that are already in the model
    apply_changes(model.Insert(el) for el in canvas_model._elems)
    view.repaint()


    data = Dummy(prev_cursor_pos=None)


    def set_up(hsm):
        hsm.data.canvas_tool = DEFAULT_TOOL
        _log.info("HSM tool set to {0}".format(hsm.data.canvas_tool))

    def remember_selected_tool(evt, hsm):
        hsm.data.canvas_tool = evt.data
        _log.info('remembered selected tool {0}'.format(hsm.data.canvas_tool))


    def redraw_view(*_):
        view.repaint()

    def get_tool(_, hsm):
        return hsm.data.canvas_tool or DEFAULT_TOOL

    def zoom_view(evt, _):
        vx1, vy1 = view.transformed(evt.x, evt.y)
        if evt.wheelRotation > 0:
            view.zoom_by(1.0 / ZOOM_IN_FACTOR)
        else:
            view.zoom_by(ZOOM_IN_FACTOR)
        vx2, vy2 = view.transformed(evt.x, evt.y)
        # pan the view so that mouse cursor position is the zoom center point
        view.pan_by(vx2 - vx1, vy2 - vy1, zoom=False)

    def remember_cursor_pos(evt, _):
        data.prev_cursor_pos = (evt.x, evt.y)

    def pan_view(evt, _):
        x, y = data.prev_cursor_pos
        view.pan_by(evt.x - x, evt.y - y)


    event_pack = [Canvas_Down, Canvas_Up, Canvas_Right_Down, Canvas_Right_Up,
                  Canvas_Middle_Down, Canvas_Middle_Up, Canvas_Move,
                  Canvas_Wheel, Tool_Done]

    combo_idle, combo_engaged, combo_trans = combo_tool.make(
        eventbus, view, event_pack, elem_map, canvas_model)

    link_idle, link_engaged, link_trans = link_tool.make(
        eventbus, view, event_pack, elem_map, canvas_model)

    ellipse_idle, ellipse_engaged, ellipse_trans = ellipse_tool.make(
        eventbus, view, event_pack, elem_map, canvas_model)

    path_idle, path_engaged, path_trans = path_tool.make(
        eventbus, view, event_pack, elem_map, canvas_model)


    states = {
        'top': S(on_enter=set_up, states={
            'idle': S(join_dicts(
                combo_idle,
                link_idle,
                ellipse_idle,
                path_idle,
            )),
            'engaged': S(join_dicts(
                combo_engaged,
                link_engaged,
                ellipse_engaged,
                path_engaged,
            )),
            'panning': S(),
        })
    }


    trans = join_dicts(
        combo_trans,
        link_trans,
        ellipse_trans,
        path_trans,
        {
            'top': {
                Initial: T('idle'),
                Model_Changed: Internal(fseq(
                    lambda evt, _: apply_changes(evt.data),
                    redraw_view)),
                Canvas_Wheel: Internal(fseq(
                    zoom_view,
                    redraw_view)),
            },
            'idle': {
                Initial: Choice(
                    {
                        COMBO_TOOL: 'combo_idle',
                        LINK_TOOL: 'link_idle',
                        ELLIPSE_TOOL: 'ellipse_idle',
                        PATH_TOOL: 'path_idle',
                        # TODO: reorganize code, referencing state name that's
                        # not specified in this file = ugly
                    },
                    default='combo_idle',
                    key=get_tool),
                # tool is idle, safe to change to another tool by reentering
                Tool_Changed: T('idle', remember_selected_tool),
                Canvas_Middle_Down: T('panning', remember_cursor_pos),
            },
            'engaged': {
                # should never be called since substates are always
                # transitioned to directly
                Initial: T('combo_engaged', action=lambda _, __: 1 / 0),
                # tool is engaged, remember new tool for later, don't change
                Tool_Changed: Internal(remember_selected_tool),
                Tool_Done: T('idle'),
            },
            'panning': {
                Canvas_Move: Internal(fseq(
                    pan_view,
                    remember_cursor_pos,
                    redraw_view)),
                Canvas_Middle_Up: T('idle'),
            },
        }
    )

    return (view, states, trans)

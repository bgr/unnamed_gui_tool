from hsmpy import Event, State, Initial
from hsmpy import Transition as T
from javax.swing import JToolBar
from util import make_button

from hsmpy.events import (Choose_Combo_Tool, Choose_Rectangle_Tool,
                          Choose_Polyline_Tool)



def make(eventbus):
    view = _make_view(eventbus)

    states = {
    }

    trans = {
    }

    return (view, states, trans)


def _make_view(eventbus):
    toolbar = JToolBar("Tools")
    btn_combo = make_button("select.png", "Combo", "Combo tool", "Combo TOOL")
    btn_rect = make_button("rect.png", "Rectangle", "Rectangle tool",
                           "Rectangle TOOL")
    btn_poly = make_button("poly.png", "Polyline", "Polyline tool",
                           "Polyline TOOL")
    toolbar.add(btn_combo)
    toolbar.add(btn_rect)
    toolbar.add(btn_poly)

    btn_combo.mousePressed = lambda: eventbus.dispatch(Choose_Combo_Tool())
    btn_rect.mousePressed = lambda: eventbus.dispatch(Choose_Rectangle_Tool())
    btn_poly.mousePressed = lambda: eventbus.dispatch(Choose_Polyline_Tool())

    return toolbar

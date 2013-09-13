#from hsmpy import Event, State, Initial, T
from javax.swing import JToolBar

from ..javautils import make_button
from ..events import (Tool_Changed, COMBO_TOOL, LINK_TOOL, ELLIPSE_TOOL,
                      PATH_TOOL)



def make(eb):
    view = JToolBar("Tools")
    btn_combo = make_button("Combo",
                            "Select and move elements",
                            "res/icons/combo-tool.png")
    btn_link = make_button("Link",
                           "Create link between two elements",
                           "res/icons/link-tool.png")
    btn_ellipse = make_button("Ellipse",
                              "Create new ellipse element",
                              "res/icons/document-new.png")  # TODO: change
    btn_path = make_button("Path",
                           "Create new path element")  # TODO: to be removed
    view.add(btn_combo)
    view.add(btn_link)
    view.add(btn_ellipse)
    view.add(btn_path)

    btn_combo.mousePressed = lambda _: eb.dispatch(Tool_Changed(COMBO_TOOL))
    btn_link.mousePressed = lambda _: eb.dispatch(Tool_Changed(LINK_TOOL))
    btn_ellipse.mousePressed = lambda _: eb.dispatch(Tool_Changed(ELLIPSE_TOOL))
    btn_path.mousePressed = lambda _: eb.dispatch(Tool_Changed(PATH_TOOL))

    states = {
    }

    trans = {
    }

    return (view, states, trans)

#from hsmpy import Event, State, Initial, T
from javax.swing import JToolBar

from ..javautils import make_button
from ..events import Tool_Changed, COMBO_TOOL, PATH_TOOL, ELLIPSE_TOOL



def make(eb):
    view = JToolBar("Tools")
    btn_combo = make_button("Combo",
                            "Select and move elements",
                            "res/icons/combo-tool.png")
    btn_path = make_button("Path",
                           "Create new path element",
                           "res/icons/link-tool.png")
    btn_ellipse = make_button("Ellipse",
                              "Create new ellipse element",
                              "res/icons/document-new.png")  # TODO: change
    view.add(btn_combo)
    view.add(btn_path)
    view.add(btn_ellipse)

    btn_combo.mousePressed = lambda _: eb.dispatch(Tool_Changed(COMBO_TOOL))
    btn_path.mousePressed = lambda _: eb.dispatch(Tool_Changed(PATH_TOOL))
    btn_ellipse.mousePressed = lambda _: eb.dispatch(Tool_Changed(ELLIPSE_TOOL))

    states = {
    }

    trans = {
    }

    return (view, states, trans)

#from hsmpy import Event, State, Initial, T
from java.awt import Dimension
from javax.swing import JToolBar

from ..javautils import make_button
from ..events import (Tool_Changed, Undo_Requested, Redo_Requested, COMBO_TOOL,
                      LINK_TOOL, ELLIPSE_TOOL, PATH_TOOL)



def make(eb):
    view = JToolBar("Tools")
    btn_undo = make_button("Undo",
                           "Undo previous action",
                           "res/icons/edit-undo.png")
    btn_redo = make_button("Redo",
                           "Redo previously undone action",
                           "res/icons/edit-redo.png")
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
    view.add(btn_undo)
    view.add(btn_redo)
    view.add(JToolBar.Separator(Dimension(30, 30)))
    view.add(btn_combo)
    view.add(btn_link)
    view.add(btn_ellipse)
    view.add(btn_path)

    btn_undo.mousePressed = lambda _: eb.dispatch(Undo_Requested())
    btn_redo.mousePressed = lambda _: eb.dispatch(Redo_Requested())
    btn_combo.mousePressed = lambda _: eb.dispatch(Tool_Changed(COMBO_TOOL))
    btn_link.mousePressed = lambda _: eb.dispatch(Tool_Changed(LINK_TOOL))
    btn_ellipse.mousePressed = lambda _: eb.dispatch(Tool_Changed(ELLIPSE_TOOL))
    btn_path.mousePressed = lambda _: eb.dispatch(Tool_Changed(PATH_TOOL))

    states = {
    }

    trans = {
    }

    return (view, states, trans)

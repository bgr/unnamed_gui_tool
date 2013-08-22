import java.awt as awt
from javax.swing import JPanel

from ... import model
from ...util import fseq


class CanvasView(JPanel):

    def __init__(self, width, height):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []

        self._elems = []
        self._draw_once_elems = []
        self._selected = set([])
        self._background_color = awt.Color.WHITE
        self._stroke_color = awt.Color.BLACK

        # maps model elements to corresponding functions that can draw them
        self.drawing_handlers = {
            model.Ellipse: CanvasView.draw_ellipse,
            model.Rectangle: CanvasView.draw_rectangle,
            model.Path: CanvasView.draw_path,
            #model.Polygon: CanvasView.draw_polygon,
        }

    @property
    def background_color(self):  # TODO: redundant, JPanel already has this
        return self._background_color


    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.repaint()


    def add_elem(self, elem, repaint=False):
        self._elems += [elem]
        if repaint:
            self.repaint()


    def remove_elem(self, elem, repaint=False):
        self._elems.remove(elem)
        if repaint:
            self.repaint()


    @property
    def selection(self):
        return self._selected


    @selection.setter
    def selection(self, elems):
        self._selected = set(elems)
        self.repaint()


    def draw_changes(self, changes):
        switch = {
            model.Insert: lambda ch: self.add_elem(ch.elem),
            model.Remove: lambda ch: self.remove_elem(ch.elem),
            model.Modify: fseq(
                lambda ch: self.remove_elem(ch.elem),
                lambda ch: self.add_elem(ch.modified)
            ),
        }
        [switch[ch.__class__](ch) for ch in changes]
        self.repaint()


    def draw_once(self, elems):
        self._draw_once_elems = elems
        self.repaint()


    def paintComponent(self, g):
        # TODO: repaint only changed regions
        g.color = self.background_color
        g.fillRect(0, 0, self.width, self.height)
        g.color = self._stroke_color
        for el in self._elems + self._draw_once_elems:
            self.drawing_handlers[el.__class__](el, g)

    # functions that perform drawing for each supported element type:

    @staticmethod
    def draw_rectangle(el, g):
        g.drawRect(*map(int, el))

    @staticmethod
    def draw_ellipse(el, g):
        g.drawOval(*map(int, el))

    @staticmethod
    def draw_path(el, g):
        shape = awt.geom.Path2D.Float()
        shape.moveTo(*el.vertices[0])
        for v in el.vertices[1:]:
            shape.lineTo(*v)
        g.draw(shape)

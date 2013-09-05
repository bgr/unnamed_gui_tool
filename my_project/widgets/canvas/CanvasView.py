import java.awt as awt
from javax.swing import JPanel

from ... import model
from ...util import fseq


class CanvasView(JPanel):

    # TODO: query functionality maybe should be moved from model to here
    def __init__(self, width, height, query):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []
        self.query = query

        self._elems = []
        self._draw_once_elems = []
        self._selected = set([])
        self._background_color = awt.Color.WHITE
        self._stroke_color = awt.Color.BLACK

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
            model.Insert: lambda ch: self.add_elem(ch.elem, repaint=False),
            model.Remove: lambda ch: self.remove_elem(ch.elem, repaint=False),
            model.Modify: fseq(
                lambda ch: self.remove_elem(ch.elem, repaint=False),
                lambda ch: self.add_elem(ch.modified, repaint=False),
            ),
        }
        for ch in changes:
            switch[ch.__class__](ch)
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
            g.draw(shape(el))


    def elements_at(self, x, y):
        elems = self.query.under(x, y)

        def contains(el, x, y):
            sh = shape(el)
            if isinstance(el, model.Path):
                # have to check against the stroke since Java's path is
                # implicitly closed and behaves like a polygon
                sh = awt.BasicStroke(2).createStrokedShape(sh)
            return sh.contains(x, y)

        return [el for el in elems if contains(el, x, y)]



def rectangle(el):
    return awt.geom.Rectangle2D.Double(el.x, el.y, el.width, el.height)

def ellipse(el):
    return awt.geom.Ellipse2D.Double(el.x, el.y, el.width, el.height)

def path(el):
    shape = awt.geom.Path2D.Float()
    shape.moveTo(*el.vertices[0])
    for v in el.vertices[1:]:
        shape.lineTo(*v)
    return shape


# maps model elements to functions that create java.awt.Shape out of them
shape_map = {
    model.Ellipse: ellipse,
    model.Rectangle: rectangle,
    model.Path: path,
    #model.Polygon: polygon,
}

def shape(model_element):
    return shape_map[model_element.__class__](model_element)

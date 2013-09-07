import java.awt as awt
from javax.swing import JPanel

from ... import model

BACKGROUND_COLOR = awt.Color.WHITE
ELEMENT_STROKE_COLOR = awt.Color.BLACK
ELEMENT_FILL_COLOR = awt.Color(200, 200, 200, 40)
SELECTED_STROKE_COLOR = awt.Color.RED
SELECTED_FILL_COLOR = ELEMENT_FILL_COLOR
MARQUEE_STROKE_COLOR = awt.Color.BLUE
MARQUEE_FILL_COLOR = awt.Color(100, 100, 255, 40)

LINE_STROKE_WIDTH = 9


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
        self._marquee = None
        self._transform = awt.geom.AffineTransform()


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


    @property
    def marquee(self):
        return self._marquee

    @marquee.setter
    def marquee(self, rect_tuple):
        """Marquee rectangle format is (x1, y1, x2, y2)."""
        if rect_tuple is None:
            self._marquee = None
            return
        x1, y1, x2, y2 = rect_tuple
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        self._marquee = (x1, y1, x2, y2)


    def apply_changes(self, changes):
        def insert(ch):
            self.add_elem(ch.elem, repaint=False)

        def remove(ch):
            self.remove_elem(ch.elem, repaint=False)
            if ch.elem in self._selected:
                self._selected.remove(ch.elem)

        def modify(ch):
            self.remove_elem(ch.elem, repaint=False)
            self.add_elem(ch.modified, repaint=False)
            if ch.elem in self._selected:
                self._selected.remove(ch.elem)
                self._selected.add(ch.modified)

        switch = {
            model.Insert: insert,
            model.Remove: remove,
            model.Modify: modify,
        }

        for ch in changes:
            switch[ch.__class__](ch)


    @property
    def draw_once(self):
        return self._draw_once_elems

    @draw_once.setter
    def draw_once(self, elems):
        assert isinstance(elems, (list, tuple))
        self._draw_once_elems = list(elems)


    @property
    def zoom(self):
        return self._transform.getScaleX()

    @property
    def pan_x(self):
        return self._transform.getTranslateX()

    @property
    def pan_y(self):
        return self._transform.getTranslateY()


    def zoom_by(self, value):
        self._transform.scale(value, value)

    def pan_by(self, h, v, zoom=True):
        z = self.zoom if zoom else 1
        self._transform.translate(h / z, v / z)

    def transformed(self, x, y):
        return ((x - self.pan_x) / self.zoom, (y - self.pan_y) / self.zoom)


    def paintComponent(self, g):
        # TODO: repaint only changed regions
        g.color = self.background
        g.fillRect(0, 0, self.width, self.height)

        g.setRenderingHint(awt.RenderingHints.KEY_ANTIALIASING,
                           awt.RenderingHints.VALUE_ANTIALIAS_ON)
        g.setRenderingHint(awt.RenderingHints.KEY_TEXT_ANTIALIASING,
                           awt.RenderingHints.VALUE_TEXT_ANTIALIAS_ON)

        old_trans = g.getTransform().clone()
        new_trans = old_trans.clone()
        new_trans.concatenate(self._transform)
        g.setTransform(new_trans)

        for el in self._elems + self._draw_once_elems:
            if el in self._selected:
                stroke, fill = SELECTED_STROKE_COLOR, SELECTED_FILL_COLOR
            else:
                stroke, fill = ELEMENT_STROKE_COLOR, ELEMENT_FILL_COLOR
            sh = shape(el)
            g.color = fill
            g.fill(sh) if not isinstance(el, model.Path) else None
            g.color = stroke
            g.draw(sh)

        self._draw_once_elems = []
        g.setTransform(old_trans)

        if self._marquee:
            x1, y1, x2, y2 = self.marquee
            g.color = MARQUEE_FILL_COLOR
            g.fillRect(x1, y1, x2 - x1, y2 - y1)
            g.color = MARQUEE_STROKE_COLOR
            g.drawRect(x1, y1, x2 - x1, y2 - y1)


    def elements_at(self, x, y):
        x, y = self.transformed(x, y)
        elems = self.query.under(x, y)  # coarse, checks against bounding boxes

        def check(el):  # precise, checks using java.awt.Shape
            sh = shape(el)
            if isinstance(el, model.Path):
                # have to check against the stroke since Java's path is
                # implicitly closed and behaves like a polygon
                stroke_width = LINE_STROKE_WIDTH / self.zoom
                sh = awt.BasicStroke(stroke_width).createStrokedShape(sh)
            return sh.contains(x, y)

        return [el for el in elems if check(el)]

    def elements_overlapping(self, x1, y1, x2, y2):
        x1, y1 = self.transformed(x1, y1)
        x2, y2 = self.transformed(x2, y2)
        elems = self.query.overlapped(x1, y1, x2, y2)

        def check(el):
            sh = shape(el)
            if isinstance(el, model.Path):
                stroke_width = LINE_STROKE_WIDTH / self.zoom
                sh = awt.BasicStroke(stroke_width).createStrokedShape(sh)
            return sh.intersects(x1, y1, x2 - x1, y2 - y1)

        return [el for el in elems if check(el)]



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

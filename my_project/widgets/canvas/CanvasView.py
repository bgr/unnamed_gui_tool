import java.awt as awt
from javax.swing import JPanel
from quadpy.quadtree import fits, overlaps, fix_bounds

from ... import model

BACKGROUND_COLOR = awt.Color.WHITE
ELEMENT_STROKE_COLOR = awt.Color.BLACK
ELEMENT_FILL_COLOR = awt.Color(200, 200, 200, 40)
SELECTED_STROKE_COLOR = awt.Color.RED
SELECTED_FILL_COLOR = ELEMENT_FILL_COLOR
MARQUEE_STROKE_COLOR = awt.Color.BLUE
MARQUEE_FILL_COLOR = awt.Color(100, 100, 255, 40)

LINE_STROKE_WIDTH = 9


# TODO:
# switch to quadtree completely (under, overlapping, enclosed)
# implement marquee using CanvasElement
# repaint dirty regions only
# stroke color logic should be implemented in CanvasElement
# move drawing logic to CanvasElement
# implement hittest in CanvasElement
# get rid of draw_once
# modifying should reuse CanvasElement instance


class CanvasView(JPanel):

    def __init__(self, width, height):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)

        self._elems = {}
        self._draw_once_elems = {}
        self._selected = set([])
        self._marquee = None
        self._transform = awt.geom.AffineTransform()


    def add_elem(self, elem, repaint=False):
        self._elems.update({ elem: CanvasElement(elem) })
        if repaint:
            self.repaint()


    def remove_elem(self, elem, repaint=False):
        del self._elems[elem]
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
        self._marquee = fix_bounds(rect_tuple)


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
        self._draw_once_elems = dict((el, CanvasElement(el)) for el in elems)


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

        for cel in self._elems.values() + self._draw_once_elems.values():
            if cel.elem in self._selected:
                stroke, fill = SELECTED_STROKE_COLOR, SELECTED_FILL_COLOR
            else:
                stroke, fill = ELEMENT_STROKE_COLOR, ELEMENT_FILL_COLOR
            g.color = fill
            g.fill(cel.shape) if not isinstance(cel.elem, model.Path) else None
            g.color = stroke
            g.draw(cel.shape)

        self.draw_once = []
        g.setTransform(old_trans)

        if self._marquee:
            x1, y1, x2, y2 = self.marquee
            g.color = MARQUEE_FILL_COLOR
            g.fillRect(x1, y1, x2 - x1, y2 - y1)
            g.color = MARQUEE_STROKE_COLOR
            g.drawRect(x1, y1, x2 - x1, y2 - y1)


    def elements_at(self, x, y):
        x, y = self.transformed(x, y)
        cels = self._under(x, y)  # coarse, checks against bounding boxes

        def check(cel):  # precise, checks using java.awt.Shape
            sh = cel.shape
            if isinstance(cel.elem, model.Path):
                # have to check against the stroke since Java's path is
                # implicitly closed and behaves like a polygon
                stroke_width = LINE_STROKE_WIDTH / self.zoom
                sh = awt.BasicStroke(stroke_width).createStrokedShape(sh)
            return sh.contains(x, y)

        return [cel.elem for cel in cels if check(cel)]


    def elements_overlapping(self, x1, y1, x2, y2):
        x1, y1 = self.transformed(x1, y1)
        x2, y2 = self.transformed(x2, y2)
        cels = self._overlapped(x1, y1, x2, y2)

        def check(cel):
            sh = cel.shape
            if isinstance(cel.elem, model.Path):
                stroke_width = LINE_STROKE_WIDTH / self.zoom
                sh = awt.BasicStroke(stroke_width).createStrokedShape(sh)
            return sh.intersects(x1, y1, x2 - x1, y2 - y1)

        return [cel.elem for cel in cels if check(cel)]

    def _under(self, x, y):
        def is_under(cel):  # TODO: switch to quadtree
            el_x1, el_y1, el_x2, el_y2 = cel.bounds
            return (el_x1 <= x <= el_x2) and (el_y1 <= y <= el_y2)

        res = filter(is_under, self._elems.values())
        return res

    def _enclosed(self, x1, y1, x2, y2):
        def is_enclosed(cel):  # TODO: switch to quadtree
            return fits(cel.bounds, (x1, y1, x2, y2))

        res = filter(is_enclosed, self._elems.values())
        return res

    def _overlapped(self, x1, y1, x2, y2):
        def is_overlapped(cel):  # TODO: switch to quadtree
            return overlaps(cel.bounds, (x1, y1, x2, y2))

        res = filter(is_overlapped, self._elems.values())
        return res



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


class CanvasElement(object):
    def __init__(self, elem):
        assert elem.__class__ in shape_map.keys(), "unsupported element"
        self._elem = elem
        self._must_update = True

    @property
    def elem(self):
        return self._elem

    #@elem.setter
    #def elem(self, new_elem):
        #assert type(new_elem) == type(self.elem), "must be same type as old"
        #self._elem = new_elem
        #self._must_update = True

    @property
    def shape(self):
        if self._must_update:  # elem was changed in the meantime
            self._shape = shape_map[self.elem.__class__](self.elem)
            self._must_update = False
        return self._shape

    @property
    def bounds(self):
        b = self.shape.getBounds()
        return b.x, b.y, b.x + b.width, b.y + b.height

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.elem)

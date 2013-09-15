import java.awt as awt
from view import CanvasElement
from ... import model


ELEMENT_STROKE_COLOR = awt.Color.BLACK
ELEMENT_FILL_COLOR = awt.Color(200, 200, 200, 40)
SELECTED_STROKE_COLOR = awt.Color.RED
SELECTED_FILL_COLOR = ELEMENT_FILL_COLOR

LINE_STROKE_WIDTH = 9


class CanvasModelElement(CanvasElement):
    def __init__(self, elem, canvas):
        super(CanvasModelElement, self).__init__(canvas)
        self._elem = elem
        self._is_selected = False

    @property
    def elem(self):
        return self._elem

    @elem.setter
    def elem(self, new_elem):
        assert type(new_elem) == type(self.elem), "must be same type as old"
        self._elem = new_elem
        self._must_update = True

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.elem)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, true_or_false):
        self._is_selected = true_or_false

    @property
    def fill_color(self):
        if self.is_selected:
            return SELECTED_FILL_COLOR
        else:
            return super(CanvasModelElement, self).fill_color

    @property
    def stroke_color(self):
        if self.is_selected:
            return SELECTED_STROKE_COLOR
        else:
            return super(CanvasModelElement, self).stroke_color

    #@staticmethod
    #def make(elem, canvas):
    #    elem_map = {
    #        model.Rectangle: RectangleCE,
    #        model.Ellipse: EllipseCE,
    #        model.Path: PathCE,
    #        model.Link: LinkCE,
    #    }
    #    return elem_map[elem.__class__](elem, canvas)



class RectangleCE(CanvasModelElement):
    def __init__(self, elem, canvas):
        assert isinstance(elem, model.Rectangle)
        super(RectangleCE, self).__init__(elem, canvas)

    def _make_shape(self):
        return awt.geom.Rectangle2D.Double(self.elem.x, self.elem.y,
                                           self.elem.width, self.elem.height)


class EllipseCE(CanvasModelElement):
    def __init__(self, elem, canvas):
        assert isinstance(elem, model.Ellipse)
        super(EllipseCE, self).__init__(elem, canvas)

    def _make_shape(self):
        return awt.geom.Ellipse2D.Double(self.elem.x, self.elem.y,
                                         self.elem.width, self.elem.height)


class PathCE(CanvasModelElement):
    def __init__(self, elem, canvas):
        assert isinstance(elem, model.Path)
        super(PathCE, self).__init__(elem, canvas)

    def _make_shape(self):
        shape = awt.geom.Path2D.Float()
        shape.moveTo(*self.elem.vertices[0])
        for v in self.elem.vertices[1:]:
            shape.lineTo(*v)
        return shape

    @property
    def fill_color(self):
        return None

    def hit_test(self, x, y):
        # have to check against the stroke since Java's path is
        # implicitly closed and behaves like a polygon
        stroke_width = LINE_STROKE_WIDTH / self.canvas.zoom
        sh = awt.BasicStroke(stroke_width).createStrokedShape(self.shape)
        return sh.contains(x, y)

    def intersects(self, x1, y1, x2, y2):
        stroke_width = LINE_STROKE_WIDTH / self.canvas.zoom
        sh = awt.BasicStroke(stroke_width).createStrokedShape(self.shape)
        return sh.intersects(x1, y1, x2 - x1, y2 - y1)



class LinkCE(PathCE):
    def __init__(self, elem, a, b, canvas):
        assert isinstance(elem, model.Link)
        assert isinstance(a, CanvasModelElement)
        assert isinstance(b, CanvasModelElement)
        super(PathCE, self).__init__(elem, canvas)
        self.a = a
        self.b = b

    def _make_shape(self):
        shape = awt.geom.Path2D.Float()
        ax1, ay1, ax2, ay2 = self.a.bounds
        bx1, by1, bx2, by2 = self.b.bounds
        shape.moveTo((ax1 + ax2) / 2, (ay1 + ay2) / 2)
        shape.lineTo((bx1 + bx2) / 2, (by1 + by2) / 2)
        return shape

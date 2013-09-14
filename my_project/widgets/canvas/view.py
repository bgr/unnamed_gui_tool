import java.awt as awt
from javax.swing import JPanel
from quadpy.quadtree import fits, overlaps, fix_bounds

BACKGROUND_COLOR = awt.Color.WHITE

# TODO:
# switch to quadtree completely (under, overlapping, enclosed)
# repaint dirty regions only


class CanvasElement(object):
    def __init__(self, canvas):
        self._canvas = canvas
        self._must_update = True  # change this when shape should be updated
        self._fill_color = None
        self._stroke_color = awt.Color.BLACK

    @property
    def canvas(self):
        return self._canvas

    @property
    def shape(self):
        if self._must_update:
            self._shape = self._make_shape()
            self._must_update = False
        return self._shape

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, color):
        self._fill_color = color

    @property
    def stroke_color(self):
        return self._stroke_color

    @stroke_color.setter
    def stroke_color(self, color):
        self._stroke_color = color

    @property
    def bounds(self):
        b = self.shape.getBounds()
        return b.x, b.y, b.x + b.width, b.y + b.height

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__)

    def _make_shape(self):
        raise NotImplementedError("override me")

    def hit_test(self, x, y):
        return self.shape.contains(x, y)

    def intersects(self, x1, y1, x2, y2):
        return self.shape.intersects(x1, y1, x2 - x1, y2 - y1)



class CanvasView(JPanel):
    """ Java Swing component responsible for drawing CanvasElement instances
        that are added to it.
    """

    def __init__(self, width, height):
        super(self.__class__, self).__init__()
        self.size = (width, height)
        self.preferredSize = (width, height)
        self._elems = []
        self._transform = awt.geom.AffineTransform()


    def add(self, canvas_element, repaint=False):
        assert isinstance(canvas_element, CanvasElement)
        self._elems.append(canvas_element)
        if repaint:
            self.repaint()

    def remove(self, canvas_element, repaint=False):
        self._elems.remove(canvas_element)
        if repaint:
            self.repaint()

    def zoom_by(self, value):
        """Zooms the view by given value (added to previous zoom value)."""
        self._transform.scale(value, value)

    @property
    def zoom(self):
        """Returns current zoom value."""
        return self._transform.getScaleX()


    def pan_by(self, h, v, zoom=True):
        """ Pans the view by given horizontal and vertical offset in pixels,
            compensating for zoom by default.
        """
        z = self.zoom if zoom else 1
        self._transform.translate(h / z, v / z)

    @property
    def pan_x(self):
        """Returns current horizontal pan offset."""
        return self._transform.getTranslateX()

    @property
    def pan_y(self):
        """Returns current vertical pan offset."""
        return self._transform.getTranslateY()


    def transformed(self, x, y):
        """ Returns transformed point tuple (x, y)."""
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

        for el in self._elems:
            if el.fill_color is not None:
                g.color = el.fill_color
                g.fill(el.shape)
            if el.stroke_color is not None:
                g.color = el.stroke_color
                g.draw(el.shape)

        g.setTransform(old_trans)


    def elements_at(self, x, y, precise=True):
        """ Returns CanvasElements under the point defined by given screen
            coordirnates.
        """
        x, y = self.transformed(x, y)
        cels = self._under(x, y)  # coarse, checks against bounding boxes
        if precise:
            return [cel for cel in cels if cel.hit_test(x, y)]
        else:
            return cels


    def elements_overlapping(self, x1, y1, x2, y2, precise=True):
        """ Returns CanvasElements intersecting with rectangle defined by
            given screen coordirnates.
        """
        x1, y1, x2, y2 = fix_bounds((x1, y1, x2, y2))
        x1, y1 = self.transformed(x1, y1)
        x2, y2 = self.transformed(x2, y2)
        cels = self._overlapped(x1, y1, x2, y2)
        if precise:
            return [cel for cel in cels if cel.intersects(x1, y1, x2, y2)]
        else:
            return cels


    def _under(self, x, y):
        def is_under(cel):  # TODO: switch to quadtree
            el_x1, el_y1, el_x2, el_y2 = cel.bounds
            return (el_x1 <= x <= el_x2) and (el_y1 <= y <= el_y2)

        res = filter(is_under, self._elems)
        return res

    def _enclosed(self, x1, y1, x2, y2):
        def is_enclosed(cel):  # TODO: switch to quadtree
            return fits(cel.bounds, (x1, y1, x2, y2))

        res = filter(is_enclosed, self._elems)
        return res

    def _overlapped(self, x1, y1, x2, y2):
        def is_overlapped(cel):  # TODO: switch to quadtree
            return overlaps(cel.bounds, (x1, y1, x2, y2))

        res = filter(is_overlapped, self._elems)
        return res

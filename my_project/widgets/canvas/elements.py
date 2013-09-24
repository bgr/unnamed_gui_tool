import java.awt as awt
from view import CanvasElement
from ... import model


ELEMENT_STROKE_COLOR = awt.Color.BLACK
ELEMENT_FILL_COLOR = awt.Color(200, 200, 200, 40)
SELECTED_STROKE_COLOR = awt.Color.RED
SELECTED_FILL_COLOR = ELEMENT_FILL_COLOR

LINE_STROKE_WIDTH = 9
PATH_PRECISION = 1


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
        if self.a == self.b:  # draw self-loop
            x1, y1, x2, y2 = self.a.bounds
            center_x, center_y = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            y_top = max(y1 + 2, center_y - 10)
            y_bot = min(y2 - 2, center_y + 10)
            l1 = (center_x, y_top, x2 + 10, y_top)
            l2 = (center_x, y_bot, x2 + 10, y_bot)
            # make sure the points are on the right side
            start_x, start_y = nearest(
                points_on_outline(self.a.shape, l1), (x2, y_top))
            end_x, end_y = nearest(
                points_on_outline(self.a.shape, l2), (x2, y_bot))
            mid_x, mid_y = start_x + 10, (start_y + end_y) / 2.0
            shape.moveTo(start_x, start_y)
            shape.lineTo(mid_x, mid_y)
            shape.lineTo(end_x, end_y)
        else:  # connect 'a' and 'b'
            ax1, ay1, ax2, ay2 = self.a.bounds
            bx1, by1, bx2, by2 = self.b.bounds
            ca_x, ca_y = (ax1 + ax2) / 2.0, (ay1 + ay2) / 2.0
            cb_x, cb_y = (bx1 + bx2) / 2.0, (by1 + by2) / 2.0
            if (ca_x, ca_y) == (cb_x, cb_y):  # elems' centers are same point
                ca_x += 1  # nudge one a bit to be able to create a line
            line = ca_x, ca_y, cb_x, cb_y
            # find the points that are nearer to the opposite element's center
            start_x, start_y = nearest(
                points_on_outline(self.a.shape, line), (cb_x, cb_y))
            end_x, end_y = nearest(
                points_on_outline(self.b.shape, line), (ca_x, ca_y))
            shape.moveTo(start_x, start_y)
            shape.lineTo(end_x, end_y)
        return shape



from jarray import zeros
from java.awt.geom import PathIterator


def iterpath(shape):
    """Python iterator for shape.getPathIterator"""
    #piter = awt.geom.FlatteningPathIterator(shape.getPathIterator(None), 3)
    piter = shape.getPathIterator(None, PATH_PRECISION)
    arr = zeros(6, 'd')
    while not piter.isDone():
        kind = piter.currentSegment(arr)
        yield (kind,) + tuple(arr)
        piter.next()


def outline(shape):
    """Returns shape outline as list of line segment tuples."""
    def to_segments(acc, next_seg):
        segs, prev_x, prev_y = acc
        kind, x, y, _, _, _, _ = next_seg
        if kind == PathIterator.SEG_LINETO:
            return (segs + [(prev_x, prev_y, x, y)], x, y)
        if kind in [PathIterator.SEG_MOVETO, PathIterator.SEG_CLOSE]:
            return (segs, x, y)
        assert False, "bezier curves not supported"
    segs, _, _ = reduce(to_segments, iterpath(shape), ([], 0, 0))
    return segs


def points_on_outline(shape, line):
    """Returns intersection points of line and shape's outline."""
    return filter(None, [line_segment_intersection(line, seg)
                         for seg in outline(shape)])


def dist_sq(point_a, point_b):
    ax, ay = point_a
    bx, by = point_b
    dx, dy = bx - ax, by - ay
    return dx * dx + dy * dy


def nearest(points, target_point):
    zipped = zip(points, [dist_sq(p, target_point) for p in points])
    return sorted(zipped, key=lambda tup: tup[1])[0][0]


def line_intersection(line_a, line_b):
    """ Returns point of intersection of two lines as a tuple (int_x, int_y),
        or None if parallel or coincident.

        Parameters
        ----------
        line_a : tuple
            4-tuple representing first line's x1, y1, x2 and y2
        line_b : tuple
            4-tuple representing second line's x1, y1, x2 and y2

        Returns
        -------
        intersection : tuple or None
            2-tuple (intersection_x, intersection_y) if lines intersect, or
            None if lines are parallel or coincident.
    """
    x1, y1, x2, y2 = line_a
    x3, y3, x4, y4 = line_b
    denom = float((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if denom == 0.0:  # lines are parallel or coincident
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    return (x1 + ua * (x2 - x1), y1 + ua * (y2 - y1))


def segment_intersection(seg_a, seg_b):
    """ Returns point of intersection of two line segments as a tuple
        (int_x, int_y), or None if parallel, coincident or don't intersect.

        Parameters
        ----------
        seg_a : tuple
            4-tuple representing first seg's x1, y1, x2 and y2
        seg_b : tuple
            4-tuple representing second seg's x1, y1, x2 and y2

        Returns
        -------
        intersection : tuple or None
            2-tuple (intersection_x, intersection_y) if segs intersect, or
            None if segs are parallel, coincident or don't intersect.
    """
    x1, y1, x2, y2 = seg_a
    x3, y3, x4, y4 = seg_b
    denom = float((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if denom == 0.0:  # segs are parallel or coincident
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ua >= 0.0 and ua <= 1.0 and ub >= 0.0 and ub <= 1.0:
        return (x1 + ua * (x2 - x1), y1 + ua * (y2 - y1))


def line_segment_intersection(line, seg):
    x1, y1, x2, y2 = line
    x3, y3, x4, y4 = seg
    denom = float((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    if denom == 0.0:  # parallel or coincident
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ub >= 0.0 and ub <= 1.0:
        return (x1 + ua * (x2 - x1), y1 + ua * (y2 - y1))

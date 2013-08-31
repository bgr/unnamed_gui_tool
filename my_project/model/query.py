from quadpy.quadtree import fits, overlaps


# TODO: switch to quadtree completely



class CanvasSimpleQuery(object):
    """Provides spatial queries on elements contained in CanvasModel."""

    def __init__(self, canvas_model):
        self.model = canvas_model

    def under(self, x, y):
        def is_under(el):
            el_x1, el_y1, el_x2, el_y2 = el.bounds
            return (el_x1 <= x <= el_x2) and (el_y1 <= y <= el_y2)

        res = filter(is_under, self.model._elems)
        return res

    def enclosed(self, x1, y1, x2, y2):
        def is_enclosed(el):
            return fits(el.bounds, (x1, y1, x2, y2))

        res = filter(is_enclosed, self.model._elems)
        return res

    def overlapped(self, x1, y1, x2, y2):
        def is_overlapped(el):
            return overlaps(el.bounds, (x1, y1, x2, y2))

        res = filter(is_overlapped, self.model._elems)
        return res

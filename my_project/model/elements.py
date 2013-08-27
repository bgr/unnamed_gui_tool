from ..util import Record, bounding_box_around_points



# model change elements

class _BaseChange(Record):
    keys = ('elem',)

    @classmethod
    def prepare(_, elem):
        assert isinstance(elem, _BaseElement), "must be valid element"


class Remove(_BaseChange):
    pass


class Insert(_BaseChange):
    pass


class Modify(_BaseChange):
    keys = ('modified',)

    @classmethod
    def prepare(cls, elem, modified):
        _BaseChange.prepare(elem)
        assert isinstance(modified, _BaseElement), "must be valid element"



# canvas elements

def fix_xywh(x, y, width, height):
    x, y, width, height = map(float, [x, y, width, height])
    if width < 0:
        x -= -width
        width = -width
    if height < 0:
        y -= -height
        height = -height
    return { 'x': x, 'y': y, 'width': width, 'height': height }


class _BaseElement(Record):
    pass


class Rectangle(_BaseElement):
    keys = ('x', 'y', 'width', 'height')

    @classmethod
    def prepare(cls, x, y, width, height):
        return fix_xywh(x, y, width, height)

    @property
    def bounds(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class Ellipse(_BaseElement):
    keys = ('x', 'y', 'width', 'height')

    @classmethod
    def prepare(cls, x, y, width, height):
        return fix_xywh(x, y, width, height)

    @property
    def bounds(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class Path(_BaseElement):
    keys = ('vertices',)
    # TODO: prepare

    @property
    def bounds(self):
        return bounding_box_around_points(self.vertices)


#class Polygon(_BaseElement):
    #keys = ('vertices',)

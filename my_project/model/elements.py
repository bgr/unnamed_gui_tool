from ..util import Record, bounding_box_around_points, remove_duplicates



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
    def children(self):
        """Declare '_children' key and override this method where needed."""
        return tuple([])

    @property
    def bounds(self):
        raise NotImplementedError("Forgot to implement 'bounds' property")

    def move(self, dx, dy):
        raise NotImplementedError("Forgot to implement 'move' method")


class Rectangle(_BaseElement):
    keys = ('x', 'y', 'width', 'height')

    @classmethod
    def prepare(cls, x, y, width, height):
        return fix_xywh(x, y, width, height)

    @property
    def bounds(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def move(self, dx, dy):
        return Rectangle(self.x + dx, self.y + dy, self.width, self.height)


class Ellipse(_BaseElement):
    keys = ('x', 'y', 'width', 'height')

    @classmethod
    def prepare(cls, x, y, width, height):
        return fix_xywh(x, y, width, height)

    @property
    def bounds(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def move(self, dx, dy):
        return Ellipse(self.x + dx, self.y + dy, self.width, self.height)


class Path(_BaseElement):
    keys = ('vertices',)

    @classmethod
    def prepare(cls, vertices):
        fixed_verts = tuple(remove_duplicates(vertices))
        return {'vertices': fixed_verts }

    @property
    def bounds(self):
        return bounding_box_around_points(self.vertices)

    def move(self, dx, dy):
        return Path(tuple((vx + dx, vy + dy) for vx, vy in self.vertices))

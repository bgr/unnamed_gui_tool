from ..util import Record, bounding_box_around_points, remove_duplicates



# model change elements

class _BaseChange(Record):
    def __init__(self, elem):
        assert isinstance(elem, _BaseElement), "must be valid element"
        self.elem = elem


class Remove(_BaseChange):
    pass


class Insert(_BaseChange):
    pass


class Modify(_BaseChange):
    def __init__(self, elem, modified):
        super(Modify, self).__init__(elem)
        assert isinstance(modified, _BaseElement), "must be valid element"
        self.modified = modified



# canvas elements

def fix_xywh(x, y, width, height):
    x, y, width, height = map(float, [x, y, width, height])
    if width == 0 and height == 0:
        raise ValueError("Cannot have zero dimensions")
    if width < 0:
        x -= -width
        width = -width
    if height < 0:
        y -= -height
        height = -height
    return x, y, width, height


class _BaseElement(Record):
    def __init__(self, parent=None):
        if parent and (not isinstance(parent, _BaseElement)
                       or isinstance(parent, Link)):
            raise ValueError("parent must be element (but not Link) or None")
        self.parent = parent
        # TODO: parent must be member of same model, but this check has to
        # be performed elsewhere

    def move(self, dx, dy):
        raise NotImplementedError("Forgot to implement 'move' method")



class Link(_BaseElement):
    def __init__(self, a, b):
        assert isinstance(a, _BaseElement) and not isinstance(a, Link)
        assert isinstance(b, _BaseElement) and not isinstance(b, Link)
        self.a = a
        self.b = b
        super(Link, self).__init__(None)  # Link never has parent


class Rectangle(_BaseElement):
    def __init__(self, x, y, width, height, parent=None):
        self.x, self.y, self.width, self.height = fix_xywh(x, y, width, height)
        super(Rectangle, self).__init__(parent)

    def move(self, dx, dy):
        return self._replace(x=self.x + dx, y=self.y + dy)


class Ellipse(_BaseElement):
    def __init__(self, x, y, width, height, parent=None):
        self.x, self.y, self.width, self.height = fix_xywh(x, y, width, height)
        super(Ellipse, self).__init__(parent)

    def move(self, dx, dy):
        return self._replace(x=self.x + dx, y=self.y + dy)


class Path(_BaseElement):
    def __init__(self, vertices, parent=None):
        self.vertices = tuple(remove_duplicates(vertices))
        super(Path, self).__init__(parent)

    def move(self, dx, dy):
        new_verts = tuple((vx + dx, vy + dy) for vx, vy in self.vertices)
        return self._replace(vertices=new_verts)

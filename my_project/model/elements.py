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
    if width < 0:
        x -= -width
        width = -width
    if height < 0:
        y -= -height
        height = -height
    return x, y, width, height


class _BaseElement(Record):
    def __init__(self, parent=None):
        if parent and not isinstance(parent, _BaseElement):
            raise ValueError("parent must be element or None")
        self.parent = parent
        #if any(not isinstance(ch, _BaseElement) for ch in children):
            #raise ValueError("children must be elements")
        # TODO: parent must be member of same model, but this check has to
        # be performed elsewhere

    @property
    def bounds(self):
        raise NotImplementedError("Forgot to implement 'bounds' property")

    def move(self, dx, dy):
        raise NotImplementedError("Forgot to implement 'move' method")

    #def add_child(self, ch):
        #raise TypeError("Not a container")

    #def remove_child(self, ch):
        #raise TypeError("Not a container")

    #def change(self, **kwargs):
        #"""Returns changelist with updates for self and all parents."""
        #new = self.replace(**kwargs)
        ## update all parents up to root to point to freshly updated elements
        #more = []
        #if self.parent:
            #parents_children = list(self.parent.children)
            #parents_children[parents_children.index(self)] = new
            #more = self.parent.change(children=tuple(parents_children))
        #return more + [Modify(self, new)]



class Link(_BaseElement):
    def __init__(self, a, b):
        assert isinstance(a, _BaseElement) and not isinstance(a, Link)
        assert isinstance(b, _BaseElement) and not isinstance(a, Link)
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

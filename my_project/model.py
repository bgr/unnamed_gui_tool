from collections import namedtuple as _n

# model elements
Rectangle = _n('Rectangle', 'x, y, width, height')
Circle = _n('Circle', 'x, y, radius')
Line = _n('Line', 'x1, y1, x2, y2')

# events
Element_selected = 'Element_selected'
Element_deleted = 'Element_deleted'
Element_added = 'Element_added'
Elements_changed = 'Elements_changed'
Add_element = 'Add_element'
Delete_element = 'Delete_element'
Select_element = 'Select_element'


class PaintingModel(object):
    def __init__(self, eventbus):
        self.eb = eventbus
        self._elems = []
        self.selected_elem = None

    def select(self, elem):
        assert elem in self._elems
        self.selected_elem = elem
        self.eb.dispatch(Element_selected, elem)

    def delete(self, elem):
        assert elem in self._elems
        self._elems.remove(elem)
        self.eb.dispatch(Element_deleted, elem)

    def add(self, elem):
        self._elems.append(elem)
        self.eb.dispatch(Element_added, elem)

    @property
    def elems(self):
        return self._elems[:]

    @elems.setter
    def elems(self, new_elems):
        self._elems = new_elems
        self.eb.dispatch(Elements_changed, self.elems)

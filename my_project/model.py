from collections import namedtuple as _n

# model elements
Rectangle = _n('Rectangle', 'x, y, width, height')
Circle = _n('Circle', 'x, y, radius')
Line = _n('Line', 'x1, y1, x2, y2')

# events
Element_Selected = 'Element_Selected'
Element_Deleted = 'Element_Deleted'
Element_Added = 'Element_Added'
Add_element = 'Add_element'
Delete_element = 'Delete_element'
Select_element = 'Select_element'


class PaintingModel(object):
    def __init__(self, eventbus):
        self.eb = eventbus
        self.elems = []
        self.selected_elem = None

    def select(self, elem):
        assert elem in self.elems
        self.selected_elem = elem
        self.eb.dispatch(Element_Selected, elem)

    def delete(self, elem):
        assert elem in self.elems
        self.elems.remove(elem)
        self.eb.dispatch(Element_Deleted, elem)

    def add(self, elem):
        self.elems.append(elem)
        self.eb.dispatch(Element_Added, elem)

    def get_all_elems(self):
        return self.elems[:]

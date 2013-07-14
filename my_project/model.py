from collections import namedtuple as _n
import logging

_log = logging.getLogger(__name__)

# model elements
Rectangle = _n('Rectangle', 'x, y, width, height')
Circle = _n('Circle', 'x, y, radius')
Line = _n('Line', 'x1, y1, x2, y2')


from events import (Commit_To_Model, Model_Addition, Model_Selection,
                    Model_Deletion, Model_Cleared, Model_Changed)


class PaintingModel(object):
    def __init__(self, eventbus):
        self.eb = eventbus
        self._elems = []
        self.selected_elem = None
        self.eb.register(Commit_To_Model, self.add)

    def select(self, evt):
        elem = evt.data
        assert elem in self._elems
        self.selected_elem = elem
        self.eb.dispatch(Model_Selection(elem))

    def delete(self, evt):
        elem = evt.data
        assert elem in self._elems
        self._elems.remove(elem)
        self.eb.dispatch(Model_Deletion(elem))

    def add(self, evt):
        try:
            elem = check(evt.data)
        except ValueError:
            return
        _log.info('model says I got {0}'.format(elem))
        self._elems.append(elem)
        self.eb.dispatch(Model_Changed(elem))

    @property
    def elems(self):
        return self._elems[:]

    @elems.setter
    def elems(self, new_elems):
        self._elems = []
        self.eb.dispatch(Model_Cleared())
        self._elems = new_elems
        self.eb.dispatch(Model_Addition(new_elems))


def check(elem):
    if elem.width == 0 or elem.height == 0:
        raise ValueError("Element with no dimensions: {0}".format(elem))

    x, y, w, h = elem
    if elem.width < 0:
        x -= -elem.width
        w = -elem.width
    if elem.height < 0:
        y -= -elem.height
        h = -elem.height
    return elem._make((x, y, w, h))

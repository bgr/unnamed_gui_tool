from collections import namedtuple
import logging

from events import Commit_To_Model, Model_Changed

_log = logging.getLogger(__name__)


Change = namedtuple('Change', 'old, new')


# model elements

class BaseElement(namedtuple('BaseElement', 'x, y, width, height')):
    def __repr__(self):
        return '{0}(x={1}, y={2}, width={3}, height={4})'.format(
            self.__class__.__name__, self.x, self.y, self.width, self.height)


class Rectangle(BaseElement):
    pass


class Circle(BaseElement):
    pass


class Line(BaseElement):
    pass



class PaintingModel(object):
    def __init__(self, eventbus):
        self._elems = []
        self.changelog
        self.eb = eventbus
        # call 'commit' and pass event.data as changelist
        self.eb.register(Commit_To_Model, lambda evt: self.commit(evt.data))


    @property
    def elems(self):
        """
            Returns list of all elements in model.

            Modifications of the list will be ignored since this method will
            return a copy of the list - changes have to be done through
            *commit* method by submitting a changelist.
        """
        return self._elems[:]

    @elems.setter
    def elems(self, new_elems):
        """
            Clears the model and sets new elements.

            Model will create a changelist containing both old (removed) and
            new elements and inform listeners with it.
        """
        # make a changelist with elements to be removed
        old_changes = (Change(old, None) for old in self._elems)
        new_changes = (Change(None, el) for el in new_elems)
        self.commit(old_changes + new_changes)


def commit(changes, changelog, eb, elems):
    """Performs the changes to model's elements and informs listeners."""
    _log.info('Model got changelist {0}'.format(changelist))

    # validate the changelist
    changes = validate(changes, elems)

    to_remove = (old for old, new in changes
                 if old is not None and new is None)
    to_insert = (old for old, new in changes
                 if old is None and new is not None)
    to_change = (ch for ch in changes if ch.old != ch.new)

    for el in to_remove:
        elems.remove(el)

    for old, new in to_change:
        elems[elems.index(old)] = new

    elems += to_insert

    changelog += [changes]  # add the list altogether, not just elements
    eb.dispatch(Model_Changed(changelist))


def validate(changelist, existing):
    validated = []
    for old, new in changelist:
        if old is None and new is None:
            raise ValueError("Invalid change, *old* and *new* "
                             "cannot both be None")
        if old is not None and not old in existing:
            raise ValueError("Invalid change, *old* refers to "
                             "element that isn't in model")
        if new is not None:
            new = fix(new)

        change = Change(old, new)
        # skip elements without change and elements identical to existing
        # and don't allow duplicates that might be in changelist itself
        if old != new and new not in existing and change not in validated:
            validated += [change]
    return validated


def fix(elem):
    if elem.width == 0 or elem.height == 0:
        raise ValueError("Element with no dimensions: {0}".format(elem))

    x, y, w, h = elem
    if elem.width < 0:
        x -= -elem.width
        w = -elem.width
    if elem.height < 0:
        y -= -elem.height
        h = -elem.height
    new_elem = elem._make((x, y, w, h))
    _log.info("Model fixed element {0} into {1}".format(elem, new_elem))
    return new_elem

import logging
from collections import namedtuple

from util import duplicates
from events import Commit_To_Model, Model_Changed

_log = logging.getLogger(__name__)


Change = namedtuple('Change', 'old, new')
Insert = namedtuple('Insert', 'elem')
Remove = namedtuple('Remove', 'elem')


# model elements

class BaseElement(namedtuple('BaseElement', 'x, y, width, height')):
    def __init__(self, x, y, width, height):
        if width == 0 or height == 0:
            raise ValueError("Dimensions cannot be 0")
        if width < 0:
            x -= -width
            width = -width
        if height < 0:
            y -= -height
            height = -height
        #float_args = map(float, [x, y, width, height])
        super(self.__class__, self).__init__(x, y, width, height)

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
    _log.info('Model got changelist {0}'.format(changes))

    parsed = parse(changes, elems)
    to_remove, to_change, to_insert = parsed

    for el in to_remove:
        elems.remove(el)

    for old, new in to_change:
        elems[elems.index(old)] = new

    elems += to_insert

    changelog += [parsed]  # add the list altogether, not just elements
    eb.dispatch(Model_Changed(parsed[:]))  # listeners get a copy


def parse(changelist, existing):
    """
        Validates changes in changelist and returns tuple:
            (validated_changelist, elems_to_remove, changed_elems, new_elems)
    """
    if not all(isinstance(c, (Change, Remove, Insert)) for c in changelist):
        raise ValueError("Invalid changes in changelist")

    to_remove = filter(lambda ch: isinstance(ch, Remove), changelist)
    to_change = filter(lambda ch: isinstance(ch, Change), changelist)
    to_insert = filter(lambda ch: isinstance(ch, Insert), changelist)

    is_elem = lambda el: isinstance(el, BaseElement)
    change_ok = lambda ch: is_elem(ch.old) and is_elem(ch.new)

    if not (all(is_elem(el) for el in to_remove + to_insert)
            and all(change_ok(c) for c in to_change)):
        raise ValueError("Changes with invalid elements in changelist")

    # element have valid types at this point
    # now validate element values

    olds = [ch.old for ch in to_change]
    news = [ch.new for ch in to_change]
    if not all(old in existing for old in olds):
        raise ValueError("Changing element that's not in the model")
    if not all(el in existing for el in to_remove):
        raise ValueError("Removing element that's not in the model")
    if any(new in existing for new in news):
        raise ValueError("Changing into element that's already in model")
    if any(el in existing for el in to_insert):
        raise ValueError("Inserting element already present in the model")

    if duplicates(to_remove):
        raise ValueError("Removing same element multiple times")
    if duplicates(to_change):
        raise ValueError("Changing same element multiple times")
    if duplicates(to_insert):
        raise ValueError("Inserting same element multiple times")
    if duplicates(to_remove + to_insert):
        raise ValueError("Removing and inserting same element")
    if duplicates(to_remove + olds + news):
        raise ValueError("Removing and changing same element")
    if duplicates(to_insert + olds + news):
        raise ValueError("Changing and inserting identical elements")

    # everything ok
    return (to_remove, to_change, to_insert)


#def fix(elem):
    #if elem.width == 0 or elem.height == 0:
        #raise ValueError("Element with no dimensions: {0}".format(elem))

    #x, y, w, h = elem
    #if elem.width < 0:
        #x -= -elem.width
        #w = -elem.width
    #if elem.height < 0:
        #y -= -elem.height
        #h = -elem.height
    #new_elem = elem._make((x, y, w, h))
    #_log.info("Model fixed element {0} into {1}".format(elem, new_elem))
    #return new_elem

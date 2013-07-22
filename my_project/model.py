import logging

from util import duplicates, Record
from events import Commit_To_Model, Model_Changed

_log = logging.getLogger(__name__)


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


# model elements

class _BaseElement(Record):
    keys = ('x', 'y', 'width', 'height')

    @classmethod
    def prepare(cls, x, y, width, height):
        x, y, width, height = map(float, [x, y, width, height])
        if width == 0 or height == 0:
            raise ValueError("Dimensions cannot be 0")
        if width < 0:
            x -= -width
            width = -width
        if height < 0:
            y -= -height
            height = -height
        return dict(zip(cls.keys, [x, y, width, height]))


class Rectangle(_BaseElement):
    pass


class Ellipse(_BaseElement):
    pass


class Line(_BaseElement):
    pass


class Polyline(_BaseElement):
    keys = ('segments',)


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
        old_changes = (Remove(old) for old in self._elems)
        new_changes = (Insert(new) for new in new_elems)
        self.commit(old_changes + new_changes)


def commit(changes, changelog, eb, elems):
    """Performs the changes to model's elements and informs listeners."""
    _log.info('Model got changelist {0}'.format(changes))

    parsed = parse(changes, elems)
    to_remove, to_change, to_insert = parsed

    for ch in to_remove:
        elems.remove(ch.elem)

    for old, new in to_change:
        elems[elems.index(old)] = new

    elems += [ch.elem for ch in to_insert]

    # changelog items are lists of elements, wrap in additional list and append
    log_item = [to_remove + to_change + to_insert]
    changelog += log_item
    eb.dispatch(Model_Changed(log_item))


def parse(changelist, existing):
    """
        Validates changes in changelist and returns tuple:
            (validated_changelist, elems_to_remove, changed_elems, new_elems)
    """
    if not all(isinstance(c, (Modify, Remove, Insert)) for c in changelist):
        raise ValueError("Invalid changes in changelist")

    to_remove = filter(lambda ch: isinstance(ch, Remove), changelist)
    to_modify = filter(lambda ch: isinstance(ch, Modify), changelist)
    to_insert = filter(lambda ch: isinstance(ch, Insert), changelist)

    is_elem = lambda el: isinstance(el, _BaseElement)

    if not (all(is_elem(c.elem) for c in to_remove + to_insert) and
            all(is_elem(m.elem) and is_elem(m.modified) for m in to_modify)):
        raise ValueError("Changes with invalid elements in changelist")

    # element have valid types at this point
    # now validate element values

    elems_old = [m.elem for m in to_modify]
    elems_new = [m.modified for m in to_modify]
    elems_rmd = [r.elem for r in to_remove]
    elems_ins = [i.elem for i in to_insert]
    if not all(el in existing for el in elems_old):
        raise ValueError("Changing element that's not in the model")
    if not all(el in existing for el in elems_rmd):
        raise ValueError("Removing element that's not in the model")
    if any(el in existing for el in elems_new):
        raise ValueError("Changing into element that's already in model")
    if any(el in existing for el in elems_ins):
        raise ValueError("Inserting element already present in the model")

    if duplicates(elems_rmd):
        raise ValueError("Removing same element multiple times")
    if duplicates(elems_old + elems_new):
        raise ValueError("Modifying same element multiple times")
    if duplicates(elems_ins):
        raise ValueError("Inserting same element multiple times")
    if duplicates(elems_rmd + elems_ins):
        raise ValueError("Removing and inserting same element")
    if duplicates(elems_rmd + elems_old + elems_new):
        raise ValueError("Removing and changing same element")
    if duplicates(elems_ins + elems_old + elems_new):
        raise ValueError("Changing and inserting identical elements")

    # everything ok
    return (to_remove, to_modify, to_insert)


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

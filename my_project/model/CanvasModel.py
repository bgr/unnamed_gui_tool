import logging
_log = logging.getLogger(__name__)

from ..util import duplicates
from ..events import Model_Changed
from elements import Remove, Insert, Modify, _BaseElement, Link
from query import CanvasSimpleQuery as CanvasQuery



class CanvasModel(object):
    def __init__(self, eventbus):
        self._elems = []
        self._changelog = []
        self._eb = eventbus
        self._query = CanvasQuery(self)

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
        old_changes = [Remove(old) for old in self._elems]
        new_changes = [Insert(new) for new in new_elems]
        self.commit(old_changes + new_changes)

    def commit(self, changes):
        _log.info('Model got changelist {0}'.format(
            ''.join(['\n * ' + str(ch) for ch in changes])))

        _commit(changes, self._changelog, self._eb, self._elems)

    @property
    def query(self):
        return self._query




def _commit(changes, changelog, eb, elems):
    """Performs the changes to model's elements and informs listeners."""
    validate(changes, elems)

    for ch in changes:
        if isinstance(ch, Remove):
            elems.remove(ch.elem)
        elif isinstance(ch, Insert):
            elems += [ch.elem]
        elif isinstance(ch, Modify):
            old, new = ch
            elems[elems.index(old)] = new
        else:
            assert False, "this cannot happen"

    # changelog items are lists of changes, wrap in additional list
    changelog += [changes[:]]
    eb.dispatch(Model_Changed(changes[:]))



def validate(changelist, existing):
    """
        Validates changes in changelist. Raises ValueError if something's not
        valid, otherwise returns None.
    """
    if not changelist:
        raise ValueError("Empty changelist")

    if not all(isinstance(c, (Modify, Remove, Insert)) for c in changelist):
        raise ValueError("Invalid changes in changelist")

    cls = changelist[0].__class__
    if not all(isinstance(c, cls) for c in changelist):
        raise ValueError("Mixed change types not allowed in same changelist")

    # TODO: simplify code below now that mixed changes are not allowed

    to_remove = filter(lambda ch: isinstance(ch, Remove), changelist)
    to_modify = filter(lambda ch: isinstance(ch, Modify), changelist)
    to_insert = filter(lambda ch: isinstance(ch, Insert), changelist)

    is_elem = lambda el: isinstance(el, _BaseElement)

    if not (all(is_elem(c.elem) for c in to_remove + to_insert) and
            all(is_elem(m.elem) and is_elem(m.modified) for m in to_modify)):
        raise ValueError("Changes with invalid elements in changelist")

    # element have valid types at this point
    # now validate element values

    if any(m.elem == m.modified for m in to_modify):
        raise ValueError("Modifying without actual changes")

    elems_old = [m.elem for m in to_modify]
    elems_mod = [m.modified for m in to_modify]
    elems_rmv = [r.elem for r in to_remove]
    elems_ins = [i.elem for i in to_insert]
    if not all(el in existing for el in elems_old):
        raise ValueError("Changing element that's not in the model")
    if not all(el in existing for el in elems_rmv):
        raise ValueError("Removing element that's not in the model")
    if any(el in existing for el in elems_mod):
        raise ValueError("Changing into element that's already in model")
    if any(el in existing for el in elems_ins):
        raise ValueError("Inserting element already present in the model")

    if duplicates(elems_rmv):
        raise ValueError("Removing same element multiple times")
    if duplicates(elems_old + elems_mod):
        raise ValueError("Modifying same element multiple times")
    if duplicates(elems_ins):
        raise ValueError("Inserting same element multiple times")
    if duplicates(elems_rmv + elems_ins):
        raise ValueError("Removing and inserting same element")
    if duplicates(elems_rmv + elems_old + elems_mod):
        raise ValueError("Removing and changing same element")
    if duplicates(elems_ins + elems_old + elems_mod):
        raise ValueError("Changing and inserting identical elements")

    if any(len(el.bounds) != 4 for el in elems_mod + elems_ins):
        raise ValueError("Elements with invalid bounds tuple")
    if any(el.bounds[2:] == el.bounds[:2] for el in elems_mod + elems_ins
           if not isinstance(el, Link)):  # TODO: remove this
        # (x1, y1) == (x2, y2) where bounds is tuple (x1, y1, x2, y2)
        raise ValueError("Elements with 0 dimensions")

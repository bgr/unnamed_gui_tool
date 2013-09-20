import logging
_log = logging.getLogger(__name__)

from ..util import duplicates
from ..events import Model_Changed
from elements import Remove, Insert, Modify, _BaseElement, Link



class CanvasModel(object):
    def __init__(self, eventbus):
        self._elems = []
        self._changelog = []
        self._redolog = []
        self._eb = eventbus

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
        """ Updates elems, appends changes to changelog, clears redo log
            and notifies listeners.
        """
        _log.info('Model got changelist {0}'.format(
            ''.join(['\n * ' + str(ch) for ch in changes])))

        if not changes:  # skip empty changelist
            return

        _commit(changes, self._changelog, self._eb, self._elems)
        self._redolog = []


    def move(self, what, dx, dy):
        """ Move element(s) by given offset. Doesn't commit!
            Returns changelist that has to be committed manually.
        """
        return _move(what, dx, dy, self._elems)

    def undo(self):
        _undo(self._changelog, self._redolog, self._eb, self._elems)

    def redo(self):
        _redo(self._changelog, self._redolog, self._eb, self._elems)



def _update_model_elements(changes, model_elements):
    """Modifies model elements list according to given changes."""
    # TODO: maybe move to each element
    for ch in changes:
        if isinstance(ch, Remove):
            model_elements.remove(ch.elem)
        elif isinstance(ch, Insert):
            model_elements += [ch.elem]
        elif isinstance(ch, Modify):
            model_elements[model_elements.index(ch.elem)] = ch.modified
        else:
            assert False, "this cannot happen"


def _commit(changes, changelog, eb, existing):
    """ Validates the changes and commits them to model, changing model elems.

        Commit performs following actions:
          * validates the given changes
          * appends changes to changelog
          * updates model elems
          * notifies listeners about the changed elements

        Parameters
        ----------
        changes : list
            list of changes to be committed
        changelog : list
            list to append changes to
        eb : EventBus
            event bus on which to dispatch Model_Changed event
        existing : list
            elements currently in the model, used for validating

        Returns
        -------
        None

        Raises
        ------
        ValueError if validation fails
    """
    _validate(changes, existing)

    _update_model_elements(changes, existing)

    # changelog items are lists of changes, wrap in additional list
    changelog += [changes[:]]
    eb.dispatch(Model_Changed(changes[:]))


def _invert(changelist):
    """Returns new list with inverted changes from given changelist."""
    return [ch.inverse for ch in changelist]


def _undo(change_log, redo_log, eb, existing):
    """ Undoes last changelist in change_log, removes it from change_log and
        prepends it to redo_log, and notifies the listeners.
    """
    if not change_log:
        return  # nothing to do

    cl = change_log.pop()
    redo_log.insert(0, cl)
    undo_cl = _invert(cl)
    _update_model_elements(undo_cl, existing)
    eb.dispatch(Model_Changed(undo_cl))


def _redo(change_log, redo_log, eb, existing):
    """ Redoes first changelist in redo_log, pops it from redo_log and appends
        it to change_log, and notifies the listeners.
    """
    if not redo_log:
        return  # nothing to do

    cl = redo_log.pop(0)
    change_log.append(cl)
    _update_model_elements(cl, existing)
    eb.dispatch(Model_Changed(cl[:]))


def _move(what, dx, dy, existing):
    """ Returns changelist that'll cause elements to be moved when committed.

        Note that number of changed elements might be larger than number of
        elements requested to be moved, e.g. when moving linked element, link
        will be changed also, or when moving an element that contains children
        elements, all of the children (and grandchildren) will be changed also.

        Parameters
        ----------
        what : _BaseElement or list of _BaseElements
            element or elements to move
        dx : Number
            horizontal offset by which to move element(s)
        dy : Number
            vertical offset by which to move element(s)

        existing : list/set
            elements currently in model, needed for finding children and links

        Returns
        -------
        changelist : list
            list of Modify instanced

        Raises
        ------
        ValueError if 'what' is not in 'existing'
    """
    if isinstance(what, _BaseElement):
        what = [what]
    what = [el for el in what if not isinstance(el, Link)]  # exclude links

    is_elem = lambda e: isinstance(e, _BaseElement) and not isinstance(e, Link)
    assert all(is_elem(el) for el in what), "elements only (but not links)"

    def get_parents(el):
        if el.parent is None:
            return []
        return [el.parent] + get_parents(el.parent)

    # TODO: slow and wasteful, optimize
    def get_children(par):
        #return [el for el in existing if par in get_parents(el)]
        return [el for el in existing if el.parent == par]

    # children won't be moved, just updated to point to new parents
    # roots will have updated coordinates, and their children updated
    parent_also_moved = lambda el: any(p in what for p in get_parents(el))
    roots = [el for el in what if not parent_also_moved(el)]

    def update_children(old_parent, new_parent):
        orig_ch = get_children(old_parent)
        ch_pairs = [(ch, ch._replace(parent=new_parent)) for ch in orig_ch]
        gr_pairs = [g for o, n in ch_pairs for g in update_children(o, n)]
        return ch_pairs + gr_pairs  # children and grandchildren pairs

    roots = [(r, r.move(dx, dy)) for r in roots]
    children = [pair for o, n in roots for pair in update_children(o, n)]
    all_elems = roots + children
    all_elems_dict = dict(all_elems)
    orig_elems = all_elems_dict.keys()

    def updated_link(lnk):
        a = lnk.a in orig_elems
        b = lnk.b in orig_elems
        if a and b:
            return lnk._replace(a=all_elems_dict[lnk.a],
                                b=all_elems_dict[lnk.b])
        elif a:
            return lnk._replace(a=all_elems_dict[lnk.a])
        elif b:
            return lnk._replace(b=all_elems_dict[lnk.b])
        return None

    links = [(l, updated_link(l)) for l in existing if isinstance(l, Link)]
    links = [pair for pair in links if pair[1] is not None]

    return [Modify(old, new) for old, new in all_elems + links]



def _validate(changelist, existing):
    """ Validates changes in changelist.

        Parameters
        ----------
        changelist : list/tuple/set
            list of changes, all must be of same type
        existing : list/tuple/set
            elements currently in model

        Returns
        -------
        None

        Raises
        ------
        ValueError if something's not valid
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

    is_elem = lambda e: isinstance(e, _BaseElement)

    if not (all(is_elem(c.elem) for c in to_remove + to_insert) and
            all(is_elem(m.elem) and is_elem(m.modified) for m in to_modify)):
        raise ValueError("Changes with invalid elements in changelist")

    # element have valid types at this point
    # now validate element values

    is_elem = lambda e: isinstance(e, _BaseElement) and not isinstance(e, Link)

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

    elems_cur = elems_ins + elems_old + elems_rmv

    parent_ok = lambda e: e.parent is None or (e.parent in existing
                                               and is_elem(e.parent))
    if not all(parent_ok(el) for el in elems_cur + elems_mod):
        raise ValueError("Element's parent must be member of same model")

    ins_links = [l for l in elems_ins if isinstance(l, Link)]
    if not all(l.a in existing and l.b in existing for l in ins_links):
        raise ValueError("Link's targets must be member of same model")

    mod_links = [l for l in elems_mod if isinstance(l, Link)]
    valid_target = lambda t: t in elems_mod or t in existing
    if not all(valid_target(l.a) and valid_target(l.b) for l in mod_links):
        raise ValueError("Modified link's targets must be in same model")

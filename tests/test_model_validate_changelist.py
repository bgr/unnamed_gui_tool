import pytest
from my_project.model.elements import Rectangle as R
from my_project.model.elements import Link
from my_project.model import Remove, Modify, Insert
from my_project.model.CanvasModel import validate



elems = [
    R(10, 10, 100, 100),
    R(20, 20, 200, 200),
    R(30, 30, 300, 300),
]

elems += [
    Link(elems[0], elems[1]),
    Link(elems[1], elems[1]),
]


def test_allows_new_elements():
    cl = [
        Insert(elem=R(44, 44, 444, 444)),
        Insert(R(55, 55, 555, 555)),
    ]
    validate(cl, elems)


def test_allows_modified_elements():
    cl = [
        Modify(R(30, 30, 300, 300), R(33, 33, 330, 330)),
        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
    ]
    validate(cl, elems)


def test_raises_on_modify_with_no_actual_changes():
    cl = [
        Modify(R(30, 30, 300, 300), R(30, 30, 300, 300)),
    ]
    with pytest.raises(ValueError) as err:
        validate(cl, elems)
    assert "Modifying without actual changes" in err.value.message


def test_allows_removing_elements():
    cl = [
        Remove(elem=R(30, 30, 300, 300)),
        Remove(R(20, 20, 200, 200)),
    ]
    validate(cl, elems)


@pytest.mark.parametrize('changelist', [
    [Remove(elems[0]), Insert(R(10, 5, -5, 5))],
    [Insert(R(10, 5, -5, 5)), Remove(elems[0])],
    [Insert(R(10, 5, -5, 5)), Modify(elems[0], R(100, 1100, 1000, 1000))],
    [Modify(elems[0], R(100, 1100, 1000, 1000)), Insert(R(10, 5, -5, 5))],
    [Remove(elems[1]), Modify(elems[0], R(100, 1100, 1000, 1000))],
    [Modify(elems[0], R(100, 1100, 1000, 1000)), Remove(elems[1])],
])
def test_raises_on_mixed_changes_in_same_changelist(changelist):
    with pytest.raises(ValueError) as err:
        validate(changelist, elems)
    assert "not allowed" in err.value.message


def test_raises_on_invalid_changelist_elements():
    with pytest.raises(ValueError) as err:
        validate([Insert(R(9, 9, 9, 9)), None], elems)
    assert 'Invalid change' in err.value.message
    with pytest.raises(ValueError) as err:
        validate([Insert(R(9, 9, 9, 9)), 2], elems)
    assert 'Invalid change' in err.value.message


def test_raises_when_inserting_same_as_existing():
    with pytest.raises(ValueError) as err:
        validate([Insert(R(30, 30, 300, 300))], elems)
    assert 'already present' in err.value.message


def test_raises_when_inserting_same_as_existing_with_fixing():
    with pytest.raises(ValueError) as err:
        validate([Insert(R(30, 330, 300, -300))], elems)
    assert 'already present' in err.value.message


def test_raises_when_modifying_old_not_in_existing():
    with pytest.raises(ValueError) as err:
        validate([Modify(R(9, 9, 9, 9), R(1, 1, 10, 10))], elems)
    assert "Changing element that's not in the model" in err.value.message


def test_raises_when_removing_old_not_in_existing():
    with pytest.raises(ValueError) as err:
        validate([Remove(R(9, 9, 9, 9))], elems)
    assert "Removing element that's not in the model" in err.value.message


def test_raises_on_duplicate_insertions():
    cl = [
        Insert(R(55, 610, 555, 555)),
        Insert(R(55, 610, 555, 555)),
    ]
    with pytest.raises(ValueError) as err:
        validate(cl, elems)
    assert 'Inserting same element' in err.value.message


def test_raises_on_duplicate_removals():
    cl = [
        Remove(R(10, 10, 100, 100)),
        Remove(R(10, 10, 100, 100)),
    ]
    with pytest.raises(ValueError) as err:
        validate(cl, elems)
    assert 'Removing same element' in err.value.message


def test_raises_on_zero_dimensions():
    validate([Insert(R(1, 1, 0, 1))], elems)  # allowed one to be 0
    validate([Insert(R(1, 1, 1, 0))], elems)
    validate([Modify(R(10, 10, 100, 100), R(10, 10, 0, 1))], elems)

    with pytest.raises(ValueError) as err:
        validate([Insert(R(1, 1, 0, 0))], elems)
    assert 'dimensions' in err.value.message

    with pytest.raises(ValueError) as err:
        validate([Modify(R(10, 10, 100, 100), R(10, 10, 0, 0))], elems)
    assert 'dimensions' in err.value.message


def test_allows_modified_link_with_targets_modified_in_same_changelist():
    el = elems[1]
    link1 = elems[-2]
    link2 = elems[-1]
    assert isinstance(el, R)
    assert isinstance(link1, Link)
    assert isinstance(link2, Link)
    assert link1.b == el
    assert link2.a == el and link2.b == el
    new_el = R(10, 11, 12, 13)
    new_link1 = Link(link1.a, new_el)
    new_link2 = Link(new_el, new_el)
    cl = [
        Modify(el, new_el),
        Modify(link1, new_link1),
        Modify(link2, new_link2),
    ]
    validate(cl, elems)


def test_raises_on_changelist_without_updated_links():
    # TODO
    # when modifying some element, and link exists which points to that same
    # element, changelist must contain modified link also

    # using same elements as in test above
    el = elems[1]
    link1 = elems[-2]
    link2 = elems[-1]
    new_el = R(10, 11, 12, 13)
    new_link1 = Link(link1.a, new_el)
    new_link2 = Link(new_el, new_el)

    with pytest.raises(ValueError) as err:
        validate([
            Modify(el, new_el),
        ], elems)
    assert "Incomplete" in err.value.message

    with pytest.raises(ValueError) as err:
        validate([
            Modify(el, new_el),
            Modify(link1, new_link1),
        ], elems)
    assert "Incomplete" in err.value.message

    with pytest.raises(ValueError) as err:
        validate([
            Modify(el, new_el),
            Modify(link2, new_link2),
        ], elems)
    assert "Incomplete" in err.value.message


@pytest.mark.parametrize('link', [
    Link(R(9, 9, 9, 9), elems[0]),
    Link(elems[0], R(9, 9, 9, 9)),
    Link(R(9, 9, 10, 10), R(9, 9, 9, 9)),
])
def test_raises_when_inserting_link_with_targets_not_in_existing(link):
    with pytest.raises(ValueError) as err:
        validate([Insert(link)], elems)
    assert "target" in err.value.message


@pytest.mark.parametrize('new', [
    Link(R(9, 9, 9, 9), elems[0]),
    Link(elems[0], R(9, 9, 9, 9)),
    Link(R(9, 9, 10, 10), R(9, 9, 9, 9)),
])
def test_raises_when_modifying_link_target_into_element_not_in_existing(new):
    old = Link(elems[0], elems[1])
    with pytest.raises(ValueError) as err:
        validate([Modify(old, new)], elems)
    assert "target" in err.value.message

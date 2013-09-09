import pytest
from my_project.model.elements import Rectangle as R
from my_project.model import Remove, Modify, Insert
from my_project.model.CanvasModel import _parse



elems = [
    R(10, 10, 100, 100),
    R(20, 20, 200, 200),
    R(30, 30, 300, 300),
]


def test_allows_new_elements():
    cl = [
        Insert(elem=R(44, 44, 444, 444)),
        Insert(R(55, 55, 555, 555)),
    ]
    rem, chg, ins = _parse(cl, elems)
    assert rem == []
    assert chg == []
    assert ins == [
        Insert(R(44, 44, 444, 444)),
        Insert(R(55, 55, 555, 555)),
    ]


def test_allows_changed_elements():
    cl = [
        Modify(R(30, 30, 300, 300), R(33, 33, 330, 330)),
        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
    ]
    rem, chg, ins = _parse(cl, elems)
    assert rem == []
    assert chg == [
        Modify(R(30, 30, 300, 300), R(33, 33, 330, 330)),
        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
    ]
    assert ins == []

# TODO raises error currently, might relax that rule in the future
#def test_excludes_elements_with_no_actual_changes():
#    cl = [
#        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
#        Modify(R(30, 30, 300, 300), R(30, 30, 300, 300)),
#        Modify(R(10, 10, 100, 100), R(10, 10, 111, 100)),
#    ]
#    rem, chg, ins = _parse(cl, elems)
#    assert rem == []
#    assert chg == [
#        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
#        Modify(R(10, 10, 100, 100), R(10, 10, 111, 100)),
#    ]
#    assert ins == []


def test_allows_removing_elements():
    cl = [
        Remove(elem=R(30, 30, 300, 300)),
        Remove(R(20, 20, 200, 200)),
    ]
    rem, chg, ins = _parse(cl, elems)
    assert rem == [
        Remove(R(30, 30, 300, 300)),
        Remove(R(20, 20, 200, 200)),
    ]
    assert chg == []
    assert ins == []


def test_mixed():
    cl = [
        Remove(R(30, 30, 300, 300)),
        Insert(R(10, 5, -5, 5)),  # fix
        Modify(R(10, 10, 100, 100), R(100, 1100, 1000, -1000)),  # fix
        Remove(R(20, 20, 200, 200)),
        Insert(R(4, 4, 4, 4)),
    ]
    rem, chg, ins = _parse(cl, elems)
    assert rem == [
        Remove(R(30, 30, 300, 300)),
        Remove(R(20, 20, 200, 200)),
    ]
    assert chg == [
        Modify(R(10, 10, 100, 100), R(100, 100, 1000, 1000))
    ]
    assert ins == [
        Insert(R(5, 5, 5, 5)),
        Insert(R(4, 4, 4, 4)),
    ]


def test_raises_on_invalid_changelist_elements():
    with pytest.raises(ValueError) as err:
        _parse([Insert(R(9, 9, 9, 9)), None], elems)
    assert 'Invalid change' in err.value.message
    with pytest.raises(ValueError) as err:
        _parse([Insert(R(9, 9, 9, 9)), 2], elems)
    assert 'Invalid change' in err.value.message


def test_raises_when_inserting_same_as_existing():
    with pytest.raises(ValueError) as err:
        _parse([Insert(R(30, 30, 300, 300))], elems)
    assert 'already present' in err.value.message


def test_raises_when_inserting_same_as_existing_with_fixing():
    with pytest.raises(ValueError) as err:
        _parse([Insert(R(30, 330, 300, -300))], elems)
    assert 'already present' in err.value.message


def test_raises_when_changing_old_not_in_existing():
    with pytest.raises(ValueError) as err:
        _parse([Modify(R(9, 9, 9, 9), R(1, 1, 10, 10))], elems)
    assert "Changing element that's not in the model" in err.value.message


def test_raises_when_removing_old_not_in_existing():
    with pytest.raises(ValueError) as err:
        _parse([Remove(R(9, 9, 9, 9))], elems)
    assert "Removing element that's not in the model" in err.value.message


def test_raises_on_duplicate_insertions():
    cl = [
        Insert(R(55, 610, 555, 555)),
        Insert(R(55, 610, 555, 555)),
    ]
    with pytest.raises(ValueError) as err:
        _parse(cl, elems)
    assert 'Inserting same element' in err.value.message


def test_raises_on_duplicate_removals():
    cl = [
        Remove(R(10, 10, 100, 100)),
        Remove(R(10, 10, 100, 100)),
    ]
    with pytest.raises(ValueError) as err:
        _parse(cl, elems)
    assert 'Removing same element' in err.value.message


def test_raises_on_zero_dimensions():
    _parse([Insert(R(1, 1, 0, 1))], elems)  # allowed one to be 0
    _parse([Insert(R(1, 1, 1, 0))], elems)
    _parse([Modify(R(10, 10, 100, 100), R(10, 10, 0, 1))], elems)

    with pytest.raises(ValueError) as err:
        _parse([Insert(R(1, 1, 0, 0))], elems)
    assert 'dimensions' in err.value.message

    with pytest.raises(ValueError) as err:
        _parse([Modify(R(10, 10, 100, 100), R(10, 10, 0, 0))], elems)
    assert 'dimensions' in err.value.message

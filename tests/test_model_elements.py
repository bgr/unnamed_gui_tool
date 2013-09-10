import pytest
from my_project.model.elements import Ellipse, Path, Rectangle
from my_project.model import Remove, Modify, Insert


# canvas elements: Rectangle, Ellipse and Path (will be changed in the future)

def test_Rectangle_properties():
    r = Rectangle(9, 10, 11, 12)
    assert r.x == 9
    assert r.y == 10
    assert r.width == 11
    assert r.height == 12


def test_can_compare_Rectangles():
    assert Rectangle(1, 2, 9, 9) == Rectangle(1, 2, 9, 9)
    assert Rectangle(1, 2, 9, 9) != Rectangle(2, 2, 9, 9)


def test_comparing_Rectangle_and_Ellipse_gives_False():
    assert Rectangle(1, 2, 9, 9) != Ellipse(1, 2, 9, 9)


def test_can_compare_Paths():
    p1 = Path([(1, 2), (3, 4), (5, 6)])
    p2 = Path([(1, 2), (3, 4), (5, 6)])
    p3 = Path([(1, 2), (3, 4), (5, 789)])
    assert p1 == p2
    assert p1 != p3


def test_Rectangle_raises_on_invalid_values():
    with pytest.raises(TypeError):
        Rectangle(None, 9, 9, 9)
    with pytest.raises(ValueError):
        Rectangle(9, 9, 'a', 9)


def test_Rectangle_fixes_negative_width():
    el = Rectangle(20, 30, -100, 40)
    assert el == Rectangle(-80, 30, 100, 40)


def test_Rectangle_fixes_negative_height():
    el = Rectangle(20, 30, 100, -40)
    assert el == Rectangle(20, -10, 100, 40)


def test_Rectangle_fixes_negative_both():
    el = Rectangle(20, 30, -100, -40)
    assert el == Rectangle(-80, -10, 100, 40)


# TODO: test real elements that will be used in final app
# TODO: test element.move
# TODO: test element.children for both container and simple elements



# model changelist elements: Insert, Modify and Remove

R = Rectangle


def test_Remove_properties():
    e = R(9, 9, 9, 9)
    r = Remove(elem=e)
    assert r.elem == e


def test_can_compare_Remove():
    assert Remove(R(1, 2, 9, 9)) == Remove(R(1, 2, 9, 9))
    assert Remove(R(1, 2, 9, 9)) != Remove(R(1, 22, 9, 9))


def test_Remove_raises_on_non_BaseElement_arguments():
    with pytest.raises(AssertionError):
        Remove('x')
    with pytest.raises(AssertionError):
        Remove(None)


def test_Insert_properties():
    e = R(9, 9, 9, 9)
    i = Insert(elem=e)
    assert i.elem == e


def test_can_compare_Insert():
    assert Insert(R(1, 2, 9, 9)) == Insert(R(1, 2, 9, 9))
    assert Insert(R(1, 2, 9, 9)) != Insert(R(1, 222, 9, 9))


def test_Insert_raises_on_non_BaseElement_arguments():
    with pytest.raises(AssertionError):
        Insert(None)
    with pytest.raises(AssertionError):
        Insert('x')
    with pytest.raises(AssertionError):
        Insert(Remove(R(9, 9, 9, 9)))


def test_Modify_properties():
    a = R(1, 1, 1, 1)
    b = R(2, 2, 2, 2)
    m = Modify(elem=a, modified=b)
    assert m.elem == a
    assert m.modified == b


def test_can_compare_Modify():
    m1 = Modify(R(1, 2, 3, 4), R(9, 9, 9, 9))
    m2 = Modify(R(1, 2, 3, 4), R(9, 9, 9, 9))
    m3 = Modify(R(1, 2, 3, 4), R(10, 9, 9, 9))
    m4 = Modify(R(1, 2, 3, 14), R(9, 9, 9, 9))
    assert m1 == m2
    assert m1 != m3
    assert m1 != m4
    assert m4 != m1


def test_Modify_raises_on_non_BaseElement_arguments():
    with pytest.raises(AssertionError):
        Modify(None, R(9, 9, 9, 9))
    with pytest.raises(AssertionError):
        Modify(23, R(9, 9, 9, 9))
    with pytest.raises(AssertionError):
        Modify(R(9, 9, 9, 9), None)
    with pytest.raises(AssertionError):
        Modify(R(9, 9, 9, 9), 23)


def test_comparing_Remove_and_Insert_gives_False():
    e = R(1, 2, 9, 9)
    assert Remove(e) != Insert(e)
    assert Insert(e) != Remove(e)

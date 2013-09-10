import pytest
from my_project.model import _move as move
from my_project.model.elements import Rectangle as R
from my_project.model import Modify


def test_move_element():
    el = R(1, 2, 3, 4)
    cl = move(el, 20, 30, [el])  # moving returns a changelist
    assert cl == [ Modify(el, R(21, 32, 3, 4)) ]


def test_raises_moving_element_not_in_model():
    el = R(1, 2, 3, 4)
    with pytest.raises(ValueError):
        move(el, 20, 30, [])


def test_move_nested_element():
    el = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el,))
    cl = move(el, 20, 30, [el, par])
    exp_el = R(21, 32, 3, 4)
    exp_par = P(1, 2, 3, 4, (exp_el,))
    # both parent and child have to be updated
    assert cl == [
        Modify(par, exp_par),
        Modify(el, exp_el)
    ]


def test_move_parent_of_nested_element():
    el = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el,))
    cl = move(par, 20, 30, [el, par])
    exp_par = P(21, 32, 3, 4, (el,))
    # only parent has to be updated
    assert cl == [
        Modify(par, exp_par),
    ]


def test_move_both_parent_and_nested_element():
    el = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el,))
    cl = move([par, el], 20, 30, [el, par])
    exp_par = P(21, 32, 3, 4, (el,))
    # only parent has to be updated since child is moved along with the parent
    assert cl == [
        Modify(par, exp_par),
    ]


def test_move_two_unassociated_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    cl = move([el1, el2], 20, 30, [el1, el2])
    # both moved
    assert cl == [
        Modify(el1, R(21, 32, 3, 4)),
        Modify(el2, R(23, 34, 5, 6)),
    ]


def test_move_nested_and_another_unassociated_element():
    el1 = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el1,))
    el2 = R(3, 4, 5, 6)
    cl = move([el1, el2], 20, 30, [el1, par, el2])
    exp_el1 = R(21, 32, 3, 4)
    exp_par = P(1, 2, 3, 4, (exp_el1,))
    exp_el2 = R(23, 34, 5, 6)
    assert cl == [
        Modify(par, exp_par),
        Modify(el1, exp_el1),
        Modify(el2, exp_el2),
    ]


def test_move_two_of_three_nested_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    par = P(1, 2, 3, 4, (el1, el2, el3))
    cl = move([el1, el3], 20, 30, [el1, el2, par, el3])
    exp_el1 = R(21, 32, 3, 4)
    exp_el3 = R(25, 36, 7, 8)
    exp_par = P(1, 2, 3, 4, (exp_el1, el2, exp_el3))
    assert cl == [
        Modify(par, exp_par),
        Modify(el1, exp_el1),
        Modify(el3, exp_el3),
    ]


def test_move_parent_and_two_of_three_nested_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    par = P(1, 2, 3, 4, (el1, el2, el3))
    cl = move([el1, el3, par], 20, 30, [el1, el2, par, el3])
    exp_par = P(21, 32, 3, 4, (el1, el2, el3))
    # basically moving of nested elements should be skipped if parent is moved
    assert cl == [
        Modify(par, exp_par),
    ]


def test_move_two_deeply_nested_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    par = P(1, 2, 3, 4, (el1, el2, el3))
    root = P(0, 1, 2, 3, (par,))
    cl = move([el1, el3], 20, 30, [el1, el2, par, root, el3])
    exp_el1 = R(21, 32, 3, 4)
    exp_el3 = R(25, 36, 7, 8)
    exp_par = P(1, 2, 3, 4, (exp_el1, el2, exp_el3))
    exp_root = P(1, 2, 3, 4, (exp_par,))
    assert cl == [
        Modify(par, exp_par),
        Modify(el1, exp_el1),
        Modify(root, exp_root),
        Modify(el3, exp_el3),
    ]


def test_move_parent_and_two_of_three_nested_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    par = P(1, 2, 3, 4, (el1, el2, el3))
    root = P(0, 1, 2, 3, (par,))
    cl = move([el1, el3, par], 20, 30, [par, el2, el1, root, el3])
    exp_par = P(1, 2, 3, 4, (el1, el2, el3))
    exp_root = P(1, 2, 3, 4, (exp_par,))
    # movement of el1 and el3 is ignored
    assert cl == [
        Modify(par, exp_par),
        Modify(root, exp_root),
    ]


def test_move_root_and_parent_and_two_of_three_nested_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    par = P(1, 2, 3, 4, (el1, el2, el3))
    root = P(0, 1, 2, 3, (par,))
    cl = move([el1, el3, par, root], 20, 30, [par, el2, el1, root, el3])
    exp_root = P(1, 2, 3, 4, (par,))
    # just root is moved, rest are ignored
    assert cl == [
        Modify(root, exp_root),
    ]


def test_move_two_unassociated_nested_elements():
    el1a = R(1, 2, 3, 4)
    el1b = R(3, 4, 5, 6)
    el2a = R(5, 6, 7, 8)
    el2b = R(7, 8, 9, 10)
    par1 = P(1, 2, 3, 4, (el1a, el1b))
    par2 = P(2, 3, 4, 5, (el2a, el2b))
    cl = move([el1a, el2b], 20, 30, [par, el1a, el1b, el2a, el2b])
    exp_el1a = R(21, 32, 3, 4)
    exp_el2b = R(27, 38, 9, 10)
    exp_par1 = P(1, 2, 3, 4, (exp_el1a, el1b))
    exp_par2 = P(2, 3, 4, 5, (el2a, exp_el2b))
    assert cl == [
        Modify(el1a, exp_el1a),
        Modify(el2b, exp_el2b),
        Modify(par1, exp_par1),
        Modify(par2, exp_par2),
    ]


# TODO: somewhere make sure that two parents cannot claim same element as child

# moving elements with links:

def test_move_one_linked_element():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    l = Link(el1, el2)
    cl = move([el1], 20, 30, [l, el1, el2, el3])
    exp_el1 = R(21, 32, 3, 4)
    exp_l = Link(exp_el1, el2)
    assert cl == [
        Modify(el1, exp_el1),
        Modify(l, exp_l),
    ]


def test_move_both_linked_elements():
    el1 = R(1, 2, 3, 4)
    el2 = R(3, 4, 5, 6)
    el3 = R(5, 6, 7, 8)
    l = Link(el1, el2)
    cl = move([el1, el2], 20, 30, [l, el1, el2, el3])
    exp_el1 = R(21, 32, 3, 4)
    exp_el2 = R(23, 34, 5, 6)
    exp_l = Link(exp_el1, exp_el2)
    assert cl == [
        Modify(el1, exp_el1),
        Modify(el2, exp_el2),
        Modify(l, exp_l),
    ]


def test_move_nested_linked_element():
    el1 = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el1,))
    el2 = R(3, 4, 5, 6)
    l = Link(el1, el2)
    cl = move([el1], 20, 30, [l, el1, el2, par])
    exp_el1 = R(21, 32, 3, 4)
    exp_par = R(1, 2, 3, 4, (exp_el1,))
    exp_l = Link(exp_el1, el2)
    assert cl == [
        Modify(el1, exp_el1),
        Modify(par, exp_par),
        Modify(l, exp_l),
    ]


def test_move_parent_of_nested_linked_element():
    el1 = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el1,))
    el2 = R(3, 4, 5, 6)
    l = Link(el1, el2)
    cl = move([par], 20, 30, [l, el1, el2, par])
    exp_par = R(21, 32, 3, 4, (el1,))
    assert cl == [
        Modify(par, exp_par),
    ]


@pytest.mark.parametrize('swap', [False, True])
def test_move_nested_element_of_linked_parent(swap):
    el1 = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el1,))
    el2 = R(3, 4, 5, 6)
    if swap:
        l = Link(par, el2)
        exp_l = Link(exp_par, el2)
    else:
        l = Link(el2, par)
        exp_l = Link(el2, exp_par)
    cl = move([par], 20, 30, [el1, el2, par, l])
    exp_el1 = R(21, 32, 3, 4)
    exp_par = R(1, 2, 3, 4, (exp_el1,))
    assert cl == [
        Modify(el1, exp_el1),
        Modify(par, exp_par),
        Modify(l, exp_l),
    ]


def test_move_both_linked_elements_one_is_nested():
    el1 = R(1, 2, 3, 4)
    par = P(1, 2, 3, 4, (el1,))
    el2 = R(3, 4, 5, 6)
    l = Link(el1, el2)
    cl = move([el1, el2], 20, 30, [l, el1, el2, par])
    exp_el1 = R(21, 32, 3, 4)
    exp_el2 = R(23, 34, 5, 6)
    exp_par = R(1, 2, 3, 4, (exp_el1,))
    exp_l = Link(exp_el1, exp_el2)
    assert cl == [
        Modify(el1, exp_el1),
        Modify(el2, exp_el2),
        Modify(par, exp_par),
        Modify(l, exp_l),
    ]


def test_move_both_linked_elements_both_are_nested():
    el1 = R(1, 2, 3, 4)
    par1 = P(1, 2, 3, 4, (el1,))
    el2 = R(3, 4, 5, 6)
    par2 = P(2, 3, 4, 5, (el2,))
    l = Link(el1, el2)
    cl = move([el1, el2], 20, 30, [l, el1, el2, par1, par2])
    exp_el1 = R(21, 32, 3, 4)
    exp_el2 = R(23, 34, 5, 6)
    exp_par1 = R(1, 2, 3, 4, (exp_el1,))
    exp_par2 = R(2, 3, 4, 5, (exp_el2,))
    exp_l = Link(exp_el1, exp_el2)
    assert cl == [
        Modify(el1, exp_el1),
        Modify(el2, exp_el2),
        Modify(par1, exp_par1),
        Modify(par2, exp_par2),
        Modify(l, exp_l),
    ]



# TODO:
# move link start/end vertex
# move multiple link's vertices
# move both linked elements and one link's vertex
# move both linked elements and one link's vertex - one is nested
# move both linked elements and one link's vertex - both are nested
# move both linked elements and multiple link's vertices
# move both linked elements and multiple link's vertices - one is nested
# move both linked elements and multiple link's vertices - both are nested

import pytest
from my_project.model.CanvasModel import _move as move
from my_project.model.elements import Rectangle as R
from my_project.model.elements import _BaseElement, Link
from my_project.model import Modify



class Container(_BaseElement):
    def __init__(self, x, y, parent=None):
        self.x, self.y = x, y
        super(Container, self).__init__(parent)

    def move(self, dx, dy):
        return self._replace(x=self.x + dx, y=self.y + dy)



class Test_moving_without_links:
    def test_move_element(self):
        el = R(1, 2, 3, 4)
        cl = move(el, 20, 30, [el])
        assert cl == [
            Modify(el, R(21, 32, 3, 4))
        ]

    def test_move_nested_element(self):
        par = Container(1, 2)
        el = R(1, 2, 3, 4, par)
        cl = move(el, 20, 30, [el, par])
        assert cl == [
            Modify(el, R(21, 32, 3, 4, par))
        ]

    def test_move_parent_of_nested_element(self):
        par = Container(1, 2)
        el = R(1, 2, 3, 4, par)
        cl = move(par, 20, 30, [el, par])
        # only parent is moved but child must be updated to point to new parent
        exp_par = Container(21, 32)
        exp_el = R(1, 2, 3, 4, exp_par)
        assert len(cl) == 2
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el, exp_el),
        ])

    def test_move_parent_of_multiple_nested_elements(self):
        par = Container(1, 2)
        el1 = R(1, 2, 3, 4, par)
        el2 = R(2, 2, 3, 4, par)
        el3 = R(3, 2, 3, 4, par)
        cl = move(par, 20, 30, [el1, el2, el3, par])
        exp_par = Container(21, 32)
        exp_el1 = R(1, 2, 3, 4, exp_par)
        exp_el2 = R(2, 2, 3, 4, exp_par)
        exp_el3 = R(3, 2, 3, 4, exp_par)
        assert len(cl) == 4
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el1, exp_el1),
            Modify(el2, exp_el2),
            Modify(el3, exp_el3),
        ])

    def test_move_both_parent_and_nested_element(self):
        par = Container(1, 2)
        el = R(1, 2, 3, 4, par)
        cl = move([par, el], 20, 30, [el, par])
        # only parent is moved since child is moved along with the parent
        # but child has to be modified to point to new parent
        exp_par = Container(21, 32)
        exp_el = R(1, 2, 3, 4, exp_par)
        assert len(cl) == 2
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el, exp_el),
        ])

    def test_move_two_unassociated_elements(self):
        el1 = R(1, 2, 3, 4)
        el2 = R(3, 4, 5, 6)
        cl = move([el1, el2], 20, 30, [el1, el2])
        assert len(cl) == 2
        assert set(cl) == set([
            Modify(el1, R(21, 32, 3, 4)),
            Modify(el2, R(23, 34, 5, 6)),
        ])

    def test_move_nested_and_another_unassociated_element(self):
        par = Container(1, 2)
        el1 = R(1, 2, 3, 4, par)
        el2 = R(3, 4, 5, 6)
        cl = move([el1, el2], 20, 30, [el1, par, el2])
        assert len(cl) == 2
        assert set(cl) == set([
            Modify(el1, R(21, 32, 3, 4, par)),
            Modify(el2, R(23, 34, 5, 6)),
        ])

    def test_move_two_of_three_nested_elements(self):
        par = Container(1, 2)
        el1 = R(1, 2, 3, 4, par)
        el2 = R(3, 4, 5, 6, par)
        el3 = R(5, 6, 7, 8, par)
        cl = move([el1, el3], 20, 30, [el1, el2, par, el3])
        assert len(cl) == 2
        assert set(cl) == set([
            Modify(el1, R(21, 32, 3, 4, par)),
            Modify(el3, R(25, 36, 7, 8, par)),
        ])

    def test_move_parent_and_two_of_three_nested_elements(self):
        par = Container(1, 2)
        el1 = R(1, 2, 3, 4, par)
        el2 = R(3, 4, 5, 6, par)
        el3 = R(5, 6, 7, 8, par)
        cl = move([el1, el3, par], 20, 30, [el1, el2, par, el3])
        # moving of nested elements should be skipped if parent is moved
        # but all children must be updated to point to new parent
        exp_par = Container(21, 32)
        exp_el1 = R(1, 2, 3, 4, exp_par)
        exp_el2 = R(3, 4, 5, 6, exp_par)
        exp_el3 = R(5, 6, 7, 8, exp_par)
        assert len(cl) == 4
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el1, exp_el1),
            Modify(el2, exp_el2),
            Modify(el3, exp_el3),
        ])

    def test_move_two_different_parents(self):
        par1 = Container(1, 2)
        par2 = Container(2, 3)
        el1 = R(1, 2, 3, 4, par1)
        el2 = R(3, 4, 5, 6, par1)
        el3 = R(5, 6, 7, 8, par2)
        cl = move([par2, par1], 20, 30, [el1, el2, par1, el3, par2])
        exp_par1 = Container(21, 32)
        exp_par2 = Container(22, 33)
        exp_el1 = R(1, 2, 3, 4, exp_par1)
        exp_el2 = R(3, 4, 5, 6, exp_par1)
        exp_el3 = R(5, 6, 7, 8, exp_par2)
        assert len(cl) == 5
        assert set(cl) == set([
            Modify(par1, exp_par1),
            Modify(par2, exp_par2),
            Modify(el1, exp_el1),
            Modify(el2, exp_el2),
            Modify(el3, exp_el3),
        ])

    @pytest.mark.parametrize('tweak', [1, 2, 3, 4])
    def test_move_root(self, tweak):
        root = Container(1, 2)
        par = Container(2, 3, root)
        el1 = R(1, 2, 3, 4, par)
        el2 = R(2, 3, 4, 5, par)
        what_to_move = {
            1: [root],
            2: [root, par],
            3: [root, par, el1],
            4: [root, el1],
        }
        cl = move(what_to_move[tweak], 20, 30, [root, par, el1, el2])
        # root is moved, rest are updated
        exp_root = Container(21, 32)
        exp_par = Container(2, 3, exp_root)
        exp_el1 = R(1, 2, 3, 4, exp_par)
        exp_el2 = R(2, 3, 4, 5, exp_par)
        assert len(cl) == 4
        assert set(cl) == set([
            Modify(root, exp_root),
            Modify(par, exp_par),
            Modify(el1, exp_el1),
            Modify(el2, exp_el2),
        ])




class Test_moving_linked_elements:
    def test_move_one_linked_element(self):
        el1 = R(1, 2, 3, 4)
        el2 = R(3, 4, 5, 6)
        el3 = R(5, 6, 7, 8)
        l = Link(el1, el2)
        cl = move([el1], 20, 30, [l, el1, el2, el3])
        exp_el1 = R(21, 32, 3, 4)
        assert len(cl) == 2
        assert set(cl) == set([
            Modify(el1, exp_el1),
            Modify(l, Link(exp_el1, el2)),
        ])

    def test_move_both_linked_elements(self):
        el1 = R(1, 2, 3, 4)
        el2 = R(3, 4, 5, 6)
        el3 = R(5, 6, 7, 8)
        l = Link(el1, el2)
        cl = move([el1, el2], 20, 30, [l, el1, el2, el3])
        exp_el1 = R(21, 32, 3, 4)
        exp_el2 = R(23, 34, 5, 6)
        assert len(cl) == 3
        assert set(cl) == set([
            Modify(el1, exp_el1),
            Modify(el2, exp_el2),
            Modify(l, Link(exp_el1, exp_el2)),
        ])

    def test_move_parent_of_nested_linked_element(self):
        par = Container(1, 2)
        el1 = R(1, 2, 3, 4)
        el2 = R(3, 4, 5, 6, par)
        l = Link(el1, el2)
        cl = move([par], 20, 30, [l, el1, el2, par])
        # link must be updated also
        exp_par = Container(21, 32)
        exp_el2 = R(3, 4, 5, 6, exp_par)
        exp_l = Link(el1, exp_el2)
        assert len(cl) == 3
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el2, exp_el2),
            Modify(l, exp_l),
        ])

    def test_move_linked_parent_with_nested_element(self):
        par = Container(1, 2)
        el1 = R(1, 2, 3, 4, par)
        el2 = R(3, 4, 5, 6)
        l = Link(par, el2)
        cl = move([par], 20, 30, [l, el1, el2, par])
        # link must be updated also
        exp_par = Container(21, 32)
        exp_el1 = R(1, 2, 3, 4, exp_par)
        exp_l = Link(exp_par, el2)
        assert len(cl) == 3
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el1, exp_el1),
            Modify(l, exp_l),
        ])

    def test_move_parent_linked_to_its_child(self):
        par = Container(1, 2)
        el = R(3, 4, 5, 6, par)
        l = Link(par, el)
        cl = move([par], 20, 30, [l, el, par])
        # it's allowed to have nested element linked to its parent
        exp_par = Container(21, 32)
        exp_el = R(3, 4, 5, 6, exp_par)
        exp_l = Link(exp_par, exp_el)
        assert len(cl) == 3
        assert set(cl) == set([
            Modify(par, exp_par),
            Modify(el, exp_el),
            Modify(l, exp_l),
        ])

    def test_move_two_different_parents_containing_linked_elements(self):
        par1 = Container(1, 2)
        par2 = Container(2, 3)
        el1 = R(1, 2, 3, 4, par1)
        el2 = R(3, 4, 5, 6, par2)
        l = Link(el1, el2)
        cl = move([par1, par2], 20, 30, [l, el1, el2, par1, par2])
        exp_par1 = Container(21, 32)
        exp_par2 = Container(22, 33)
        exp_el1 = R(1, 2, 3, 4, exp_par1)
        exp_el2 = R(3, 4, 5, 6, exp_par2)
        exp_l = Link(exp_el1, exp_el2)
        assert len(cl) == 5
        assert set(cl) == set([
            Modify(par1, exp_par1),
            Modify(par2, exp_par2),
            Modify(el1, exp_el1),
            Modify(el2, exp_el2),
            Modify(l, exp_l),
        ])



# TODO:
# move link start/end vertex
# move multiple link's vertices
# move both linked elements and one link's vertex
# move both linked elements and one link's vertex - one is nested
# move both linked elements and one link's vertex - both are nested
# move both linked elements and multiple link's vertices
# move both linked elements and multiple link's vertices - one is nested
# move both linked elements and multiple link's vertices - both are nested

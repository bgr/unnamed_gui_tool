import pytest
from my_project.model import Remove, Change, Insert, parse, commit
from my_project.model import BaseElement as BE


class Test_instantiating_changes(object):
    def test_Change(self):
        Change(old=BE(9, 9, 9, 9), new=BE(9, 9, 9, 9))  # works
        with pytest.raises(ValueError):
            Change(None, BE(9, 9, 9, 9))
        with pytest.raises(ValueError):
            Change(BE(9, 9, 9, 9), 23)

    def test_Remove(self):
        Remove(elem=BE(9, 9, 9, 9))  # works
        with pytest.raises(ValueError):
            Remove('x')
        with pytest.raises(ValueError):
            Remove(None)

    def test_Insert(self):
        Insert(elem=BE(9, 9, 9, 9))  # works
        with pytest.raises(ValueError):
            Insert('x')
        with pytest.raises(ValueError):
            Insert(Remove(9, 9, 9, 9))


class Test_instantiating_elements(object):
    def test_BaseElement(self):
        BE(9, 9, 9, 9)  # works
        with pytest.raises(ValueError):
            BE('9', 9, 9, 9)
            BE(9, 9, 9, 9)

    def test_zero_width(self):
        with pytest.raises(ValueError):
            BE(100, 100, 0, 100)

    def test_zero_height(self):
        with pytest.raises(ValueError):
            BE(100, 100, 100, 0)

    def test_fix_negative_width(self):
        el = BE(20, 30, -100, 40)
        assert el == BE(-80, 30, 100, 40)

    def test_fix_negative_height(self):
        el = BE(20, 30, 100, -40)
        assert el == BE(20, -10, 100, 40)

    def test_fix_negative_both(self):
        el = BE(20, 30, -100, -40)
        assert el == BE(-80, -10, 100, 40)



class Test_parse_changelist(object):

    def setup_class(self):
        self.elems = [
            BE(10, 10, 100, 100),
            BE(20, 20, 200, 200),
            BE(30, 30, 300, 300),
        ]

    def test_allows_new_elements(self):
        cl = [
            Insert(elem=BE(44, 44, 444, 444)),
            Insert(BE(55, 55, 555, 555)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(BE(44, 44, 444, 444)),
            Insert(BE(55, 55, 555, 555)),
        ]


    def test_fixes_new_with_negative_dimensions(self):
        cl = [
            Insert(BE(488, 44, -444, 444)),
            Insert(BE(55, 610, 555, -555)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(BE(44, 44, 444, 444)),
            Insert(BE(55, 55, 555, 555)),
        ]

    def test_excludes_fixed_new_with_same_properties_as_existing(self):
        cl = [
            Insert(BE(330, 30, -300, 300)),  # existing!
            Insert(BE(488, 44, -444, 444)),
            Insert(BE(20, 220, 200, -200)),  # existing!
            Insert(BE(55, 610, 555, -555)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(BE(44, 44, 444, 444)),
            Insert(BE(55, 55, 555, 555)),
        ]

    def test_excludes_duplicate_fixed_new(self):
        cl = [
            Insert(BE(330, 30, -300, 300)),  # existing!
            Insert(BE(488, 44, -444, 444)),
            Insert(BE(20, 220, 200, -200)),  # existing!
            Insert(BE(55, 610, 555, -555)),
            Insert(BE(488, 488, -444, -444)),  # duplicate in cl!
            Insert(BE(55, 610, 555, -555)),  # duplicate in cl!
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(BE(44, 44, 444, 444)),
            Insert(BE(55, 55, 555, 555)),
        ]

    def test_allows_changed_elements(self):
        cl = [
            Change(old=BE(30, 30, 300, 300), new=BE(33, 33, 330, 330)),
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Change(old=BE(30, 30, 300, 300), new=BE(33, 33, 330, 330)),
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
        ]
        assert ins == []

    def test_excludes_elements_with_no_actual_changes(self):
        cl = [
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
            Change(old=BE(30, 30, 300, 300), new=BE(30, 30, 300, 300)),
            Change(old=BE(10, 10, 100, 100), new=BE(10, 10, 111, 100)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
            Change(old=BE(10, 10, 100, 100), new=BE(10, 10, 111, 100)),
        ]
        assert ins == []

    def test_fixes_changes_with_negative_dimensions(self):
        cl = [
            Change(old=BE(20, 20, 200, 200), new=BE(200, 20, -100, 20)),
            Change(old=BE(10, 10, 100, 100), new=BE(-10, 10, -90, 100)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Change(old=BE(20, 20, 200, 200), new=BE(100, 20, 100, 20)),
            Change(old=BE(10, 10, 100, 100), new=BE(-100, 10, 90, 100)),
        ]
        assert ins == []

    def test_allows_removing_elements(self):
        cl = [
            Remove(elem=BE(30, 30, 300, 300)),
            Remove(BE(20, 20, 200, 200)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == [
            Remove(BE(30, 30, 300, 300)),
            Remove(BE(20, 20, 200, 200)),
        ]
        assert chg == []
        assert ins == []


    def test_mixed(self):
        cl = [
            Remove(BE(30, 30, 300, 300)),
            Insert(BE(10, 5, -5, 5)),  # fix
            Change(BE(10, 10, 100, 100), BE(100, 1100, 1000, -1000)),  # fix
            Remove(BE(20, 20, 200, 200)),
            Insert(BE(4, 4, 4, 4)),
        ]
        rem, chg, ins = parse(cl, self.elems)
        assert rem == [
            Remove(BE(30, 30, 300, 300)),
            Remove(BE(20, 20, 200, 200)),
        ]
        assert chg == [
            Change(BE(10, 10, 100, 100), BE(100, 100, 1000, 1000))
        ]
        assert ins == [
            Insert(BE(5, 5, 5, 5)),
            Insert(BE(4, 4, 4, 4)),
        ]


    def test_raises_on_invalid_changelist_elements(self):
        with pytest.raises(ValueError):
            parse([Insert(BE(9, 9, 9, 9)), None], self.elems)
        with pytest.raises(ValueError):
            parse([Insert(BE(9, 9, 9, 9)), 2], self.elems)


    def test_raises_when_inserting_same_properties_as_existing(self):
        with pytest.raises(ValueError):
            parse([Insert(BE(30, 30, 300, 300))], self.elems)

    def test_raises_when_changing_old_not_in_existing(self):
        with pytest.raises(ValueError):
            parse([Change(BE(9, 9, 9, 9), BE(1, 1, 10, 10))], self.elems)

    def test_raises_when_deleting_old_not_in_existing(self):
        with pytest.raises(ValueError):
            parse([Change(BE(9, 9, 9, 9), None)], self.elems)

    def test_raises_when_both_old_and_new_are_None(self):
        with pytest.raises(ValueError):
            parse([Change(None, None)], self.elems)

    def test_raises_when_deleting_then_adding_same_elem(self):
        cl = [
            Remove(BE(10, 10, 100, 100)),
            Insert(BE(10, 10, 100, 100)),
        ]
        with pytest.raises(ValueError):
            parse(cl, self.elems)

    def test_raises_when_adding_then_deleting_same_elem(self):
        cl = [
            Insert(BE(10, 10, 100, 100)),
            Remove(BE(10, 10, 100, 100)),
        ]
        with pytest.raises(ValueError):
            parse(cl, self.elems)

    def test_raises_when_deleting_then_adding_same_elem_with_fixing(self):
        cl = [
            Remove(BE(10, 10, 100, 100)),
            Insert(BE(10, 110, 100, -100)),
        ]
        with pytest.raises(ValueError):
            parse(cl, self.elems)

    def test_raises_when_adding_then_deleting_same_elem_with_fixing(self):
        cl = [
            Insert(BE(10, 110, 100, -100)),
            Remove(BE(10, 10, 100, 100)),
        ]
        with pytest.raises(ValueError):
            parse(cl, self.elems)



class Test_commit(object):

    def setup_method(self, method):
        self.elems = [
            BE(1, 1, 10, 10),
            BE(2, 2, 20, 20),
            BE(3, 3, 30, 30),
        ]

    def test_validates_before_committing(self):
        cl = [
            Change(old=BE(3, 3, 30, 30), new=BE(33, 33, 33, 33)),  # change
            Change(old=BE(3, 3, 30, 30), new=BE(33, 33, 33, 33)),  # duplicate

            Change(old=None, new=BE(2, 2, 20, 20)),  # existing - exclude
            Change(old=None, new=BE(33, 3, -30, 30)),  # existing - exclude

            Change(old=None, new=BE(488, 44, -444, 444)),  # fix dimensions
            Change(old=None, new=BE(55, 55, 555, 555)),  # add
            Change(old=None, new=BE(488, 488, -444, -444)),  # duplicate

            Change(old=BE(1, 1, 10, 10), new=BE(1, 1, 10, 10)),  # no change
            Change(old=BE(4, 4, 40, 40), new=None),  # remove
        ]
        parsed = parse(cl, self.elems)
        assert parsed == [
            Change(old=BE(3, 3, 30, 30), new=BE(33, 33, 33, 33)),
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
            Change(old=BE(4, 4, 40, 40), new=None),
        ]
        commit

    def test_informs_listeners_about_new_elements(self):
        pass

    def test_informs_listeners_about_changed_elements(self):
        pass

    def test_informs_listeners_about_deleted_elements(self):
        pass

    def test_informs_listeners_when_assigning_new_elements(self):
        pass

    def test_doesnt_inform_when_empty_changelist(self):
        pass


class Test_tampering(object):
    def setup_class(self):
        self.initial = []

    def test_cant_modify_elems(self):
        pass

    def test_cant_change_changelist_via_event(self):
        # submit a changelist then get informed via eventbus
        # modify received changelist and assert that model is untouched
        pass

    def test_cant_change_changelist_after_submitting(self):
        # submit a changelist as method argument, then
        # modify the argument, assert that it doesn't reflect in model
        pass

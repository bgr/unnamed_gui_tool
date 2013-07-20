import pytest
from my_project.model import Change, fix, validate
from my_project.model import BaseElement as BE


class Test_fix_element(object):

    def test_zero_width(self):
        el = BE(100, 100, 0, 100)
        with pytest.raises(ValueError):
            fix(el)

    def test_zero_height(self):
        el = BE(100, 100, 100, 0)
        with pytest.raises(ValueError):
            fix(el)

    def test_negative_width(self):
        el = BE(20, 30, -100, 40)
        assert fix(el) == BE(-80, 30, 100, 40)

    def test_negative_height(self):
        el = BE(20, 30, 100, -40)
        assert fix(el) == BE(20, -10, 100, 40)

    def test_negative_both(self):
        el = BE(20, 30, -100, -40)
        assert fix(el) == BE(-80, -10, 100, 40)



class Test_validate_changelist(object):

    def setup_class(self):
        self.elems = [
            BE(10, 10, 100, 100),
            BE(20, 20, 200, 200),
            BE(30, 30, 300, 300),
        ]

    def test_allows_new_elements(self):
        cl = [
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
        ]

    def test_excludes_new_with_same_properties_as_existing(self):
        cl = [
            Change(old=None, new=BE(30, 30, 300, 300)),
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(20, 20, 200, 200)),
            Change(old=None, new=BE(55, 55, 555, 555)),
            Change(old=None, new=BE(20, 20, 200, 200)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
        ]

    def test_fixes_new_with_negative_dimensions(self):
        cl = [
            Change(old=None, new=BE(488, 44, -444, 444)),
            Change(old=None, new=BE(55, 610, 555, -555)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
        ]

    def test_excludes_fixed_new_with_same_properties_as_existing(self):
        cl = [
            Change(old=None, new=BE(330, 30, -300, 300)),  # existing!
            Change(old=None, new=BE(488, 44, -444, 444)),
            Change(old=None, new=BE(20, 220, 200, -200)),  # existing!
            Change(old=None, new=BE(55, 610, 555, -555)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
        ]

    def test_excludes_duplicate_fixed_new(self):
        cl = [
            Change(old=None, new=BE(330, 30, -300, 300)),  # existing!
            Change(old=None, new=BE(488, 44, -444, 444)),
            Change(old=None, new=BE(20, 220, 200, -200)),  # existing!
            Change(old=None, new=BE(55, 610, 555, -555)),
            Change(old=None, new=BE(488, 488, -444, -444)),  # duplicate in cl!
            Change(old=None, new=BE(55, 610, 555, -555)),  # duplicate in cl!
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=None, new=BE(44, 44, 444, 444)),
            Change(old=None, new=BE(55, 55, 555, 555)),
        ]

    def test_allows_changed_elements(self):
        cl = [
            Change(old=BE(30, 30, 300, 300), new=BE(33, 33, 330, 330)),
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=BE(30, 30, 300, 300), new=BE(33, 33, 330, 330)),
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
        ]

    def test_excludes_elements_with_no_actual_changes(self):
        cl = [
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
            Change(old=BE(30, 30, 300, 300), new=BE(30, 30, 300, 300)),
            Change(old=BE(10, 10, 100, 100), new=BE(10, 10, 111, 100)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=BE(20, 20, 200, 200), new=BE(23, 23, 230, 320)),
            Change(old=BE(10, 10, 100, 100), new=BE(10, 10, 111, 100)),
        ]

    def test_fixes_changes_with_negative_dimensions(self):
        cl = [
            Change(old=BE(20, 20, 200, 200), new=BE(200, 20, -100, 20)),
            Change(old=BE(10, 10, 100, 100), new=BE(-10, 10, -90, 100)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=BE(20, 20, 200, 200), new=BE(100, 20, 100, 20)),
            Change(old=BE(10, 10, 100, 100), new=BE(-100, 10, 90, 100)),
        ]

    def test_excludes_duplicate_changes(self):
        cl = [
            Change(old=BE(10, 10, 100, 100), new=BE(-10, 10, -90, 100)),
            Change(old=BE(20, 20, 200, 200), new=BE(200, 20, -100, 20)),
            Change(old=BE(10, 10, 100, 100), new=BE(-100, 110, 90, -100)),
        ]
        validated = validate(cl, self.elems)
        assert validated == [
            Change(old=BE(10, 10, 100, 100), new=BE(-100, 10, 90, 100)),
            Change(old=BE(20, 20, 200, 200), new=BE(100, 20, 100, 20)),
        ]

    def test_raises_when_changing_old_not_in_existing(self):
        with pytest.raises(ValueError):
            validate([Change(BE(9, 9, 9, 9), BE(1, 1, 10, 10))], self.elems)

    def test_raises_when_deleting_old_not_in_existing(self):
        with pytest.raises(ValueError):
            validate([Change(BE(9, 9, 9, 9), None)], self.elems)

    def test_raises_when_both_old_and_new_are_None(self):
        with pytest.raises(ValueError):
            validate([Change(None, None)], self.elems)

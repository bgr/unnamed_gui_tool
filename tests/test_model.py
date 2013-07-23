import pytest
from my_project.model import (Remove, Modify, Insert, _parse, _commit,
                              Model_Changed, CanvasModel)
from my_project.model import _BaseElement as BE
from hsmpy import EventBus


class Test_elements(object):
    def test_BaseElement(self):
        BE(9, 9, 9, 9)

    def test_comparable_BaseElement(self):
        assert BE(1, 2, 9, 9) == BE(1, 2, 9, 9)
        assert BE(1, 2, 9, 9) != BE(2, 2, 9, 9)

    def test_raises_on_invalid_values(self):
        with pytest.raises(TypeError):
            BE(None, 9, 9, 9)
        with pytest.raises(ValueError):
            BE(9, 9, 'a', 9)

    def test_raises_on_zero_width(self):
        with pytest.raises(ValueError):
            BE(100, 100, 0, 100)

    def test_raises_on_zero_height(self):
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



class Test_changes(object):
    def test_Remove(self):
        Remove(elem=BE(9, 9, 9, 9))

    def test_comparable_Remove(self):
        assert Remove(BE(1, 2, 9, 9)) == Remove(BE(1, 2, 9, 9))

    def test_Remove_raises_on_invalid_elements(self):
        with pytest.raises(AssertionError):
            Remove('x')
        with pytest.raises(AssertionError):
            Remove(None)

    def test_Insert(self):
        Insert(elem=BE(9, 9, 9, 9))

    def test_comparable_Insert(self):
        assert Insert(BE(1, 2, 9, 9)) == Insert(BE(1, 2, 9, 9))

    def test_Insert_raises_on_invalid_elements(self):
        with pytest.raises(AssertionError):
            Insert('x')
        with pytest.raises(AssertionError):
            Insert(Remove(BE(9, 9, 9, 9)))

    def test_Modify(self):
        Modify(elem=BE(9, 9, 9, 9), modified=BE(9, 9, 9, 9))

    def test_Modify_comparable(self):
        assert Modify(BE(1, 2, 3, 4), BE(9, 9, 9, 9)) == Modify(BE(1, 2, 3, 4),
                                                                BE(9, 9, 9, 9))

    def test_Modify_raises_on_invalid_elements(self):
        with pytest.raises(AssertionError):
            Modify(None, BE(9, 9, 9, 9))
        with pytest.raises(AssertionError):
            Modify(BE(9, 9, 9, 9), 23)



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
        rem, chg, ins = _parse(cl, self.elems)
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
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(BE(44, 44, 444, 444)),
            Insert(BE(55, 55, 555, 555)),
        ]

    def test_allows_changed_elements(self):
        cl = [
            Modify(BE(30, 30, 300, 300), BE(33, 33, 330, 330)),
            Modify(BE(20, 20, 200, 200), BE(23, 23, 230, 320)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Modify(BE(30, 30, 300, 300), BE(33, 33, 330, 330)),
            Modify(BE(20, 20, 200, 200), BE(23, 23, 230, 320)),
        ]
        assert ins == []

    # TODO raises error currently, might relax that rule in the future
    #def test_excludes_elements_with_no_actual_changes(self):
    #    cl = [
    #        Modify(BE(20, 20, 200, 200), BE(23, 23, 230, 320)),
    #        Modify(BE(30, 30, 300, 300), BE(30, 30, 300, 300)),
    #        Modify(BE(10, 10, 100, 100), BE(10, 10, 111, 100)),
    #    ]
    #    rem, chg, ins = _parse(cl, self.elems)
    #    assert rem == []
    #    assert chg == [
    #        Modify(BE(20, 20, 200, 200), BE(23, 23, 230, 320)),
    #        Modify(BE(10, 10, 100, 100), BE(10, 10, 111, 100)),
    #    ]
    #    assert ins == []

    def test_fixes_changes_with_negative_dimensions(self):
        cl = [
            Modify(BE(20, 20, 200, 200), BE(200, 20, -100, 20)),
            Modify(BE(10, 10, 100, 100), BE(-10, 10, -90, 100)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Modify(BE(20, 20, 200, 200), BE(100, 20, 100, 20)),
            Modify(BE(10, 10, 100, 100), BE(-100, 10, 90, 100)),
        ]
        assert ins == []

    def test_allows_removing_elements(self):
        cl = [
            Remove(elem=BE(30, 30, 300, 300)),
            Remove(BE(20, 20, 200, 200)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
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
            Modify(BE(10, 10, 100, 100), BE(100, 1100, 1000, -1000)),  # fix
            Remove(BE(20, 20, 200, 200)),
            Insert(BE(4, 4, 4, 4)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == [
            Remove(BE(30, 30, 300, 300)),
            Remove(BE(20, 20, 200, 200)),
        ]
        assert chg == [
            Modify(BE(10, 10, 100, 100), BE(100, 100, 1000, 1000))
        ]
        assert ins == [
            Insert(BE(5, 5, 5, 5)),
            Insert(BE(4, 4, 4, 4)),
        ]


    def test_raises_on_invalid_changelist_elements(self):
        with pytest.raises(ValueError) as err:
            _parse([Insert(BE(9, 9, 9, 9)), None], self.elems)
        assert 'Invalid change' in err.value.message
        with pytest.raises(ValueError) as err:
            _parse([Insert(BE(9, 9, 9, 9)), 2], self.elems)
        assert 'Invalid change' in err.value.message

    def test_raises_when_inserting_same_as_existing(self):
        with pytest.raises(ValueError) as err:
            _parse([Insert(BE(30, 30, 300, 300))], self.elems)
        assert 'already present' in err.value.message

    def test_raises_when_inserting_same_as_existing_with_fixing(self):
        with pytest.raises(ValueError) as err:
            _parse([Insert(BE(30, 330, 300, -300))], self.elems)
        assert 'already present' in err.value.message

    def test_raises_when_changing_old_not_in_existing(self):
        with pytest.raises(ValueError) as err:
            _parse([Modify(BE(9, 9, 9, 9), BE(1, 1, 10, 10))], self.elems)
        assert "Changing element that's not in the model" in err.value.message

    def test_raises_when_removing_old_not_in_existing(self):
        with pytest.raises(ValueError) as err:
            _parse([Remove(BE(9, 9, 9, 9))], self.elems)
        assert "Removing element that's not in the model" in err.value.message

    def test_raises_on_duplicate_insertions(self):
        cl = [
            Insert(BE(55, 610, 555, -555)),
            Insert(BE(610, 55, -555, 555)),
        ]
        with pytest.raises(ValueError) as err:
            _parse(cl, self.elems)
        assert 'Inserting same element' in err.value.message

    def test_raises_on_duplicate_removals(self):
        cl = [
            Remove(BE(10, 10, 100, 100)),
            Remove(BE(10, 10, 100, 100)),
        ]
        with pytest.raises(ValueError) as err:
            _parse(cl, self.elems)
        assert 'Removing same element' in err.value.message


class Test_commit(object):

    def setup_class(self):
        self.elems = [
            BE(1, 1, 10, 10),
            BE(2, 2, 20, 20),
            BE(3, 3, 30, 30),
        ]
        self.changelog = [
            ['some', 'old'],
            ['changes', 'here'],
        ]
        self.counter = 0
        self.received_events = []

        def on_change(event):
            self.counter += 1
            self.received_events += [event]

        self.eb = EventBus()
        self.eb.register(Model_Changed, on_change)


    def test_commit(self):
        cl = [
            Remove(BE(3, 3, 30, 30)),
            Insert(BE(10, 5, -5, 5)),  # fix
            Modify(BE(1, 1, 10, 10), BE(100, 1100, 1000, -1000)),  # fix
            Remove(BE(2, 2, 20, 20)),
            Insert(BE(4, 4, 4, 4)),
        ]

        _commit(cl, self.changelog, self.eb, self.elems)

    def test_elems_list_updated(self):
        assert self.elems == [
            BE(100, 100, 1000, 1000),
            BE(5, 5, 5, 5),
            BE(4, 4, 4, 4),
        ]

    def test_received_event(self):
        assert self.counter == 1
        assert len(self.received_events) == 1
        assert isinstance(self.received_events[0], Model_Changed)

    def test_event_data_contains_fixed_and_ordered_changes(self):
        assert self.received_events[0].data == [
            Remove(BE(3, 3, 30, 30)),
            Remove(BE(2, 2, 20, 20)),
            Modify(BE(1, 1, 10, 10), BE(100, 100, 1000, 1000)),
            Insert(BE(5, 5, 5, 5)),
            Insert(BE(4, 4, 4, 4)),
        ]

    def test_changes_appended_to_changelog(self):
        assert self.changelog == [
            ['some', 'old'],
            ['changes', 'here'],
            self.received_events[0].data,
        ]

    def test_doesnt_inform_when_empty_changelist(self):
        _commit([], self.changelog, self.eb, self.elems)
        # everything should be the same
        assert self.elems == [
            BE(100, 100, 1000, 1000),
            BE(5, 5, 5, 5),
            BE(4, 4, 4, 4),
        ]
        assert self.counter == 1
        assert len(self.received_events) == 1
        assert isinstance(self.received_events[0], Model_Changed)
        assert self.received_events[0].data == [
            Remove(BE(3, 3, 30, 30)),
            Remove(BE(2, 2, 20, 20)),
            Modify(BE(1, 1, 10, 10), BE(100, 100, 1000, 1000)),
            Insert(BE(5, 5, 5, 5)),
            Insert(BE(4, 4, 4, 4)),
        ]
        assert self.changelog == [
            ['some', 'old'],
            ['changes', 'here'],
            self.received_events[0].data,
        ]


class Test_CanvasModel(object):
    def setup_class(self):
        self.initial_elements = [
            BE(1, 1, 10, 10),
            BE(2, 2, 20, 20),
            BE(3, 3, 30, 30),
        ]
        self.counter = 0
        self.received_events = []

        def on_change(event):
            self.counter += 1
            self.received_events += [event]

        self.changelist = [  # used for commit
            Insert(BE(4, 4, 40, 40)),
            Modify(BE(3, 3, 30, 30), BE(30, 30, 300, 300)),
            Remove(BE(2, 2, 20, 20)),
        ]

        self.eb = EventBus()
        self.model = CanvasModel(self.eb)
        self.eb.register(Model_Changed, on_change)

    def test_setting_elems_updates_elems(self):
        to_give = self.initial_elements[:]  # copy
        self.model.elems = to_give
        assert to_give == self.initial_elements  # model didn't change given
        assert self.model.elems == self.initial_elements
        assert self.model._elems == self.initial_elements

    def test_setting_elems_updates_changelog(self):
        assert self.model._changelog == [
            [
                Insert(BE(1, 1, 10, 10)),
                Insert(BE(2, 2, 20, 20)),
                Insert(BE(3, 3, 30, 30)),
            ],
        ]

    def test_setting_elems_informs_listeners(self):
        assert self.counter == 1
        assert len(self.received_events) == 1
        assert self.received_events[0].data == self.model._changelog[0]

    def test_cant_modify_elems_through_getter(self):
        self.model.elems[1] = 'abc'
        self.model.elems.pop(0)
        assert self.model.elems == self.initial_elements

    def test_cant_inject_changes_to_changelog_through_event(self):
        evt = self.received_events[0]
        backup = evt.data[0]
        evt.data[0] == 'abc'
        assert self.model._changelog == [
            [
                Insert(BE(1, 1, 10, 10)),
                Insert(BE(2, 2, 20, 20)),
                Insert(BE(3, 3, 30, 30)),
            ],
        ]
        evt.data[0] = backup

    def test_commit(self):
        self.model.commit(self.changelist)

    def test_commit_informs_listeners(self):
        assert self.counter == 2
        assert len(self.received_events) == 2
        assert self.received_events[1].data == [
            Remove(BE(2, 2, 20, 20)),
            Modify(BE(3, 3, 30, 30), BE(30, 30, 300, 300)),
            Insert(BE(4, 4, 40, 40)),
        ]

    def test_commit_updates_elems(self):
        assert self.model._elems == [
            BE(1, 1, 10, 10),
            BE(30, 30, 300, 300),
            BE(4, 4, 40, 40),
        ]
        assert self.model.elems == self.model._elems

    def test_commit_updates_changelog(self):
        assert self.model._changelog == [
            [
                Insert(BE(1, 1, 10, 10)),
                Insert(BE(2, 2, 20, 20)),
                Insert(BE(3, 3, 30, 30)),
            ],
            [
                Remove(BE(2, 2, 20, 20)),
                Modify(BE(3, 3, 30, 30), BE(30, 30, 300, 300)),
                Insert(BE(4, 4, 40, 40)),
            ]
        ]

    def test_cant_inject_changes_to_changelog_through_commit_argument(self):
        self.changelist[2] = 'abc'
        self.changelist.pop(0)
        assert self.received_events[1].data == [
            Remove(BE(2, 2, 20, 20)),
            Modify(BE(3, 3, 30, 30), BE(30, 30, 300, 300)),
            Insert(BE(4, 4, 40, 40)),
        ]
        assert self.model._changelog == [
            [
                Insert(BE(1, 1, 10, 10)),
                Insert(BE(2, 2, 20, 20)),
                Insert(BE(3, 3, 30, 30)),
            ],
            [
                Remove(BE(2, 2, 20, 20)),
                Modify(BE(3, 3, 30, 30), BE(30, 30, 300, 300)),
                Insert(BE(4, 4, 40, 40)),
            ]
        ]

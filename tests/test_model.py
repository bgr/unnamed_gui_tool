import pytest
from my_project.model import Remove, Modify, Insert, CanvasModel
from my_project.model.CanvasModel import _parse, _commit
from my_project.model.elements import Rectangle as R
from my_project.events import Model_Changed
from hsmpy import EventBus



class Test_elements(object):
    def test_BaseElement(self):
        R(9, 9, 9, 9)

    def test_comparable_BaseElement(self):
        assert R(1, 2, 9, 9) == R(1, 2, 9, 9)
        assert R(1, 2, 9, 9) != R(2, 2, 9, 9)

    def test_raises_on_invalid_values(self):
        with pytest.raises(TypeError):
            R(None, 9, 9, 9)
        with pytest.raises(ValueError):
            R(9, 9, 'a', 9)

    def test_fix_negative_width(self):
        el = R(20, 30, -100, 40)
        assert el == R(-80, 30, 100, 40)

    def test_fix_negative_height(self):
        el = R(20, 30, 100, -40)
        assert el == R(20, -10, 100, 40)

    def test_fix_negative_both(self):
        el = R(20, 30, -100, -40)
        assert el == R(-80, -10, 100, 40)



class Test_changes(object):
    def test_Remove(self):
        Remove(elem=R(9, 9, 9, 9))

    def test_comparable_Remove(self):
        assert Remove(R(1, 2, 9, 9)) == Remove(R(1, 2, 9, 9))

    def test_Remove_raises_on_invalid_elements(self):
        with pytest.raises(AssertionError):
            Remove('x')
        with pytest.raises(AssertionError):
            Remove(None)

    def test_Insert(self):
        Insert(elem=R(9, 9, 9, 9))

    def test_comparable_Insert(self):
        assert Insert(R(1, 2, 9, 9)) == Insert(R(1, 2, 9, 9))

    def test_Insert_raises_on_invalid_elements(self):
        with pytest.raises(AssertionError):
            Insert('x')
        with pytest.raises(AssertionError):
            Insert(Remove(R(9, 9, 9, 9)))

    def test_Modify(self):
        Modify(elem=R(9, 9, 9, 9), modified=R(9, 9, 9, 9))

    def test_Modify_comparable(self):
        assert Modify(R(1, 2, 3, 4), R(9, 9, 9, 9)) == Modify(R(1, 2, 3, 4),
                                                              R(9, 9, 9, 9))

    def test_Modify_raises_on_invalid_elements(self):
        with pytest.raises(AssertionError):
            Modify(None, R(9, 9, 9, 9))
        with pytest.raises(AssertionError):
            Modify(R(9, 9, 9, 9), 23)



class Test_parse_changelist(object):

    def setup_class(self):
        self.elems = [
            R(10, 10, 100, 100),
            R(20, 20, 200, 200),
            R(30, 30, 300, 300),
        ]

    def test_allows_new_elements(self):
        cl = [
            Insert(elem=R(44, 44, 444, 444)),
            Insert(R(55, 55, 555, 555)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(R(44, 44, 444, 444)),
            Insert(R(55, 55, 555, 555)),
        ]

    def test_fixes_new_with_negative_dimensions(self):
        cl = [
            Insert(R(488, 44, -444, 444)),
            Insert(R(55, 610, 555, -555)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == []
        assert ins == [
            Insert(R(44, 44, 444, 444)),
            Insert(R(55, 55, 555, 555)),
        ]

    def test_allows_changed_elements(self):
        cl = [
            Modify(R(30, 30, 300, 300), R(33, 33, 330, 330)),
            Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Modify(R(30, 30, 300, 300), R(33, 33, 330, 330)),
            Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
        ]
        assert ins == []

    # TODO raises error currently, might relax that rule in the future
    #def test_excludes_elements_with_no_actual_changes(self):
    #    cl = [
    #        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
    #        Modify(R(30, 30, 300, 300), R(30, 30, 300, 300)),
    #        Modify(R(10, 10, 100, 100), R(10, 10, 111, 100)),
    #    ]
    #    rem, chg, ins = _parse(cl, self.elems)
    #    assert rem == []
    #    assert chg == [
    #        Modify(R(20, 20, 200, 200), R(23, 23, 230, 320)),
    #        Modify(R(10, 10, 100, 100), R(10, 10, 111, 100)),
    #    ]
    #    assert ins == []

    def test_fixes_changes_with_negative_dimensions(self):
        cl = [
            Modify(R(20, 20, 200, 200), R(200, 20, -100, 20)),
            Modify(R(10, 10, 100, 100), R(-10, 10, -90, 100)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == []
        assert chg == [
            Modify(R(20, 20, 200, 200), R(100, 20, 100, 20)),
            Modify(R(10, 10, 100, 100), R(-100, 10, 90, 100)),
        ]
        assert ins == []

    def test_allows_removing_elements(self):
        cl = [
            Remove(elem=R(30, 30, 300, 300)),
            Remove(R(20, 20, 200, 200)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
        assert rem == [
            Remove(R(30, 30, 300, 300)),
            Remove(R(20, 20, 200, 200)),
        ]
        assert chg == []
        assert ins == []


    def test_mixed(self):
        cl = [
            Remove(R(30, 30, 300, 300)),
            Insert(R(10, 5, -5, 5)),  # fix
            Modify(R(10, 10, 100, 100), R(100, 1100, 1000, -1000)),  # fix
            Remove(R(20, 20, 200, 200)),
            Insert(R(4, 4, 4, 4)),
        ]
        rem, chg, ins = _parse(cl, self.elems)
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


    def test_raises_on_invalid_changelist_elements(self):
        with pytest.raises(ValueError) as err:
            _parse([Insert(R(9, 9, 9, 9)), None], self.elems)
        assert 'Invalid change' in err.value.message
        with pytest.raises(ValueError) as err:
            _parse([Insert(R(9, 9, 9, 9)), 2], self.elems)
        assert 'Invalid change' in err.value.message

    def test_raises_when_inserting_same_as_existing(self):
        with pytest.raises(ValueError) as err:
            _parse([Insert(R(30, 30, 300, 300))], self.elems)
        assert 'already present' in err.value.message

    def test_raises_when_inserting_same_as_existing_with_fixing(self):
        with pytest.raises(ValueError) as err:
            _parse([Insert(R(30, 330, 300, -300))], self.elems)
        assert 'already present' in err.value.message

    def test_raises_when_changing_old_not_in_existing(self):
        with pytest.raises(ValueError) as err:
            _parse([Modify(R(9, 9, 9, 9), R(1, 1, 10, 10))], self.elems)
        assert "Changing element that's not in the model" in err.value.message

    def test_raises_when_removing_old_not_in_existing(self):
        with pytest.raises(ValueError) as err:
            _parse([Remove(R(9, 9, 9, 9))], self.elems)
        assert "Removing element that's not in the model" in err.value.message

    def test_raises_on_duplicate_insertions(self):
        cl = [
            Insert(R(55, 610, 555, -555)),
            Insert(R(610, 55, -555, 555)),
        ]
        with pytest.raises(ValueError) as err:
            _parse(cl, self.elems)
        assert 'Inserting same element' in err.value.message

    def test_raises_on_duplicate_removals(self):
        cl = [
            Remove(R(10, 10, 100, 100)),
            Remove(R(10, 10, 100, 100)),
        ]
        with pytest.raises(ValueError) as err:
            _parse(cl, self.elems)
        assert 'Removing same element' in err.value.message

    def test_raises_on_zero_dimensions(self):
        _parse([Insert(R(1, 1, 0, 1))], self.elems)  # allowed one to be 0
        _parse([Insert(R(1, 1, 1, 0))], self.elems)
        _parse([Modify(R(10, 10, 100, 100), R(10, 10, 0, 1))], self.elems)

        with pytest.raises(ValueError) as err:
            _parse([Insert(R(1, 1, 0, 0))], self.elems)
        assert 'dimensions' in err.value.message

        with pytest.raises(ValueError) as err:
            _parse([Modify(R(10, 10, 100, 100), R(10, 10, 0, 0))],
                   self.elems)
        assert 'dimensions' in err.value.message


class Test_commit(object):

    def setup_class(self):
        self.elems = [
            R(1, 1, 10, 10),
            R(2, 2, 20, 20),
            R(3, 3, 30, 30),
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
            Remove(R(3, 3, 30, 30)),
            Insert(R(10, 5, -5, 5)),  # fix
            Modify(R(1, 1, 10, 10), R(100, 1100, 1000, -1000)),  # fix
            Remove(R(2, 2, 20, 20)),
            Insert(R(4, 4, 4, 4)),
        ]

        _commit(cl, self.changelog, self.eb, self.elems)

    def test_elems_list_updated(self):
        assert self.elems == [
            R(100, 100, 1000, 1000),
            R(5, 5, 5, 5),
            R(4, 4, 4, 4),
        ]

    def test_received_event(self):
        assert self.counter == 1
        assert len(self.received_events) == 1
        assert isinstance(self.received_events[0], Model_Changed)

    def test_event_data_contains_fixed_and_ordered_changes(self):
        assert self.received_events[0].data == [
            Remove(R(3, 3, 30, 30)),
            Remove(R(2, 2, 20, 20)),
            Modify(R(1, 1, 10, 10), R(100, 100, 1000, 1000)),
            Insert(R(5, 5, 5, 5)),
            Insert(R(4, 4, 4, 4)),
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
            R(100, 100, 1000, 1000),
            R(5, 5, 5, 5),
            R(4, 4, 4, 4),
        ]
        assert self.counter == 1
        assert len(self.received_events) == 1
        assert isinstance(self.received_events[0], Model_Changed)
        assert self.received_events[0].data == [
            Remove(R(3, 3, 30, 30)),
            Remove(R(2, 2, 20, 20)),
            Modify(R(1, 1, 10, 10), R(100, 100, 1000, 1000)),
            Insert(R(5, 5, 5, 5)),
            Insert(R(4, 4, 4, 4)),
        ]
        assert self.changelog == [
            ['some', 'old'],
            ['changes', 'here'],
            self.received_events[0].data,
        ]


class Test_CanvasModel(object):
    def setup_class(self):
        self.initial_elements = [
            R(1, 1, 10, 10),
            R(2, 2, 20, 20),
            R(3, 3, 30, 30),
        ]
        self.counter = 0
        self.received_events = []

        def on_change(event):
            self.counter += 1
            self.received_events += [event]

        self.changelist = [  # used for commit
            Insert(R(4, 4, 40, 40)),
            Modify(R(3, 3, 30, 30), R(30, 30, 300, 300)),
            Remove(R(2, 2, 20, 20)),
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
                Insert(R(1, 1, 10, 10)),
                Insert(R(2, 2, 20, 20)),
                Insert(R(3, 3, 30, 30)),
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
                Insert(R(1, 1, 10, 10)),
                Insert(R(2, 2, 20, 20)),
                Insert(R(3, 3, 30, 30)),
            ],
        ]
        evt.data[0] = backup

    def test_commit(self):
        self.model.commit(self.changelist)

    def test_commit_informs_listeners(self):
        assert self.counter == 2
        assert len(self.received_events) == 2
        assert self.received_events[1].data == [
            Remove(R(2, 2, 20, 20)),
            Modify(R(3, 3, 30, 30), R(30, 30, 300, 300)),
            Insert(R(4, 4, 40, 40)),
        ]

    def test_commit_updates_elems(self):
        assert self.model._elems == [
            R(1, 1, 10, 10),
            R(30, 30, 300, 300),
            R(4, 4, 40, 40),
        ]
        assert self.model.elems == self.model._elems

    def test_commit_updates_changelog(self):
        assert self.model._changelog == [
            [
                Insert(R(1, 1, 10, 10)),
                Insert(R(2, 2, 20, 20)),
                Insert(R(3, 3, 30, 30)),
            ],
            [
                Remove(R(2, 2, 20, 20)),
                Modify(R(3, 3, 30, 30), R(30, 30, 300, 300)),
                Insert(R(4, 4, 40, 40)),
            ]
        ]

    def test_cant_inject_changes_to_changelog_through_commit_argument(self):
        self.changelist[2] = 'abc'
        self.changelist.pop(0)
        assert self.received_events[1].data == [
            Remove(R(2, 2, 20, 20)),
            Modify(R(3, 3, 30, 30), R(30, 30, 300, 300)),
            Insert(R(4, 4, 40, 40)),
        ]
        assert self.model._changelog == [
            [
                Insert(R(1, 1, 10, 10)),
                Insert(R(2, 2, 20, 20)),
                Insert(R(3, 3, 30, 30)),
            ],
            [
                Remove(R(2, 2, 20, 20)),
                Modify(R(3, 3, 30, 30), R(30, 30, 300, 300)),
                Insert(R(4, 4, 40, 40)),
            ]
        ]

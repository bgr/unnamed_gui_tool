from my_project.model.CanvasModel import _commit
from my_project.model.elements import Rectangle as R
from my_project.model import Remove, Modify, Insert
from my_project.events import Model_Changed
from hsmpy import EventBus


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

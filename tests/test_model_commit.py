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

    # insert

    def test_insert(self):
        cl = [
            Insert(R(10, 5, -5, 5)),  # fix
            Insert(R(4, 4, 4, 4)),
        ]
        _commit(cl, self.changelog, self.eb, self.elems)
        assert self.elems == [
            R(1, 1, 10, 10),
            R(2, 2, 20, 20),
            R(3, 3, 30, 30),
            R(5, 5, 5, 5),
            R(4, 4, 4, 4),
        ]

    def test_received_event_after_insert(self):
        assert self.counter == 1
        assert len(self.received_events) == 1
        assert isinstance(self.received_events[0], Model_Changed)

    def test_event_data_contains_insert_changes(self):
        assert self.received_events[0].data == [
            Insert(R(5, 5, 5, 5)),
            Insert(R(4, 4, 4, 4)),
        ]

    def test_changes_appended_to_changelog_after_insert(self):
        assert self.changelog == [
            ['some', 'old'],
            ['changes', 'here'],
            self.received_events[0].data,
        ]

    # modify

    def test_modify(self):
        cl = [
            Modify(R(1, 1, 10, 10), R(100, 1100, 1000, -1000)),  # fix
            Modify(R(5, 5, 5, 5), R(55, 5, 5, 5)),
        ]
        _commit(cl, self.changelog, self.eb, self.elems)
        assert self.elems == [
            R(100, 100, 1000, 1000),
            R(2, 2, 20, 20),
            R(3, 3, 30, 30),
            R(55, 5, 5, 5),
            R(4, 4, 4, 4),
        ]

    def test_received_event_after_modify(self):
        assert self.counter == 2
        assert len(self.received_events) == 2
        assert isinstance(self.received_events[1], Model_Changed)

    def test_event_data_contains_modify_changes(self):
        assert self.received_events[1].data == [
            Modify(R(1, 1, 10, 10), R(100, 100, 1000, 1000)),
            Modify(R(5, 5, 5, 5), R(55, 5, 5, 5)),
        ]

    def test_changes_appended_to_changelog_after_modify(self):
        assert self.changelog == [
            ['some', 'old'],
            ['changes', 'here'],
            self.received_events[0].data,
            self.received_events[1].data,
        ]

    # remove

    def test_remove(self):
        cl = [
            Remove(R(3, 3, 30, 30)),
            Remove(R(2, 2, 20, 20)),
        ]
        _commit(cl, self.changelog, self.eb, self.elems)
        assert self.elems == [
            R(100, 100, 1000, 1000),
            R(55, 5, 5, 5),
            R(4, 4, 4, 4),
        ]

    def test_received_event_after_remove(self):
        assert self.counter == 3
        assert len(self.received_events) == 3
        assert isinstance(self.received_events[2], Model_Changed)

    def test_event_data_contains_remove_changes(self):
        assert self.received_events[2].data == [
            Remove(R(3, 3, 30, 30)),
            Remove(R(2, 2, 20, 20)),
        ]

    def test_changes_appended_to_changelog_after_remove(self):
        assert self.changelog == [
            ['some', 'old'],
            ['changes', 'here'],
            self.received_events[0].data,
            self.received_events[1].data,
            self.received_events[2].data,
        ]

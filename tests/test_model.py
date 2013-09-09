from my_project.model import Remove, Modify, Insert, CanvasModel
from my_project.model.elements import Rectangle as R
from my_project.events import Model_Changed
from hsmpy import EventBus


# this suite tests CanvasModel as a whole, makes sure that units it's made of
# are integrated well and that it keeps its integrity by preventing changing
# previously commited elements from outside

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

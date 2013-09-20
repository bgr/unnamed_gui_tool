from hsmpy import EventBus
from my_project.events import Model_Changed
from my_project.model.elements import Insert, Remove, Modify
from my_project.model.elements import Rectangle as R
from my_project.model.CanvasModel import _invert, _undo, _redo, CanvasModel



class Test_invert_changelist:

    def test_invert_one_insert(self):
        cl = [ Insert(R(1, 1, 1, 1)) ]
        assert _invert(cl) == [ Remove(R(1, 1, 1, 1)) ]

    def test_invert_one_remove(self):
        cl = [ Remove(R(1, 1, 1, 1)) ]
        assert _invert(cl) == [ Insert(R(1, 1, 1, 1)) ]

    def test_invert_one_modify(self):
        cl = [ Modify(R(1, 1, 1, 1), R(2, 2, 2, 2)) ]
        assert _invert(cl) == [ Modify(R(2, 2, 2, 2), R(1, 1, 1, 1)) ]

    def test_invert_multiple_inserts(self):
        cl = [
            Insert(R(1, 1, 1, 1)),
            Insert(R(2, 2, 2, 2)),
            Insert(R(3, 3, 3, 3)),
        ]
        assert _invert(cl) == [
            Remove(R(1, 1, 1, 1)),
            Remove(R(2, 2, 2, 2)),
            Remove(R(3, 3, 3, 3)),
        ]

    def test_invert_multiple_removes(self):
        cl = [
            Remove(R(1, 1, 1, 1)),
            Remove(R(2, 2, 2, 2)),
            Remove(R(3, 3, 3, 3)),
        ]
        assert _invert(cl) == [
            Insert(R(1, 1, 1, 1)),
            Insert(R(2, 2, 2, 2)),
            Insert(R(3, 3, 3, 3)),
        ]

    def test_invert_multiple_modifies(self):
        cl = [
            Modify(R(1, 1, 1, 1), R(2, 2, 2, 2)),
            Modify(R(3, 3, 3, 3), R(4, 4, 4, 4)),
            Modify(R(5, 5, 5, 5), R(6, 6, 6, 6)),
        ]
        assert _invert(cl) == [
            Modify(R(2, 2, 2, 2), R(1, 1, 1, 1)),
            Modify(R(4, 4, 4, 4), R(3, 3, 3, 3)),
            Modify(R(6, 6, 6, 6), R(5, 5, 5, 5)),
        ]



class Test_undo:
    def setup_class(self):
        self.eb = EventBus()
        self.event_log = []

        def append_to_event_log(e):
            self.event_log += [e]
        self.eb.register(Model_Changed, append_to_event_log)

    def test_undo_one_insert(self):
        change_log = [
            [ 'previous' ], [ 'changes' ],  # these remain untouched
            [ Insert(R(1, 1, 1, 1)) ],  # undoes only last changelist
        ]
        model_elems = [ R(3, 3, 3, 3), R(1, 1, 1, 1), R(2, 2, 2, 2) ]
        redo_log = [ [ 'future' ], [ 'changes'] ]

        _undo(change_log, redo_log, self.eb, model_elems)

        assert change_log == [
            [ 'previous' ], [ 'changes' ],
        ]
        assert redo_log == [
            [ Insert(R(1, 1, 1, 1)) ],
            [ 'future' ], [ 'changes'],
        ]
        assert model_elems == [ R(3, 3, 3, 3), R(2, 2, 2, 2) ]

        assert len(self.event_log) == 1
        assert self.event_log[-1].data == [ Remove(R(1, 1, 1, 1)) ]  # inverted


    def test_undo_one_remove(self):
        change_log = [
            [ 'previous' ], [ 'changes' ],
            [ Remove(R(1, 1, 1, 1)) ],
        ]
        model_elems = [ R(2, 2, 2, 2) ]
        redo_log = [ [ 'future' ], [ 'changes'] ]

        _undo(change_log, redo_log, self.eb, model_elems)

        assert change_log == [
            [ 'previous' ], [ 'changes' ],
        ]
        assert redo_log == [
            [ Remove(R(1, 1, 1, 1)) ],
            [ 'future' ], [ 'changes'],
        ]
        assert model_elems == [ R(2, 2, 2, 2), R(1, 1, 1, 1) ]

        assert len(self.event_log) == 2
        assert self.event_log[-1].data == [ Insert(R(1, 1, 1, 1)) ]  # inverted


    def test_undo_one_modify(self):
        change_log = [
            [ 'previous' ], [ 'changes' ],
            [ Modify(R(3, 3, 3, 3), R(1, 1, 1, 1)) ],
        ]
        model_elems = [ R(1, 1, 1, 1), R(2, 2, 2, 2) ]
        redo_log = [ [ 'future' ], [ 'changes'] ]

        _undo(change_log, redo_log, self.eb, model_elems)

        assert change_log == [
            [ 'previous' ], [ 'changes' ],
        ]
        assert redo_log == [
            [ Modify(R(3, 3, 3, 3), R(1, 1, 1, 1)) ],
            [ 'future' ], [ 'changes'],
        ]
        assert model_elems == [ R(3, 3, 3, 3), R(2, 2, 2, 2) ]

        assert len(self.event_log) == 3
        assert self.event_log[-1].data == [ Modify(R(1, 1, 1, 1),
                                                   R(3, 3, 3, 3)) ]  # inverted


class Test_redo:
    def setup_class(self):
        self.eb = EventBus()
        self.event_log = []

        def append_to_event_log(e):
            self.event_log += [e]
        self.eb.register(Model_Changed, append_to_event_log)

    def test_redo_one_insert(self):
        change_log = [ [ 'previous' ], [ 'changes' ] ]
        model_elems = [ R(2, 2, 2, 2) ]
        redo_log = [ [ Insert(R(1, 1, 1, 1)) ], [ 'future' ], [ 'changes'] ]

        _redo(change_log, redo_log, self.eb, model_elems)

        assert change_log == [
            [ 'previous' ], [ 'changes' ],
            [ Insert(R(1, 1, 1, 1)) ],
        ]
        assert redo_log == [ [ 'future' ], [ 'changes'] ]
        assert model_elems == [ R(2, 2, 2, 2), R(1, 1, 1, 1) ]

        assert len(self.event_log) == 1
        assert self.event_log[-1].data == [ Insert(R(1, 1, 1, 1)) ]


    def test_redo_one_remove(self):
        change_log = [ [ 'previous' ], [ 'changes' ] ]
        model_elems = [ R(1, 1, 1, 1), R(2, 2, 2, 2) ]
        redo_log = [ [ Remove(R(1, 1, 1, 1)) ], [ 'future' ], [ 'changes'] ]

        _redo(change_log, redo_log, self.eb, model_elems)

        assert change_log == [
            [ 'previous' ], [ 'changes' ],
            [ Remove(R(1, 1, 1, 1)) ],
        ]
        assert redo_log == [ [ 'future' ], [ 'changes'] ]
        assert model_elems == [ R(2, 2, 2, 2) ]

        assert len(self.event_log) == 2
        assert self.event_log[-1].data == [ Remove(R(1, 1, 1, 1)) ]


    def test_redo_one_modify(self):
        change_log = [ [ 'previous' ], [ 'changes' ] ]
        model_elems = [ R(1, 1, 1, 1), R(2, 2, 2, 2) ]
        redo_log = [
            [ Modify(R(1, 1, 1, 1), R(3, 3, 3, 3)) ],
            [ 'future' ], [ 'changes']
        ]

        _redo(change_log, redo_log, self.eb, model_elems)

        assert change_log == [
            [ 'previous' ], [ 'changes' ],
            [ Modify(R(1, 1, 1, 1), R(3, 3, 3, 3)) ],
        ]
        assert redo_log == [ [ 'future' ], [ 'changes'] ]
        assert model_elems == [ R(3, 3, 3, 3), R(2, 2, 2, 2) ]

        assert len(self.event_log) == 3
        assert self.event_log[-1].data == [ Modify(R(1, 1, 1, 1),
                                                   R(3, 3, 3, 3)) ]


    def test_model_one_undo_redo(self):
        model = CanvasModel(self.eb)
        model.commit([ Insert(R(1, 1, 1, 1)) ])
        assert model._elems == [ R(1, 1, 1, 1) ]
        assert model._changelog == [ [ Insert(R(1, 1, 1, 1)) ] ]
        assert model._redolog == []
        model.undo()
        assert model._elems == []
        assert model._changelog == []
        assert model._redolog == [ [ Insert(R(1, 1, 1, 1)) ] ]
        model.redo()
        assert model._elems == [ R(1, 1, 1, 1) ]
        assert model._changelog == [ [ Insert(R(1, 1, 1, 1)) ] ]
        assert model._redolog == []

    def test_model_two_undo_redos(self):
        model = CanvasModel(self.eb)
        model.commit([ Insert(R(1, 1, 1, 1)) ])
        model.commit([ Insert(R(2, 2, 2, 2)) ])
        assert model._elems == [ R(1, 1, 1, 1), R(2, 2, 2, 2) ]
        assert model._changelog == [
            [Insert(R(1, 1, 1, 1))],
            [Insert(R(2, 2, 2, 2))]
        ]
        assert model._redolog == []

        model.undo()
        assert model._elems == [ R(1, 1, 1, 1) ]
        assert model._changelog == [ [ Insert(R(1, 1, 1, 1)) ] ]
        assert model._redolog == [ [ Insert(R(2, 2, 2, 2)) ] ]

        model.undo()
        assert model._elems == []
        assert model._changelog == []
        assert model._redolog == [
            [ Insert(R(1, 1, 1, 1)) ],
            [ Insert(R(2, 2, 2, 2)) ],
        ]

        model.redo()
        assert model._elems == [ R(1, 1, 1, 1) ]
        assert model._changelog == [ [ Insert(R(1, 1, 1, 1)) ] ]
        assert model._redolog == [ [ Insert(R(2, 2, 2, 2)) ] ]

        model.redo()
        assert model._elems == [ R(1, 1, 1, 1), R(2, 2, 2, 2) ]
        assert model._changelog == [
            [Insert(R(1, 1, 1, 1))],
            [Insert(R(2, 2, 2, 2))]
        ]
        assert model._redolog == []

    def test_model_commit_clears_redo_log(self):
        model = CanvasModel(self.eb)
        model.commit([ Insert(R(1, 1, 1, 1)) ])
        model.commit([ Insert(R(2, 2, 2, 2)) ])

        model.undo()

        model.commit([ Insert(R(3, 3, 3, 3)) ])  # this one clears redo log
        assert model._elems == [ R(1, 1, 1, 1), R(3, 3, 3, 3) ]
        assert model._changelog == [
            [Insert(R(1, 1, 1, 1))],
            [Insert(R(3, 3, 3, 3))]
        ]
        assert model._redolog == []

from my_project.statemachine import State, StateMachine
from my_project.statemachine import Transition as T
from my_project.eventbus import EventBus


class Test_door():
    def setup_class(self):
        self.eb = EventBus()
        self.check = {
            'closed_enter': 0,
            'closed_exit': 0,
            'opened_enter': 0,
            'opened_exit': 0,
            'trans_opening': 0,
            'trans_closing': 0,
        }

        def get_callback(key):
            def func():
                print 'callback triggered for "{0}"'.format(key)
                self.check[key] += 1
            return func

        closed = State(on_enter=get_callback('closed_enter'),
                       on_exit=get_callback('closed_exit'),)

        opened = State(on_enter=get_callback('opened_enter'),
                       on_exit=get_callback('opened_exit'),)

        self.trans_map = {
            closed: T('open', opened, get_callback('trans_opening')),
            opened: T('close', closed, get_callback('trans_closing')),
        }
        self.closed = closed
        self.opened = opened
        self.fsm = StateMachine(self.trans_map, self.closed, self.eb)

    def test_before_starting(self):
        self.fsm = StateMachine(self.trans_map, self.closed, self.eb)

        assert self.fsm.current_state is None
        assert all([v == 0 for v in self.check.values()])

    def test_in_closed_state_after_starting(self):
        self.fsm.start()
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 1
        assert self.check.values().count(0) == 5

    def test_transition_to_opened(self):
        self.eb.dispatch('open')
        assert self.fsm.current_state == self.opened
        assert self.check['closed_enter'] == 1
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 0
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 0

    def test_ignores_open_when_already_opened(self):
        self.eb.dispatch('open')
        assert self.fsm.current_state == self.opened
        assert self.check['closed_enter'] == 1
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 0
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 0

    def test_transition_to_closed(self):
        self.eb.dispatch('close')
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 2
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 1
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 1

    def test_ignores_close_when_already_closed(self):
        self.eb.dispatch('close')
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 2
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 1
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 1

    def test_transition_to_opened_again(self):
        self.eb.dispatch('open')
        assert self.fsm.current_state == self.opened
        assert self.check['closed_enter'] == 2
        assert self.check['closed_exit'] == 2
        assert self.check['opened_enter'] == 2
        assert self.check['opened_exit'] == 1
        assert self.check['trans_opening'] == 2
        assert self.check['trans_closing'] == 1

    def test_transition_to_closed_again(self):
        self.eb.dispatch('close')
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 3
        assert self.check['closed_exit'] == 2
        assert self.check['opened_enter'] == 2
        assert self.check['opened_exit'] == 2
        assert self.check['trans_opening'] == 2
        assert self.check['trans_closing'] == 2

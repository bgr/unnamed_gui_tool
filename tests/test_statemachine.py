from my_project.statemachine import State, StateMachine
from my_project.statemachine import Transition as T
from my_project.eventbus import EventBus


class Test_simple_door_machine():
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
            closed: [
                T('open', opened, get_callback('trans_opening')) ],
            opened: [
                T('close', closed, get_callback('trans_closing')) ],
        }
        self.closed = closed
        self.opened = opened
        self.fsm = StateMachine(self.trans_map, self.closed, self.eb)

    def test_transitions_not_allowed_before_start(self):
        assert self.fsm.current_state is None
        assert all([v == 0 for v in self.check.values()])
        assert not self.fsm.can_transition('close')
        assert not self.fsm.can_transition('open')

    def test_in_closed_state_after_starting(self):
        self.fsm.start()
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 1
        assert self.check.values().count(0) == 5
        assert not self.fsm.can_transition('close')
        assert self.fsm.can_transition('open')

    def test_transition_to_opened(self):
        self.eb.dispatch('open')
        assert self.fsm.current_state == self.opened
        assert self.check['closed_enter'] == 1
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 0
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 0
        assert self.fsm.can_transition('close')
        assert not self.fsm.can_transition('open')

    def test_ignores_open_when_already_opened(self):
        self.eb.dispatch('open')
        assert self.fsm.current_state == self.opened
        assert self.check['closed_enter'] == 1
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 0
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 0
        assert self.fsm.can_transition('close')
        assert not self.fsm.can_transition('open')

    def test_transition_to_closed(self):
        self.eb.dispatch('close')
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 2
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 1
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 1
        assert not self.fsm.can_transition('close')
        assert self.fsm.can_transition('open')

    def test_ignores_close_when_already_closed(self):
        self.eb.dispatch('close')
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 2
        assert self.check['closed_exit'] == 1
        assert self.check['opened_enter'] == 1
        assert self.check['opened_exit'] == 1
        assert self.check['trans_opening'] == 1
        assert self.check['trans_closing'] == 1
        assert not self.fsm.can_transition('close')
        assert self.fsm.can_transition('open')

    def test_transition_to_opened_again(self):
        self.eb.dispatch('open')
        assert self.fsm.current_state == self.opened
        assert self.check['closed_enter'] == 2
        assert self.check['closed_exit'] == 2
        assert self.check['opened_enter'] == 2
        assert self.check['opened_exit'] == 1
        assert self.check['trans_opening'] == 2
        assert self.check['trans_closing'] == 1
        assert self.fsm.can_transition('close')
        assert not self.fsm.can_transition('open')

    def test_transition_to_closed_again(self):
        self.eb.dispatch('close')
        assert self.fsm.current_state == self.closed
        assert self.check['closed_enter'] == 3
        assert self.check['closed_exit'] == 2
        assert self.check['opened_enter'] == 2
        assert self.check['opened_exit'] == 2
        assert self.check['trans_opening'] == 2
        assert self.check['trans_closing'] == 2
        assert not self.fsm.can_transition('close')
        assert self.fsm.can_transition('open')


class Test_loops_and_multiple_paths_machine():
    def setup_class(self):
        self.eb = EventBus()
        self.check = {
            'start_enter': 0,
            'start_exit': 0,
            'goal_enter': 0,
            'goal_exit': 0,
            'trans_left': 0,
            'trans_right': 0,
            'trans_loop': 0,
            'trans_restart': 0,
        }

        def get_callback(key):
            def func():
                print 'callback triggered for "{0}"'.format(key)
                self.check[key] += 1
            return func

        start = State(on_enter=get_callback('start_enter'),
                      on_exit=get_callback('start_exit'),)

        goal = State(on_enter=get_callback('goal_enter'),
                     on_exit=get_callback('goal_exit'),)

        self.trans_map = {
            start: [
                T('left', goal, get_callback('trans_left')),
                T('right', goal, get_callback('trans_right')), ],
            goal: [
                T('loop', goal, get_callback('trans_loop')),
                T('restart', start, get_callback('trans_restart')), ],
        }
        self.start = start
        self.goal = goal
        self.fsm = StateMachine(self.trans_map, self.start, self.eb)

    def test_transitions_not_allowed_before_start(self):
        assert self.fsm.current_state is None
        assert all([v == 0 for v in self.check.values()])
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert not self.fsm.can_transition('loop')
        assert not self.fsm.can_transition('restart')

    def test_in_start_state_after_starting(self):
        self.fsm.start()
        assert self.fsm.current_state == self.start
        assert self.check['start_enter'] == 1
        assert self.check.values().count(0) == 7
        assert self.fsm.can_transition('left')
        assert self.fsm.can_transition('right')
        assert not self.fsm.can_transition('loop')
        assert not self.fsm.can_transition('restart')

    def test_transition_to_goal_via_right(self):
        self.eb.dispatch('right')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 1
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 1
        assert self.check['goal_exit'] == 0
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 0
        assert self.check['trans_restart'] == 0
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')

    def test_loop_in_goal(self):
        self.eb.dispatch('loop')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 1
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 2
        assert self.check['goal_exit'] == 1
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 1
        assert self.check['trans_restart'] == 0
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')
        self.eb.dispatch('loop')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 1
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 3
        assert self.check['goal_exit'] == 2
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 2
        assert self.check['trans_restart'] == 0
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')
        self.eb.dispatch('loop')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 1
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 4
        assert self.check['goal_exit'] == 3
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 0
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')

    def test_ignore_left_and_right_events_while_in_goal(self):
        self.eb.dispatch('left')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 1
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 4
        assert self.check['goal_exit'] == 3
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 0
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')
        self.eb.dispatch('right')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 1
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 4
        assert self.check['goal_exit'] == 3
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 0
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')

    def test_restart(self):
        self.eb.dispatch('restart')
        assert self.fsm.current_state == self.start
        assert self.check['start_enter'] == 2
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 4
        assert self.check['goal_exit'] == 4
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 1
        assert self.fsm.can_transition('left')
        assert self.fsm.can_transition('right')
        assert not self.fsm.can_transition('loop')
        assert not self.fsm.can_transition('restart')

    def test_ignore_loop_and_restart_events_while_in_start(self):
        self.eb.dispatch('loop')
        assert self.fsm.current_state == self.start
        assert self.check['start_enter'] == 2
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 4
        assert self.check['goal_exit'] == 4
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 1
        assert self.fsm.can_transition('left')
        assert self.fsm.can_transition('right')
        assert not self.fsm.can_transition('loop')
        assert not self.fsm.can_transition('restart')
        self.eb.dispatch('restart')
        assert self.fsm.current_state == self.start
        assert self.check['start_enter'] == 2
        assert self.check['start_exit'] == 1
        assert self.check['goal_enter'] == 4
        assert self.check['goal_exit'] == 4
        assert self.check['trans_left'] == 0
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 1
        assert self.fsm.can_transition('left')
        assert self.fsm.can_transition('right')
        assert not self.fsm.can_transition('loop')
        assert not self.fsm.can_transition('restart')

    def test_transition_to_goal_via_left(self):
        self.eb.dispatch('left')
        assert self.fsm.current_state == self.goal
        assert self.check['start_enter'] == 2
        assert self.check['start_exit'] == 2
        assert self.check['goal_enter'] == 5
        assert self.check['goal_exit'] == 4
        assert self.check['trans_left'] == 1
        assert self.check['trans_right'] == 1
        assert self.check['trans_loop'] == 3
        assert self.check['trans_restart'] == 1
        assert not self.fsm.can_transition('left')
        assert not self.fsm.can_transition('right')
        assert self.fsm.can_transition('loop')
        assert self.fsm.can_transition('restart')

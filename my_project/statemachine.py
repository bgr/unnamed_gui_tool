from collections import namedtuple as _n

_State = _n('State', 'on_enter, on_exit')
_Transition = _n('Transition', 'triggering_event, to_state,'
                               'on_transition, condition')


def State(on_enter=None, on_exit=None):
    if on_enter is None:
        on_enter = lambda: None
    if on_exit is None:
        on_exit = lambda: None
    return _State(on_enter, on_exit)


def Transition(triggering_event, to_state, on_transition=None, condition=None):
    if on_transition is None:
        on_transition = lambda: None
    if condition is None:
        condition = lambda: True
    return _Transition(triggering_event, to_state, on_transition, condition)


def get_all_transitions(from_state, transition_map):
    return [tr for st, tr in transition_map.items() if from_state == st]


class StateMachine(object):
    def __init__(self, transition_map, initial_state, eventbus):
        assert initial_state in transition_map.keys()
        self._tmap = transition_map
        self._initial_state = initial_state
        self._state = None
        self._valid_transitions = []
        self._eb = eventbus
        self._running = False

    def _setup_transition_listeners(self, from_state):
        # unregister currently registered listeners
        for tr in self._valid_transitions:
            self._eb.unregister(tr.triggering_event, self._attempt_transition)

        self._valid_transitions = get_all_transitions(self._state, self._tmap)

        # register new transitions
        for tr in self._valid_transitions:
            self._eb.register(tr.triggering_event, self._attempt_transition)

    def _attempt_transition(self, evt, aux=None):
        assert evt is not None
        found_trans = [tr for tr in self._valid_transitions
                       if tr.triggering_event == evt]
        assert len(found_trans) == 1, 'must have one transition per event'
        trans = found_trans[0]
        print 'cond: {0}'.format(trans.condition())
        if not trans.condition():
            print "nope"
            return
        self._state.on_exit()
        self._state = trans.to_state
        self._setup_transition_listeners(self._state)
        trans.on_transition()
        self._state.on_enter()
        print "transitioned"

    def start(self):
        assert not self._running
        self._state = self._initial_state
        self._setup_transition_listeners(self._state)
        self._state.on_enter()
        self._running = True

    @property
    def current_state(self):
        return self._state

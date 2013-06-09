from collections import namedtuple as _n

_Transition = _n('Transition', 'triggering_event, to_state,'
                               'on_transition, condition')


class State(object):
    def __init__(self):
        self._interests = {}  # override this value

    @property
    def parent_fsm(self):
        return self._fsm

    @parent_fsm.setter
    def parent_fsm(self, fsm):
        self._fsm = fsm

    def enter(self):
        # override this method
        pass

    def exit(self):
        # override this method
        pass

    @property
    def interests(self):
        return self._interests


def Transition(triggering_event, to_state, on_transition=None, condition=None):
    if on_transition is None:
        on_transition = lambda: None
    if condition is None:
        condition = lambda: True
    return _Transition(triggering_event, to_state, on_transition, condition)


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

        self._valid_transitions = self._tmap[from_state]

        # register new transitions
        print 'found {0} transitions'.format(len(self._valid_transitions))
        print 'setting up transitions from "{0}"'.format(from_state)
        for tr in self._valid_transitions:
            print '    registering for {0}'.format(tr.triggering_event)
            self._eb.register(tr.triggering_event, self._attempt_transition)

    def can_transition(self, event):
        return event in [tr.triggering_event for tr in self._valid_transitions]

    def _attempt_transition(self, event, aux=None):
        assert event is not None
        found_trans = [tr for tr in self._valid_transitions
                       if tr.triggering_event == event]
        assert len(found_trans) == 1, 'must have one transition per event'
        trans = found_trans[0]
        print 'found transition for event "{0}": {1}'.format(event, trans)
        if not trans.condition():
            print "nope"
            return
        self._state.exit()
        self._state = trans.to_state
        self._setup_transition_listeners(self._state)
        trans.on_transition()
        self._state.enter()
        print "transitioned"

    def start(self):
        assert not self._running
        self._state = self._initial_state
        self._setup_transition_listeners(self._state)
        self._state.enter()
        self._running = True

    @property
    def current_state(self):
        return self._state

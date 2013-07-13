import hsmpy
from hsmpy import HSM, State, CompositeState, Initial, Event, EventBus
from hsmpy import Transition as T


class Step(Event):
    pass


class Test_hsmpy(object):

    def setup_class(self):

        self.worked = 'no'

        def blah(evt, hsm):
            self.worked = 'yes'

        self.states = {
            'top': CompositeState({
                'left': State(),
                'right': State(),
            })
        }
        self.trans = {
            'top': {
                Initial: T('left'),
            },
            'left': {
                Step: T('right', action=blah),
            }
        }
        self.eb = EventBus()
        self.hsm = HSM(self.states, self.trans)

    def test_start(self):
        self.hsm.start(self.eb)

    def test_seems_fine(self):
        self.eb.dispatch(Step())
        assert self.worked == 'yes'
        assert self.hsm._current_state.name == 'right'

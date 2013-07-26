import hsmpy  # check that import works
from hsmpy import HSM, State, Initial, Event, EventBus
from hsmpy import Transition as T


class Step(Event):
    pass


class Test_hsmpy(object):

    def setup_class(self):

        self.worked = 'no'

        def blah(evt, hsm):
            self.worked = 'yes'

        self.states = {
            'top': State({
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
        assert len(self.hsm.current_state_set) == 2

import pytest
from my_project.util import Dummy


class Test_Dummy():
    def test_raises_on_non_kwargs(self):
        with pytest.raises(TypeError):
            Dummy(3)

    def test_reset_no_initial(self):
        d = Dummy()
        assert d.__dict__ == { '_original_kwargs': {} }
        d.x = 3
        d.abcd = 'yay'
        assert d.x == 3
        assert d.abcd == 'yay'
        d.reset()
        assert not hasattr(d, 'x')
        assert not hasattr(d, 'abcd')
        assert d.__dict__ == { '_original_kwargs': {} }
        d.reset()
        assert d.__dict__ == { '_original_kwargs': {} }

    def test_reset_with_initial(self):
        d = Dummy(x=3, abcd='abcd')
        assert d.x == 3
        assert d.abcd == 'abcd'
        assert d.__dict__ == {
            'x': 3,
            'abcd': 'abcd',
            '_original_kwargs': { 'x': 3, 'abcd': 'abcd'}
        }
        d.reset()
        assert d.x == 3
        assert d.abcd == 'abcd'
        assert d.__dict__ == {
            'x': 3,
            'abcd': 'abcd',
            '_original_kwargs': { 'x': 3, 'abcd': 'abcd'}
        }
        d.x = 44
        d.abcd = 'hello'
        d.new = 1
        assert d.x == 44
        assert d.abcd == 'hello'
        assert d.new == 1
        d.reset()
        assert d.x == 3
        assert d.abcd == 'abcd'
        assert not hasattr(d, 'new')

import pytest
from my_project.util import Record


class Test_base_class:

    def test_instantiate(self):
        r = Record()
        assert r.keys == ()

    def test_str(self):
        r = Record()
        assert str(r) == 'Record()'

    def test_comparable_with_tuple(self):
        assert Record() == ()

    def test_comparable_with_another_Record(self):
        assert Record() == Record()

    def test_doesnt_take_arguments(self):
        with pytest.raises(TypeError) as err:
            Record(1)
        assert 'Record takes 0 items, got 1' in err.value

        with pytest.raises(TypeError) as err:
            Record(1, b=2)
        assert 'Record takes 0 items, got 2' in err.value

    def test_cannot_set_keys(self):
        r = Record()
        with pytest.raises(TypeError) as err:
            r.a = 2
        assert 'Record is immutable' in err.value

    def test_cannot_change_keys_of_class(self):
        with pytest.raises(TypeError):
            Record.keys = ('a',)
            Record.keys = ()  # reset if above passes so other tests don't fail

    def test_cannot_change_keys_of_instance(self):
        r = Record()
        with pytest.raises(TypeError) as err:
            r.keys = ('a',)
            Record.keys = ()  # reset so other tests don't fail
        assert 'Record is immutable' in err.value


class Test_inheritance:

    def setup_class(self):
        class C(Record):
            keys = ('a', 'bc')
        self.C = C

    def test_instantiate_with_positional_args(self):
        self.C(2, 3)

    def test_instantiate_with_keyword_args(self):
        self.C(a=2, bc=3)
        self.C(bc=3, a=3)

    def test_instantiate_with_mixed_args(self):
        self.C(2, bc=3)

    def test_isinstance_of_Record(self):
        assert isinstance(self.C(2, 3), Record)

    def test_str(self):
        assert str(self.C(2, 3)) == 'C(a=2, bc=3)'
        assert str(self.C(2, bc=3)) == 'C(a=2, bc=3)'
        assert str(self.C(bc=3, a=2)) == 'C(a=2, bc=3)'

    def test_comparable_with_tuple(self):
        assert self.C(2, 3) == (2, 3)
        assert self.C(a=2, bc=3) == (2, 3)
        assert self.C(2, bc=3) == (2, 3)
        assert self.C(bc=3, a=2) == (2, 3)

    def test_comparable_with_another_C(self):
        assert self.C(2, 3) == self.C(bc=3, a=2)

    def test_can_access_properties(self):
        c = self.C(2, 3)
        assert c.a == 2
        assert c.bc == 3

    def test_can_access_via_index(self):
        c = self.C(bc=3, a=2)
        assert c[0] == 2
        assert c[1] == 3

    def test_cannot_change_values(self):
        c = self.C(2, 3)
        with pytest.raises(TypeError) as err:
            c.a = 4
        assert 'C is immutable' in err.value

    def test_cannot_change_values_via_index(self):
        c = self.C(2, 3)
        with pytest.raises(TypeError) as err:
            c[0] = 4
        assert 'C is immutable' in err.value

    def test_cannot_change_keys_of_class(self):
        with pytest.raises(TypeError):
            self.C.keys = ('de',)
            self.C.keys = ('a', 'bc')  # reset so other tests don't fail

    def test_cannot_change_keys_of_instance(self):
        c = self.C(2, 3)
        with pytest.raises(TypeError) as err:
            c.keys = ('de',)
            c.keys = ('a', 'bc')  # reset so other tests don't fail
        assert 'C is immutable' in err.value

    def test_cannot_pass_keyword_arguments_with_wrong_keys(self):
        with pytest.raises(TypeError) as err:
            self.C(d=2, dc=3)
        assert 'Invalid' in err.value.message

        with pytest.raises(TypeError) as err:
            self.C(2, dc=3)
        assert 'Invalid' in err.value.message


    @pytest.mark.parametrize('create', [
        lambda self: self.C(2),
        lambda self: self.C(2, 3, 4),
        lambda self: self.C(2, 3, a=2, bc=3),
        lambda self: self.C(2, a=2, bc=3),
        lambda self: self.C(2, bc=2, a=3),
        lambda self: self.C(a=2, bc=2, d=3),
        lambda self: self.C(2, 3, a=2),
        lambda self: self.C(2, 3, bc=3),
        lambda self: self.C(**{'a': 2}),
        lambda self: self.C(**{'a': 2, 'bc': 3, 'd': 4}),
        lambda self: self.C(2, **{'bc': 3, 'd': 4}),
    ])
    def test_cannot_wrong_number_of_arguments(self, create):
        with pytest.raises(TypeError) as err:
            create(self)
        assert 'takes' in err.value.message


    @pytest.mark.parametrize('create', [
        lambda self: self.C(2, a=2),
        lambda self: self.C(2, a=3),
        lambda self: self.C(2, **{'a': 3}),
    ])
    def test_cannot_pass_same_keyword_arguments_along_positional(self, create):
        with pytest.raises(TypeError) as err:
            create(self)
        assert 'already specified' in err.value.message



class Test_many_arguments:

    def setup_class(self):
        class MyFiveThings(Record):
            keys = ('a', 'bc', 'defg', 'h', 'i')
        self.C = MyFiveThings

    @pytest.mark.parametrize('create', [
        lambda self: self.C(2, 3, 4, 5, 6),
        lambda self: self.C(a=2, bc=3, defg=4, h=5, i=6),
        lambda self: self.C(2, bc=3, defg=4, h=5, i=6),
        lambda self: self.C(2, 3, defg=4, h=5, i=6),
        lambda self: self.C(2, 3, 4, h=5, i=6),
        lambda self: self.C(2, 3, 4, 5, i=6),
        lambda self: self.C(**{'a': 2, 'bc': 3, 'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(2, **{'bc': 3, 'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, **{'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, 4, **{'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, 4, 5, **{'i': 6}),
        lambda self: self.C(a=2, **{'bc': 3, 'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(defg=4, **{'bc': 3, 'a': 2, 'h': 5, 'i': 6}),
        lambda self: self.C(bc=3, h=5, **{'defg': 4, 'a': 2, 'i': 6}),
        lambda self: self.C(a=2, bc=3, defg=4, **{'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, h=5, **{'defg': 4, 'i': 6}),
        lambda self: self.C(2, 3, i=6, h=5, **{'defg': 4}),
    ])
    def test_args(self, create):
        c = create(self)
        assert c == (2, 3, 4, 5, 6)
        assert c == self.C(2, 3, 4, 5, 6)
        assert str(c) == 'MyFiveThings(a=2, bc=3, defg=4, h=5, i=6)'
        assert c.defg == 4
        assert c[2] == 4

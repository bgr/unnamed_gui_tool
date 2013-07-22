import pytest
from my_project.util import Record, is_valid_identifier


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
            keys = ('x', 'bc', 'defg', 'h', 'i')
        self.C = MyFiveThings

    @pytest.mark.parametrize('create', [
        lambda self: self.C(2, 3, 4, 5, 6),
        lambda self: self.C(x=2, bc=3, defg=4, h=5, i=6),
        lambda self: self.C(2, bc=3, defg=4, h=5, i=6),
        lambda self: self.C(2, 3, defg=4, h=5, i=6),
        lambda self: self.C(2, 3, 4, h=5, i=6),
        lambda self: self.C(2, 3, 4, 5, i=6),
        lambda self: self.C(**{'x': 2, 'bc': 3, 'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(2, **{'bc': 3, 'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, **{'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, 4, **{'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, 4, 5, **{'i': 6}),
        lambda self: self.C(x=2, **{'bc': 3, 'defg': 4, 'h': 5, 'i': 6}),
        lambda self: self.C(defg=4, **{'bc': 3, 'x': 2, 'h': 5, 'i': 6}),
        lambda self: self.C(bc=3, h=5, **{'defg': 4, 'x': 2, 'i': 6}),
        lambda self: self.C(x=2, bc=3, defg=4, **{'h': 5, 'i': 6}),
        lambda self: self.C(2, 3, h=5, **{'defg': 4, 'i': 6}),
        lambda self: self.C(2, 3, i=6, h=5, **{'defg': 4}),
    ])
    def test_args(self, create):
        c = create(self)
        assert c == (2, 3, 4, 5, 6)
        assert c == self.C(2, 3, 4, 5, 6)
        assert str(c) == 'MyFiveThings(x=2, bc=3, defg=4, h=5, i=6)'
        assert c.defg == 4
        assert c[2] == 4



class Test_duplicated_keys_in_subclass:

    def setup_class(self):
        class Base(Record):
            keys = ('x', 'a', 'b')
        self.Base = Base

    def test_repeat_some(self):
        class Ch(self.Base):
            keys = ('a', 'c')
        assert Ch.keys == ('x', 'a', 'b', 'c')

        class Grch(Ch):
            keys = ('a', 'c', 'd')
        assert Grch.keys == ('x', 'a', 'b', 'c', 'd')

    def test_repeat_all(self):
        class Ch(self.Base):
            keys = ('a', 'x', 'b')
        assert Ch.keys == ('x', 'a', 'b')

        class Grch(Ch):
            keys = ('x', 'd', 'b', 'c', 'a')
        assert Grch.keys == ('x', 'a', 'b', 'd', 'c')



class Test_grandchildren:

    def setup_class(self):
        class Base(Record):
            keys = ('p1', 'mm')


        class Ch1(Base):
            keys = ('c11', 'c12')

        class Grch11(Ch1):
            keys = ('a111', 'g112')

        class Grch12(Ch1):
            keys = ['b', 'g122']


        class Ch2(Base):
            keys = ('c21', 'c22', 'c23')

        class Grch21(Ch2):
            keys = ['g211']

        class Grch22(Ch2):
            keys = ('x', 'yz')

        self.Base = Base
        self.Ch1 = Ch1
        self.Ch2 = Ch2
        self.Grch11 = Grch11
        self.Grch12 = Grch12
        self.Grch21 = Grch21
        self.Grch22 = Grch22


    def test_child_keys_appended_to_parent_keys(self):
        assert self.Base.keys == ('p1', 'mm')
        assert self.Ch1.keys == ('p1', 'mm', 'c11', 'c12')
        assert self.Ch2.keys == ('p1', 'mm', 'c21', 'c22', 'c23')
        assert self.Grch11.keys == ('p1', 'mm', 'c11', 'c12', 'a111', 'g112')
        assert self.Grch12.keys == ('p1', 'mm', 'c11', 'c12', 'b', 'g122')
        assert self.Grch21.keys == ('p1', 'mm', 'c21', 'c22', 'c23', 'g211')
        assert self.Grch22.keys == ('p1', 'mm', 'c21', 'c22', 'c23', 'x', 'yz')

    def test_cannot_instantiate_without_parents_keys(self):
        with pytest.raises(TypeError) as err:
            self.Ch1(2, 3)
        assert 'takes 4' in err.value.message

        with pytest.raises(TypeError) as err:
            self.Ch2(c21=4, c22=5, c23=6)
        assert 'takes 5' in err.value.message

        with pytest.raises(TypeError) as err:
            self.Grch22(4, 5, 6, 7, 8)
        assert 'takes 7' in err.value.message

    def test_instantiate_requires_parents_keys(self):
        self.Ch1(p1=2, mm=3, c11=4, c12=5)
        self.Ch2(p1=2, mm=3, c21=4, c22=5, c23=6)
        self.Grch22(p1=2, mm=3, c21=4, c22=5, c23=6, x=7, yz=8)

    def test_order_of_keyword_arguments(self):
        c = self.Ch1(c12=5, mm=3, p1=2, c11=4)
        gc = self.Grch22(2, 3, yz=8, c21=4, c23=6, c22=5, x=7)
        assert c  == (2, 3, 4, 5)
        assert gc == (2, 3, 4, 5, 6, 7, 8)

    def test_can_get_values_via_keys(self):
        assert self.Ch1(p1=2, mm=3, c11=4, c12=5).p1 == 2
        assert self.Ch1(p1=2, mm=3, c11=4, c12=5).c11 == 4
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8).p1 == 2
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8).c21 == 4
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8).c22 == 5
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8).x == 7
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8).yz == 8

    def test_can_get_values_via_index(self):
        assert self.Ch1(p1=2, mm=3, c11=4, c12=5)[0] == 2
        assert self.Ch1(p1=2, mm=3, c11=4, c12=5)[2] == 4
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8)[0] == 2
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8)[2] == 4
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8)[3] == 5
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8)[5] == 7
        assert self.Grch22(2, 3, 4, c22=5, c23=6, x=7, yz=8)[6] == 8

    def test_isinstance(self):
        assert isinstance(self.Base(2, 3), Record)
        c = self.Ch1(5, 6, 7, 8)
        assert isinstance(c, Record)
        assert isinstance(c, self.Base)
        gc = self.Grch11(3, 4, 5, 6, 7, 8)
        assert isinstance(gc, Record)
        assert isinstance(gc, self.Base)
        assert isinstance(gc, self.Ch1)
        assert not isinstance(gc, self.Ch2)
        assert not isinstance(gc, self.Grch12)

    def test_cannot_change_values_via_properties(self):
        b = self.Base(2, 3)
        with pytest.raises(TypeError):
            b.p1 = 3
        assert b == (2, 3)

        c = self.Ch1(5, 6, 7, 8)
        with pytest.raises(TypeError):
            c.p1 = 3
        with pytest.raises(TypeError):
            c.c12 = 3
        assert c == (5, 6, 7, 8)

        gc = self.Grch11(3, 4, 5, 6, 7, 8)
        with pytest.raises(TypeError):
            gc.p1 = 3
        with pytest.raises(TypeError):
            gc.c12 = 3
        with pytest.raises(TypeError):
            gc.g112 = 3
        assert gc == (3, 4, 5, 6, 7, 8)

    def test_cannot_change_values_via_index(self):
        b = self.Base(2, 3)
        with pytest.raises(TypeError):
            b[1] = 2
        assert b == (2, 3)

        c = self.Ch1(5, 6, 7, 8)
        with pytest.raises(TypeError):
            c[1] = 2
        with pytest.raises(TypeError):
            c[3] = 2
        assert c == (5, 6, 7, 8)

        gc = self.Grch11(3, 4, 5, 6, 7, 8)
        with pytest.raises(TypeError):
            gc[3] = 3
        with pytest.raises(TypeError):
            gc[5] = 3
        assert gc == (3, 4, 5, 6, 7, 8)

    def test_cannot_mess_with_keys(self):
        with pytest.raises(TypeError):
            self.Base.keys = ('a', 'b',)
        with pytest.raises(TypeError):
            self.Ch1.keys = ('a', 'b',)
        with pytest.raises(TypeError):
            self.Grch12.keys = ('a', 'b',)

        b = self.Base(2, 3)
        c = self.Ch1(5, 6, 7, 8)
        gc = self.Grch11(3, 4, 5, 6, 7, 8)
        with pytest.raises(TypeError):
            b.keys = ('a', 'b',)
        with pytest.raises(TypeError):
            c.keys = ('a', 'b',)
        with pytest.raises(TypeError):
            gc.keys = ('a', 'b',)

        assert b.keys == ('p1', 'mm')
        assert c.keys == ('p1', 'mm', 'c11', 'c12')
        assert gc.keys == ('p1', 'mm', 'c11', 'c12', 'a111', 'g112')
        assert self.Base.keys == ('p1', 'mm')
        assert self.Ch1.keys == ('p1', 'mm', 'c11', 'c12')
        assert self.Ch2.keys == ('p1', 'mm', 'c21', 'c22', 'c23')
        assert self.Grch11.keys == ('p1', 'mm', 'c11', 'c12', 'a111', 'g112')
        assert self.Grch12.keys == ('p1', 'mm', 'c11', 'c12', 'b', 'g122')
        assert self.Grch21.keys == ('p1', 'mm', 'c21', 'c22', 'c23', 'g211')
        assert self.Grch22.keys == ('p1', 'mm', 'c21', 'c22', 'c23', 'x', 'yz')



class Test_key_naming_format:

    @pytest.mark.parametrize('key', [
        '',
        ' ',
        '9',
        '99',
        '9a',
        'a b',
        'a-b',
        'a!',
        '!',
        '+',
        'a+b',
        'a+',
        'def',
        'is',
        'for',
    ])
    def test_regex_disallowed(self, key):
        assert not is_valid_identifier(key)
        with pytest.raises(TypeError) as err:
            class X(Record):
                keys = (key,)
        assert 'Invalid keys' in err.value

    @pytest.mark.parametrize('key', [
        'a',
        'hey',
        'hElLo',
        'HELLO',
        'H9_l__lo',
        '_9',
    ])
    def test_regex_allowed(self, key):
        assert is_valid_identifier(key)

        class X(Record):
            keys = (key,)
        assert X.keys == (key,)

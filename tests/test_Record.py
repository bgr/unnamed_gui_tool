import pytest
from my_project.util import Record


class Test_base_class:
    def test_can_instantiate_without_args(self):
        r = Record()
        assert r._frozen

    def test_raises_when_passed_args(self):
        with pytest.raises(TypeError):
            Record(2)

    def test_raises_when_passed_kwargs(self):
        with pytest.raises(TypeError):
            Record(a=2)

    def test_raises_when_assigning_new_fields(self):
        r = Record()
        with pytest.raises(TypeError):
            r.x = 2

    def test_replace_cannot_add_new_fields(self):
        r = Record()
        with pytest.raises(TypeError):
            r.replace(x=2)


class Test_inheritance:
    def test_without_init(self):
        class B(Record):
            pass
        b = B()
        assert b._frozen

    def test_empty_init(self):
        class B(Record):
            def __init__(self):
                pass
        b = B()
        assert b._frozen

    def test_init_with_one_arg(self):
        class B(Record):
            def __init__(self, hello):
                self.hello = hello
        b = B(2)
        assert b.hello == 2
        assert b._frozen

    def test_init_with_one_arg_with_default(self):
        class B(Record):
            def __init__(self, hello=4):
                self.hello = hello
        b = B(2)
        assert b.hello == 2
        assert b._frozen

        b = B()
        assert b.hello == 4
        assert b._frozen

    def test_init_with_multiple_args(self):
        class B(Record):
            def __init__(self, a, b, c=3, hello=4):
                self.a, self.b, self.c, self.hello = a, b, c, hello
        b = B(1, 2, 5)
        assert (b.a, b.b, b.c, b.hello) == (1, 2, 5, 4)
        assert b._frozen

    def test_replace_one_value(self):
        class B(Record):
            def __init__(self, a, b, c=3, hello=4):
                self.a, self.b, self.c, self.hello = a, b, c, hello
        b1 = B(1, 2, 5)
        b2 = b1.replace(c=22)
        assert (b1.a, b1.b, b1.c, b1.hello) == (1, 2, 5, 4)
        assert (b2.a, b2.b, b2.c, b2.hello) == (1, 2, 22, 4)
        assert b1._frozen
        assert b2._frozen

    def test_replace_multiple_values(self):
        class B(Record):
            def __init__(self, a, b, c=3, hello=4):
                self.a, self.b, self.c, self.hello = a, b, c, hello
        b1 = B(1, 2, 5)
        b2 = b1.replace(c=22, a=11)
        assert (b1.a, b1.b, b1.c, b1.hello) == (1, 2, 5, 4)
        assert (b2.a, b2.b, b2.c, b2.hello) == (11, 2, 22, 4)
        assert b1._frozen
        assert b2._frozen

    def test_cant_modify_after_replace(self):
        class B(Record):
            def __init__(self, a, b, c=3, hello=4):
                self.a, self.b, self.c, self.hello = a, b, c, hello
        b = B(1, 2, 5)
        b2 = b.replace(c=22)

        with pytest.raises(TypeError):
            b.a = 3
        with pytest.raises(TypeError):
            b2.a = 3
        with pytest.raises(TypeError):
            b.x = 3
        with pytest.raises(TypeError):
            b2.x = 3

    def test_accepts_unhashable_arguments_if_converted_manually(self):
        class B(Record):
            def __init__(self, a):
                self.a = tuple(a)

        b = B([3])
        assert b.a == (3,)
        assert type(b.a) == tuple

    def test_raises_when_assigned_unhashable_fields(self):
        class B(Record):
            def __init__(self, a):
                self.a = a
        with pytest.raises(TypeError) as err:
            B([3])
        assert 'hashable' in err.value.message


    def test_raises_when_init_leaves_unassigned_fields(self):
        class B(Record):
            def __init__(self, a, b):
                self.a = a
        with pytest.raises(TypeError) as err:
            B(1, 2)
        assert 'all fields' in err.value.message

    def test_raises_when_init_assigns_extra_fields(self):
        class B(Record):
            def __init__(self, a, b):
                self.a = a
                self.b = b
                self.c = 1
        with pytest.raises(TypeError) as err:
            B(1, 2)
        assert 'all fields' in err.value.message

    def test_raises_when_init_assigns_wrong_fields(self):
        class B(Record):
            def __init__(self, a):
                self.blah = a
        with pytest.raises(TypeError) as err:
            B(2)
        assert 'all fields' in err.value.message

    def test_raises_when_trying_to_reassign(self):
        class B(Record):
            def __init__(self, a):
                self.a = a
        b = B(2)
        with pytest.raises(TypeError):
            b.a = 3
        with pytest.raises(TypeError):
            b.x = 3

    def test_raises_on_init_with_varargs(self):
        with pytest.raises(TypeError):
            class B(Record):
                def __init__(self, *args):
                    pass

    def test_raises_on_init_with_kwargs(self):
        with pytest.raises(TypeError):
            class B(Record):
                def __init__(self, **kwargs):
                    pass



class Test_grandchildren:
    def setup_class(self):
        class B(Record):
            def __init__(self, a, b, c=3):
                self.a = a
                self.b = b
                self.c = c
        self.B = B

    def test_uses_parents_init_when_no_init(self):
        class C(self.B):
            pass

        c = C(1, 2)
        assert c.a == 1
        assert c.b == 2
        assert c.c == 3
        assert c._frozen

    def test_raises_when_not_enough_arguments(self):
        class C(self.B):
            pass
        with pytest.raises(TypeError):
            C()
        with pytest.raises(TypeError):
            C(1)

    def test_init_with_no_arguments_ok_if_sets_fields(self):
        class C(self.B):
            def __init__(self):
                self.a = 2
                self.b = 3
                self.c = 4
        c = C()
        assert c.a == 2
        assert c.b == 3
        assert c.c == 4
        assert c._frozen

    def test_init_with_no_arguments_ok_if_sets_fields_via_parent_init(self):
        class C(self.B):
            def __init__(slf):
                super(C, slf).__init__(2, 3, 4)
        c = C()
        assert c.a == 2
        assert c.b == 3
        assert c.c == 4
        assert c._frozen

    def test_init_can_declare_additional_fields(self):
        class C(self.B):
            def __init__(slf, d, e=5):
                slf.d = d
                super(C, slf).__init__(1, 2)
                slf.e = e
        c = C(4)
        assert (c.a, c.b, c.c, c.d, c.e) == (1, 2, 3, 4, 5)
        assert c._frozen

    def test_raises_when_init_leaves_unassigned_parents_fields(self):
        class C(self.B):
            def __init__(self):
                self.a = 1
                self.c = 1
        with pytest.raises(TypeError) as err:
            C()
        assert 'all fields' in err.value.message

    def test_raises_when_init_leaves_unassigned_own_fields(self):
        class C(self.B):
            def __init__(slf, d, e=5):
                slf.d = d
                super(C, slf).__init__(1, 2)
        with pytest.raises(TypeError) as err:
            C(3)
        assert 'all fields' in err.value.message



# TODO: __eq__

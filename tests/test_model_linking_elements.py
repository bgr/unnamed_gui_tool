import pytest


def test_get_links_for_element():
    el1 = R(1, 2, 3, 4)
    el2 = R(2, 3, 4, 5)
    el3 = R(3, 4, 5, 6)
    l1 = Link(el1, el2)
    l2 = Link(el2, el1)
    l3 = Link(el1, el3)
    l4 = Link(el1, el3)  # duplicate allowed
    l5 = Link(el3, el1)
    l6 = Link(el2, el3)
    l7 = Link(el3, el3)

    all_elems = [el1, el2, el3, l1, l2, l3, l4, l5, l6, l7]

    links_el1 = get_links_for(el1, all_elems)
    assert links_el1 == [l1, l2, l3, l4, l5]

    links_el2 = get_links_for(el2, all_elems)
    assert links_el2 == [l1, l2, l6]

    links_el3 = get_links_for(el3, all_elems)
    assert links_el3 == [l3, l4, l5, l6, l7]


# link with nested element

# model should check on commit:
#   * link start and end must be in same model

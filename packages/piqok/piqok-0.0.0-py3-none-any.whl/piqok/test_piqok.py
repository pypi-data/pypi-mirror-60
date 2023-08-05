from typing import List
from piqok.piqok import Json


class Person(Json):
    name: str
    age: int


def test_person():
    p = Person({
        'name': 'Gilad',
        'age': 40
    })

    assert p.name == 'Gilad'
    assert p.age == 40


class Bag(Json):
    size: float
    items: List[str]


def test_bag():
    b = Bag({
        'size': 30.4,
        'items': ['apple', 'map']
    })

    assert b.size == 30.4
    assert b.items[1] == 'map'

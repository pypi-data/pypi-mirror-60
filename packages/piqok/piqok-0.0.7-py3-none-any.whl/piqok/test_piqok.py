import json
from typing import List
from piqok import Json


class Person(Json):
    name: str
    age: float
    pets: List[str]
    friends: List['Person']


def someone():
    return json.loads("""
        {
            "name": "Gilad",
            "age": 40,
            "pets": ["Bisli", "Bamba"],
            "friends": [
                {
                    "name": "Uri",
                    "age": 40
                },
                {
                    "name": "Chen",
                    "age": 40
                }
            ]
        }
        """)


def test_person_hasattr():
    p = Person(someone())
    assert hasattr(p, 'name')
    assert hasattr(p, 'age')
    assert hasattr(p, 'pets')
    assert hasattr(p, 'friends')

    assert not hasattr(p, 'dada')
    assert not hasattr(p, 'baba')


def test_person_getattr():
    p = Person(someone())

    assert type(p.name) is str
    assert type(p.age) is int
    assert type(p.pets) is list

    assert p.name == 'Gilad'
    assert p.age == 40
    assert p.pets == ["Bisli", "Bamba"]
    assert p.friends[0].name == 'Uri'
    assert p.friends[1].age == 40


def test_person_setattr():
    Moshe = someone()
    p = Person(Moshe)
    p.age = 41
    p.name = 'Moshe'
    p.pets = ['Mishmish']
    p.friends = [Moshe]

    assert p.age == 41
    assert p.name == 'Moshe'
    assert p.pets == ['Mishmish']

    assert p.friends[0].age == 41
    assert p.friends[0].name == 'Moshe'


def test_person_call():
    p = someone()

    assert Json.obj(Person(p)) == p

import json
from typing import List
from piqok import Json


class Person(Json):
    name: str
    age: float
    friends: List['Person']


def test_a_person_with_a_bag():
    p = Person(json.loads("""
        {
            "name": "Gilad",
            "age": 40,
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
        """))
    assert p.age == 40
    assert p.friends[0].name == 'Uri'
    assert p.friends[1].age == 40

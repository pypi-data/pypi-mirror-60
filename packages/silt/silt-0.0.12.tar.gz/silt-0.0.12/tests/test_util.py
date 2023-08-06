from __future__ import annotations
import pytest

import json
from jigu.util import JSONSerializable, JSONDeserializable


class Good(JSONSerializable):
    """JSONSerializable should implement to_dict()"""

    def to_dict(self) -> dict:
        return {"test": "abc"}


class Good2(JSONSerializable):
    """to_dict() unfortunately is a misnomer, you can return anything that is json.dumps() can serialize
    normally, including other JSONSerializable instances."""

    def to_dict(self) -> int:
        return 5


class Bad(JSONSerializable):
    pass


class GoodBlank(JSONDeserializable):
    @classmethod
    def from_dict(cls) -> GoodBlank:
        cls()


class BadBlank(JSONDeserializable):
    pass


class GoodDog(JSONSerializable, JSONDeserializable):
    """JSONDeserializable must implement classmethod from_dict()."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def to_dict(self) -> dict:
        return {"name": self.name, "age": str(self.age)}

    @classmethod
    def from_dict(cls, data: dict) -> GoodDog:
        return cls(data["name"], int(data["age"]))


@pytest.fixture
def s_good():
    return Good()


@pytest.fixture
def s_good2():
    return Good2()


@pytest.fixture
def d_good():
    return GoodBlank()


@pytest.fixture
def dog_json():
    return '{"name": "william", "age": "20"}'


def test_jsonserializable_interface():
    a = Good()
    b = Good2()
    assert a.to_json()
    assert b.to_json()
    with pytest.raises(TypeError):
        Bad()  # shouldn't be able to instantiate


def test_to_json(s_good, s_good2):
    r = json.loads(s_good.to_json())
    assert type(r) == dict
    assert "test" in r
    assert r["test"] == "abc"


def test_jsondeserializable_interface():
    a = GoodBlank()
    with pytest.raises(TypeError):
        BadBlank()  # shouldn't be able to instantiate


def test_serialize_deserialize(dog_json):
    a = GoodDog("william", 20)
    b = GoodDog.from_dict(json.loads(dog_json))
    assert a == b  # equality will be implemented for us
    assert json.loads(a.to_json()) == json.loads(dog_json)

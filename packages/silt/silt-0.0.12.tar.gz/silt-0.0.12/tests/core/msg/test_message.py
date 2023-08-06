import pytest

from jigu.core.msg import Message


class GoodMessage(Message):
    """Message needs to implement property type, and msg_value"""

    type = "hello"

    def msg_value(self) -> dict:
        return {"test": "abc"}


class GoodMessage2(Message):
    @property
    def type(self) -> str:
        return "hello"

    def msg_value(self) -> dict:
        return {"test": "abc"}


class NoNameMessage(Message):
    def msg_value(self) -> dict:
        return {"test": "abc"}


class NoMsgValueMessage(Message):
    type = "no_msg_value_message"
    pass


def test_message_interface():
    a = GoodMessage().to_dict()
    b = GoodMessage2().to_dict()

    assert "type" in a
    assert a["type"] == "hello"
    assert "value" in a
    assert type(a["value"]) == dict
    assert "test" in a["value"]
    assert a["value"]["test"] == "abc"
    assert "type" in b
    assert "value" in b
    assert a == b
    with pytest.raises(TypeError):
        x = NoNameMessage()
    with pytest.raises(TypeError):
        x = NoMsgValueMessage()

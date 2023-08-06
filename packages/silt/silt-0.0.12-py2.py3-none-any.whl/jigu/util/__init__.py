from __future__ import annotations

import uuid
import abc
import json
import hashlib
import base64

from typing import Any, Optional, List, Dict, Type, Callable

from jigu.util.validation import is_acc_address, is_val_address


def abbreviate(addr: str) -> str:
    if is_acc_address(addr):
        return f"{addr[0:8]}...{addr[-4:]}"
    elif is_val_address(addr):
        return f"{addr[0:15]}...{addr[-4:]}"
    else:
        return addr


def try_to_dict(o):
    try:
        return o.to_dict()
    except AttributeError:
        return None


def generate_salt() -> str:
    """Generate a 4 bytes salt."""
    return uuid.uuid4().hex[:4]


def hash_amino(txdata: str) -> str:
    """Get the transaction hash from Amino-encoded Transaction in base64."""
    return hashlib.sha256(base64.b64decode(txdata)).digest().hex()


def list_to_dict(key: str, deserialize: Callable) -> Callable:
    def transform_list_to_dict(data: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        if data:
            return {o[key]: deserialize(o) for o in data}
        return {}

    return transform_list_to_dict


def pretty_repr(title: str, *items: Tuple[str, str]) -> str:
    """Returns a basic fancy __repr__"""
    newline = "\n"
    return f"""--{title}--
{newline.join(f"  {item[0]:<25}{item[1]}" for item in items)}
"""


def serialize_to_json(item: Any, sort: bool = False, debug: bool = False) -> str:
    """This is used in case the serialization strategy must be used outside of JSONSerializable"""
    return json.dumps(
        item,
        indent=2 if debug else None,
        sort_keys=sort,
        separators=(",", ":") if not debug else None,
        default=try_to_dict,
    )


class JSONSerializable(object, metaclass=abc.ABCMeta):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, JSONSerializable):
            return self.to_dict() == other.to_dict()
        else:
            return self.to_dict() == other

    @abc.abstractmethod
    def to_dict(self) -> Any:
        """Implement this, returning a JSON-serializable object that will be
        called by to_json()."""
        raise NotImplementedError("JSONSerializable must implement to_dict()")

    def to_json(self, sort: bool = False) -> str:
        return serialize_to_json(self.to_dict(), sort=sort)


class JSONDeserializable(object, metaclass=abc.ABCMeta):
    """Can deserialize back into an Jigu object from JSON-friendly Python object."""

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data):
        raise NotImplementedError("JSONDeserializable must implement from_dict()")

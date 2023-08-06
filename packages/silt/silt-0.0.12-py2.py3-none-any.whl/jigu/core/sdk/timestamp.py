from __future__ import annotations

from jigu.util import JSONSerializable, JSONDeserializable

from datetime import datetime
from dateutil import parser


class Timestamp(datetime, JSONSerializable, JSONDeserializable):

    # instead of __init__ as datetime is immutable
    def __new__(cls, dt: datetime):
        return datetime.__new__(
            cls,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo,
        )

    def __str__(self) -> str:
        return self.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self) -> str:
        return f"Timestamp({self.strftime('%Y-%m-%d %H:%M:%S...')})"

    def to_dict(self) -> str:
        # TODO: fix microsecond precision
        return self.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @classmethod
    def from_dict(cls, data: str) -> Timestamp:
        return Timestamp(dt=parser.isoparse(data))

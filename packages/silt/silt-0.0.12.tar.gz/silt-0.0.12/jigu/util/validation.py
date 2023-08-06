import bech32
from jigu.error import ValidationError


def is_bech32(data: str) -> bool:
    return bech32.bech32_decode != (None, None)


def is_acc_address(data: str) -> bool:
    return (
        is_bech32(data)
        and data.startswith("terra")
        and not data.startswith("terravaloper")
        and not data.startswith("terrapub")
        and not data.startswith("terravaloperpub")
    )


def is_val_address(data: str) -> bool:
    return (
        is_bech32(data)
        and data.startswith("terravaloper")
        and not data.startswith("terravaloperpub")
    )


def validate_acc_address(data: str) -> None:
    if not is_acc_address(data):
        raise ValidationError(f"'{data}' is not a valid Terra address")


def validate_val_address(data: str) -> None:
    if not is_val_address(data):
        raise ValidationError(f"'{data}' is not a valid Terra validator operator address")

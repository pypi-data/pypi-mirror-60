import pytest

from typing import List

from jigu.key.mnemonic import MnemonicKey


@pytest.fixture
def acc1() -> dict:
    return {
        "mnemonic": "wonder caution square unveil april art add hover spend smile proud admit modify old copper throw crew happy nature luggage reopen exhibit ordinary napkin",
        "address": "terra1jnzv225hwl3uxc5wtnlgr8mwy6nlt0vztv3qqm",
        "pubkey": "terrapub1addwnpepqt8ha594svjn3nvfk4ggfn5n8xd3sm3cz6ztxyugwcuqzsuuhhfq5nwzrf9",
        "val_address": "terravaloper1jnzv225hwl3uxc5wtnlgr8mwy6nlt0vztraasg",
        "val_pubkey": "terravaloperpub1addwnpepqt8ha594svjn3nvfk4ggfn5n8xd3sm3cz6ztxyugwcuqzsuuhhfq5y7accr",
    }


@pytest.fixture
def acc2() -> dict:
    return {
        "mnemonic": "speak scatter present rice cattle sight amateur novel dizzy wheel cannon mango model sunset smooth appear impose want lunar tattoo theme zero misery flower",
        "address": "terra1ghvjx8jyn3m4v94nwdzjjevlsqz3uevvvhvedp",
        "pubkey": "terrapub1addwnpepqdavy7mkxxjl8dd5mck7tef8rrxmmhzs3ts0grn3laczdjstt6vtjfsumau",
        "val_address": "terravaloper1ghvjx8jyn3m4v94nwdzjjevlsqz3uevvvcqyaj",
        "val_pubkey": "terravaloperpub1addwnpepqdavy7mkxxjl8dd5mck7tef8rrxmmhzs3ts0grn3laczdjstt6vtj7qrqv6",
    }


@pytest.fixture
def acc3() -> dict:
    return {
        "mnemonic": "pool december kitchen crouch robot relax oppose system virtual spread pistol obtain vicious bless salmon drive repeat when frost summer render shed bone limb",
        "address": "terra1a3l5xudduhrk43whxm65hpyh3lqspx94vhlx6h",
        "pubkey": "terrapub1addwnpepqvaz9qpllrwu7l4nf3wzgnz6vn54x4snsw7r7kfmygf06dq2tjkc2plmywj",
        "val_address": "terravaloper1a3l5xudduhrk43whxm65hpyh3lqspx94vcnm2y",
        "val_pubkey": "terravaloperpub1addwnpepqvaz9qpllrwu7l4nf3wzgnz6vn54x4snsw7r7kfmygf06dq2tjkc2k0yll5",
    }


@pytest.fixture
def accounts(acc1, acc2, acc3) -> List[dict]:
    return [acc1, acc2, acc3]


def compare(w: MnemonicKey, data: dict):
    assert w.mnemonic == data["mnemonic"]
    assert w.acc_address == data["address"]
    assert w.val_address == data["val_address"]
    assert w.acc_pubkey == data["pubkey"]
    assert w.val_pubkey == data["val_pubkey"]


@pytest.mark.slow
def test_from_mnemonic(accounts):
    for account in accounts:
        w = MnemonicKey(account["mnemonic"])
        compare(w, account)


@pytest.mark.slow
def test_random_wallet():
    w = MnemonicKey.generate()
    assert len(w.mnemonic.split()) == 24
    assert w.mnemonic != MnemonicKey.generate().mnemonic

# Jigu - The Python SDK for Terra

Jigu (지구, or __Earth__ in Korean) is the official Python SDK (Software Development Kit) for Terra, which allows developers to write software that integrates with the blockchain and its ecosystem. You can find the official documentation at our SDK [docs site](https://jigu.terra.money).


## Quick Start

> Note: Requires **Python v3.6+**. Python 2 is not supported, as support for it discontinued on Jan 01, 2020.

First, install the library off PyPI.

```shell
$ pip install jigu
```

Jigu makes it easy to interact with a node running `terra-core`.

```python
from jigu import Terra
from jigu.networks import SOJU
from jigu.wallet import Wallet

from jigu.core.denoms import MicroLuna

wallet = Wallet.generate() # create a random wallet
terra = Terra(**SOJU) # connect to soju testnet

# check my balances!
luna = terra.account(wallet.address).balances[MicroLuna]
```

## A Tour of Jigu

### The `Terra` instance

The `jigu.Terra` instance represents your connection parameters for contacting a node, and provides an intuitive, pythonic interface for accessing data on the Terra blockchain. By default, it will connect to Columbus-3 mainnet.

```python
>>> from jigu import Terra
>>>
>>> terra = Terra()
Node(https://lcd.terra.dev -> columbus-3)
```

### Accounts

```python
>>> gazua = terra.account("terra1rf9xakxf97a49qa5svsf7yypjswzkutqfclur8")
>>> gazua.address
'terra1rf9xakxf97a49qa5svsf7yypjswzkutqfclur8'
>>> gazua.validator
Validator(terravaloper1rf9xakxf97a49qa5svsf7yypjswzkutqfhnpn5)
>>> gazua.validator.val_address
'terravaloper1rf9xakxf97a49qa5svsf7yypjswzkutqfhnpn5'
```
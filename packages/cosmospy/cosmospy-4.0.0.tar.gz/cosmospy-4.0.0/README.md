[![Build Status](https://travis-ci.com/hukkinj1/cosmospy.svg?branch=master)](https://travis-ci.com/hukkinj1/cosmospy)
[![codecov.io](https://codecov.io/gh/hukkinj1/cosmospy/branch/master/graph/badge.svg)](https://codecov.io/gh/hukkinj1/cosmospy)
[![PyPI version](https://badge.fury.io/py/cosmospy.svg)](https://badge.fury.io/py/cosmospy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# cosmospy

<!--- Don't edit the version line below manually. Let bump2version do it for you. -->
> Version 4.0.0

> Tools for Cosmos wallet management and offline transaction signing

## Installing
Installing from PyPI repository (https://pypi.org/project/cosmospy):
```bash
pip install cosmospy
```

## Usage

### Generating a wallet
```python
from cosmospy import generate_wallet
wallet = generate_wallet()
```
The value assigned to `wallet` will be a dictionary just like:
```python
{
    "private_key": "6dcd05d7ac71e09d3cf7da666709ebd59362486ff9e99db0e8bc663570515afa",
    "public_key": "03e8005aad74da5a053602f86e3151d4f3214937863a11299c960c28d3609c4775",
    "address": "cosmos1jkc7hv9j92gj7r6sqq0l630lv4kqyac7t2dj2t"
}
 ```

### Converter functions
#### Private key to public key
```python
from cosmospy import privkey_to_pubkey
pubkey = privkey_to_pubkey("6dcd05d7ac71e09d3cf7da666709ebd59362486ff9e99db0e8bc663570515afa")
 ```
#### Public key to address
```python
from cosmospy import pubkey_to_address
addr = pubkey_to_address("03e8005aad74da5a053602f86e3151d4f3214937863a11299c960c28d3609c4775")
 ```
#### Private key to address
```python
from cosmospy import privkey_to_address
addr = privkey_to_address("6dcd05d7ac71e09d3cf7da666709ebd59362486ff9e99db0e8bc663570515afa")
 ```

### Signing transactions
```python
from cosmospy import Transaction
tx = Transaction(
    privkey="26d167d549a4b2b66f766b0d3f2bdbe1cd92708818c338ff453abde316a2bd59",
    account_num=11335,
    sequence=0,
    fee=1000,
    gas=70000,
    memo="",
    chain_id="cosmoshub-3",
    sync_mode="sync",
)
tx.add_transfer(recipient="cosmos103l758ps7403sd9c0y8j6hrfw4xyl70j4mmwkf", amount=387000)
tx.add_transfer(recipient="cosmos1lzumfk6xvwf9k9rk72mqtztv867xyem393um48", amount=123)
pushable_tx = tx.get_pushable()
```
One or more token transfers can be added to a transaction by calling the `add_transfer` method.

When the transaction is fully prepared, calling `get_pushable_tx` will return a signed transaction in the form of a JSON string. This can be used as request body when calling the `POST /txs` endpoint of the [Cosmos REST API](https://cosmos.network/rpc).

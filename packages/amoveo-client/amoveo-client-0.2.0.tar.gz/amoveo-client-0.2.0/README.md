# Python Amoveo Client

## Introduction

Amoveo is a pretty new blockchain, the mainnet was launched on March, 2nd.

it's not a fork of any existing coin, but it implements number of interesting concepts: on-chain governance, oracles working on top of the coin itself, lightning channels, turing-complete smart-contracts on top of channels, and last but not least -- prediction markets, they're one of main purposes of the project.

Amoveo shows steady growth of userbase and has number of services, implemented by 3rd parties, working with this coin: there're mobile wallets, desktop app, mining pools etc.

Right now it's trading on two small exchanges not listed on CMC, and trade volume including OTC deals is like tens of BTCs per day.

The project itself is open source and community-driven, its main developer is Zack Hess, former CTO of Augur and Aeternity.

To find more information you can look through https://amoveo.io -- it's community site, recently launched. Also, join the community at https://t.me/amoveo


## Infrastructure
To work with API you need a running full node. Full node is written in Erlang and available from project repository at https://github.com/zack-bitcoin/amoveo

The full node can be set up using instructions from official repo: https://github.com/zack-bitcoin/amoveo/blob/master/docs/getting-started/build_intro.md

Once node’s up you need to sync it according to https://github.com/zack-bitcoin/amoveo/blob/master/docs/getting-started/sync.md

NB: it’s vital to switch `sync_mode` to `normal` after the first sync (and after every restart).

Also, take care of security, ‘cause `epmd` opens the maintenance port: https://github.com/zack-bitcoin/amoveo/blob/master/docs/getting-started/firewall.md

The full node opens two ports: 8080 for external api, it should be visible from internet too to sync, and 8081 on `lo` listening for internal api (which is effectively erlang methods calls via HTTP).

In case of troubles with sync, etc. you can use our own full node at 88.99.245.31:8080

List of open full nodes is available on https://veoscan.io

Nice public block explorer (supporting tx hashes) is https://explorer.veopool.pw

Good reference of deposit/withdraw UI is on https://qtrade.io


## Install and use

### Install
```
pip install amoveo-client
```
### Examples

Init
```
AMOVEO_CONF = {
  'EXPLORER': ...,
  'NODE': ...
}
amoveo_client = AmoveoClient(AMOVEO_CONF)
```

Create address and private key
```
address, private_key, passphrase = amoveo_client.generate_wallet()
```

Get current balance
It can return 0 if account has never been funded
```
balance = amoveo_client.balance(address)
balance_in_satoshi = amoveo_client.balance(address, in_satoshi=True)
```

Get transaction by tx hash
```
amoveo.get_tx(tx_hash)
```

Get account transactions
```
amoveo.account_txs(address)
```

Send transaction. Call `Amoveo.send`. It determines tx type needed, forms the transaction payload, serializes it and sends to full node.
Please note, there should be at least 1 satoshi left on the account to make spending transaction correct (i.e. you can’t transfer the whole amount, just amount - 1 satoshi, excluding fee).
```
acc = amoveo.account(_to)
tx_typ = "create_account_tx" if acc == "empty" else "spend_tx"
fee = 152168 if acc == "empty" else 61657
tx = amoveo_client.prepare_tx(tx_typ, amount, fee, _from, _to)
sign = amoveo.sign(tx, private_key)
transaction_id = amoveo_client.send_tx(tx, sign)
```

Get current blockchain height
```
height = amoveo_client.last_block()
```

Get block and its tx’s. Response contains several nested arrays, first with transactions and theirs signatures (MQ…) and the second with theirs hashes in the corresponding order.
```
block_data = amoveo_client.last_block(block_height)
```

Pending transactions. Response contains current pending transactions. Unfortunately, they have no hashes included in response but one can map them using theirs signatures.
```
amoveo_client.pending_tx()
```
```
curl --request GET \
        --url http://amoveo.node/ \
        --header 'content-type: application/json' \
        --data '["mempool"]'
```


Other methods
```
amoveo_client.account(address)

```

account not funded
```
curl --request GET \
    --url http://amoveo.node/ \
    --header 'content-type: application/json' \
    --data '["account", "BIkj6yP84pYqRP8LDjKnO6Ae4cQSP5NiX6x5jRpWUcYWyR87uM6pf90ZhAH/J0g3Fm35O+Kf6a0mAqzsuvTPmyU="]'
> ["ok",0]  # account not funded yet.
```

account funded
```
curl --request GET \
    --url http://amoveo.node/ \
    --header 'content-type: application/json' \
    --data '["account", "BH8sPvGR4DqpnasL3zVJ9C068bPHbtBEOLV4rhEQvqt1Y8NH9ceXFozaFctuSaAtgb0SZ5kiuPxZZY6jGM+BDHw="]'
> ["ok",["acc",74679577,25,"BH8sPvGR4DqpnasL3zVJ9C068bPHbtBEOLV4rhEQvqt1Y8NH9ceXFozaFctuSaAtgb0SZ5kiuPxZZY6jGM+BDHw=",0,"B2onx55azio9R/ndLoPk/26ohys8Ihj2bJK4m1XzZWA="]]
[result, [request type, balance, ...]]
```

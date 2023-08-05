from .node import AmoveoNode
from .explorer import AmoveoExplorer
from .sign import sign, generate_wallet
from .serializer import get_tx_hash
from decimal import Decimal
from .excepts import NotEnoughMoney
import logging


logger = logging.getLogger('amoveo')


class AmoveoClient:
    def __init__(self, conf):
        """
        Implement all methods from node, explorer, sign
        :param conf: dict {'EXPLORER': ..., 'NODE': ...}
        """
        explorer = AmoveoExplorer(conf.get("EXPLORER"))
        self.get_tx = explorer.get_tx
        self.account_txs = explorer.account_txs

        node = AmoveoNode(conf.get("NODE"))
        self.last_block = node.last_block
        self.block = node.block
        self.account = node.account
        self.pending_tx = node.pending_tx
        self.prepare_tx = node.prepare_tx
        self.send_tx = node.send_tx

    sign = staticmethod(sign)
    generate_wallet = staticmethod(generate_wallet)

    def balance(self, address: str, in_satoshi=False):
        """
        Get balance in veo or satoshi.
        :param address:
        :return:
        """
        res = self.account(address)
        if res == 0:
            return 0
        else:
            try:
                amount = res[1]
                if in_satoshi:
                    return amount
                else:
                    return amount / 1e8
            except:
                raise Exception

    def tx_confirmations(self, tx_hash):
        tx = self.get_tx(tx_hash)
        confirmations = self.last_block() - tx["blocknumber"]
        return confirmations

    def get_txs(self, block_data):
        """
        Get txs from block_data.
        :param block_data:
            [
              "ok",
              [
                -6,
                [
                  -6,
                  [
                    "signed",
                    [
                      "spend",
                      "BBrLVfwGFhMTmnZ6RZrBTwPXYHnsvi9Y8hL0EkWaoWM9qWxTiS8AWPdVWd7Cz6p4hv9moSC6m1ekbxi2DVYhwvo=",
                      1221,
                      61657,
                      "BKHzjIT1+N58gkU12i7kgtn/BlFOshonqoBId13Ap1r6Rhie/7CLb/ldDHa0iKk+3++umO86mbIcXee+GnveuCo=",
                      63398162,
                      0
                    ],
                    "MEQCIDcvqA4lDOfVt48P90s5A2QT9zdVD3Bl15UuN/N/dvptAiAUlxIT7ES6dUtVoeyM6D1D+46xESKFLxfSKmNvDRZXnQ==",
                    [
                      -6
                    ]
                  ]
                ],
                [
                  -6,
                  "cQuiBwY20dqcQPmrkHYMyrQwo/x3ho7cFuB1lVjMGQQ="
                ]
              ]
            ]

        :return:
            txs: list
             [ [
                "signed",
                [
                  "spend",
                  "BBrLVfwGFhMTmnZ6RZrBTwPXYHnsvi9Y8hL0EkWaoWM9qWxTiS8AWPdVWd7Cz6p4hv9moSC6m1ekbxi2DVYhwvo=",
                  1221,
                  61657,
                  "BKHzjIT1+N58gkU12i7kgtn/BlFOshonqoBId13Ap1r6Rhie/7CLb/ldDHa0iKk+3++umO86mbIcXee+GnveuCo=",
                  63398162,
                  0
                ],
                "MEQCIDcvqA4lDOfVt48P90s5A2QT9zdVD3Bl15UuN/N/dvptAiAUlxIT7ES6dUtVoeyM6D1D+46xESKFLxfSKmNvDRZXnQ==",
                [
                  -6
                ]
              ], ...
             ]
             hashes: list (str)
        """
        try:
            txs, hashes = block_data[1][1:], block_data[2][1:]
        except IndexError:
            txs, hashes = [], []

        return self.parse_txs(txs, hashes)

    def parse_txs(self, raw_txs, hashes=None):
        """
        Convert to list of tx dict values.
        :param raw_txs
            [
                [
                    "signed",
                    [
                        "spend",
                        "BGJJ08FDDFCQ8w3G3AbrL/qjEQJXWZsLqIqrmyoH3Vhy709+UlkJLgA2KarZTfXQg5E46jd918Nl9AkexDUKNzI=",
                        5965,
                        61657,
                        "BEodyMSNL3mDGZwhb1a34YLLapqMWJmBXvcIA9BwN+UA3eHFSPeHj1jDxElAlGBGQehVlxuQH696yVbNfQubRfs=",
                        44343288,
                        0
                    ],
                    "MEYCIQDwxypFRNzvPU8WTPM9nxQ5x0dgM1xJTCXrKl6+4S3zcQIhALKP7ohD12HUzpN6kY/v5SXK0dPkLKSK4FN+cl8wWHyw",
                    [
                        -6
                    ]
                ],
            ...]
        :param hashes: list(str)
        =>
        :return: list (dict)
            [
                {
                    'hash':
                    'sign': tx_sign,
                    'from':
                    'to':
                    'amount':
                }
            ]
        """
        txs = []
        for ind, tx_raw in enumerate(raw_txs):
            tx_sign = tx_raw[2]
            tx = tx_raw[1]

            if tx[0] in ["spend", "create_acc_tx"]:
                txs.append({
                    'hash': hashes[ind] if hashes else get_tx_hash(tx),
                    'sign': tx_sign,
                    'from': tx[1],
                    'to': tx[4],
                    'amount': tx[5]
                })
        return txs

    def send(self, _from, private_key, _to, value):
        """
        Send `value` coins.
        :param _from: (str) address
        :param private_key: (str) private key
        :param _to: (str) address
        :param value: value as is
        :return:
        """
        value = int(value * Decimal(1e8))

        # get balance
        balance = self.balance(_from, in_satoshi=True)

        # find out tx type
        #       - if wallet is empty - create_account_tx
        #       - else spend_tx
        res = self.account(_to)
        tx_typ = "create_account_tx" if res in ["empty", 0] else "spend_tx"
        fee = 152168 if res in ["empty", 0] else 61657
        value_with_fee = value + fee

        if balance - value_with_fee < 0:
            raise NotEnoughMoney(f"Balance on {_from} is not enough for transaction")

        logger.info(f"Prepare VEO tx, tx_typ: {tx_typ}, value: {value}, fee: {fee}, _from: {_from}, _to: {_to}")
        res = self.prepare_tx(tx_typ, value, fee, _from, _to)

        # sign transaction
        sign_str = self.sign(res, private_key)

        # send transaction
        transaction_id = self.send_tx(res, sign_str)
        return transaction_id
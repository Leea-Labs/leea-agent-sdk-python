import os.path

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder
import json
from os import urandom
from leea_agent_sdk.logger import logger
from eth_account.messages import encode_defunct
from eth_utils import keccak
from web3.eth import Contract


class Web3Instance:
    account: LocalAccount
    w3: Web3

    def __init__(self, keystore_path: str, keystore_password: str):
        self.path = keystore_path
        self.password = keystore_password

    def create_wallet(self):
        if not os.path.isfile(self.path):
            logger.info("Could not open/read keystore file, creating a new one")
            self.account: LocalAccount = Account.create(urandom(256))
            logger.info(f"New account created: {self.account.address}")
            encrypted = self.account.encrypt(self.password)
            with open(self.path, "w") as f:
                f.write(json.dumps(encrypted))
                logger.info(f"New account was saved as file: {self.path}")
                f.close()
            return

        with open(self.path) as keyfile:
            encrypted_file = json.load(keyfile)
            private_key = Account.decrypt(encrypted_file, self.password)
            self.account: LocalAccount = Account.from_key(private_key)
            logger.info(f"Using existing account: {self.account.address}")
            keyfile.close()

    def connect(self, endpoint: str):
        w3: Web3 = Web3(Web3.HTTPProvider(endpoint))
        w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account), layer=0
        )
        self.w3 = w3
        return self.w3.is_connected()

    def sign_message(self, msg: str) -> str:
        signed_msg = self.account.sign_message(encode_defunct(keccak(text=msg)))
        return signed_msg.signature.to_0x_hex()

    def verify_message(self, msg: str, signature: str) -> bool:
        try:
            Account.recover_message(
                encode_defunct(keccak(text=msg)), signature=signature
            )
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def register(self, contract_address: str, fee: int, name: str) -> bool:
        with open(
            "contracts/contracts/artifacts/aregistry/AgentRegistry.abi", "r"
        ) as abi_file:
            abi = abi_file.read().rstrip()
            contract_instance: Contract = self.w3.eth.contract(
                address=contract_address, abi=abi
            )
            registered: bool = contract_instance.functions.isAgent(
                self.account.address
            ).call()
            if registered is True:
                logger.exception("Agent address already registered")
                return False
            gas = contract_instance.functions.registerAgent(
                self.account.address, fee, name
            ).estimate_gas()
            balance = self.w3.eth.get_balance(self.account.address)
            if balance < gas:
                logger.exception(
                    f"Agent balance is less than gas required, please top up by {gas - balance}"
                )
                return False
            unsent_tx = contract_instance.functions.registerAgent(
                self.account.address, fee, name
            ).build_transaction({"from": self.account.address,"nonce": self.w3.eth.get_transaction_count(self.account.address)})
            signed_tx = self.w3.eth.account.sign_transaction(unsent_tx, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"Transaction hash {signed_tx}")
            txn_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            logger.info(f"Transaction receipt {txn_receipt}")
            return True

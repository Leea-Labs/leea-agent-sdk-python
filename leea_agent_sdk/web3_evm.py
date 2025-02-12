import os.path
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder
import json
from leea_agent_sdk.logger import logger
from eth_account.messages import encode_defunct
from eth_utils import keccak
from web3.eth import Contract
from os import urandom


class Web3InstanceEVM:
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
            return

        with open(self.path) as keyfile:
            private_key = Account.decrypt(json.load(keyfile), "12345678")
            self.account: LocalAccount = Account.from_key(private_key)
            logger.info(f"Using existing account: {self.account.address}")

    def get_agent_id(self) -> str:
        return self.account.address

    def connected(self):
        return self.w3.is_connected()

    def sign_message(self, msg: bytes) -> (str, bytes):
        signed_msg = self.account.sign_message(encode_defunct(keccak(primitive=msg)))
        return self.account.address, signed_msg.signature.to_0x_hex()

    def verify_message(self, msg: bytes, signature: str) -> bool:
        try:
            Account.recover_message(
                encode_defunct(keccak(primitive=msg)), signature=signature
            )
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def set_web3_provider(self, w3: Web3):
        w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account), layer=0
        )
        self.w3 = w3

    def register(self, contract_address: str, fee: int, name: str) -> bool:
        contract_instance: Contract = self.get_registry_contract(contract_address)
        registered: bool = contract_instance.functions.isAgent(
            self.account.address
        ).call()
        if registered is True:
            logger.exception("Agent address already registered")
            return False
        gas = self.get_gas(self.account.address, fee, name)
        balance = self.w3.eth.get_balance(self.account.address)
        if balance < gas:
            logger.exception(
                f"Agent balance is less than gas required, please top up by {gas - balance}"
            )
            return False
        tx_hash = contract_instance.functions.registerAgent(
            self.account.address, fee, name
        ).transact()
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        txn_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        logger.info(f"Transaction receipt {txn_receipt}")
        return True

    def get_gas(self, contract_address: str, fee: int, name: str) -> int:
        contract_instance: Contract = self.get_registry_contract(contract_address)
        gas = contract_instance.functions.registerAgent(
            self.account.address, fee, name
        ).estimate_gas()
        return gas

    def get_registry_contract(self, contract_address: str) -> Contract:
        with open(
            "contracts/contracts/artifacts/aregistry/AgentRegistry.abi", "r"
        ) as abi_file:
            abi = abi_file.read().rstrip()
            contract_instance: Contract = self.w3.eth.contract(
                address=contract_address, abi=abi
            )
            return contract_instance

    def get_public_key(self):
        return self.account.address

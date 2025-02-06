from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder
import json
from os import urandom
from leea_agent_sdk.logger import logger
from eth_account.messages import encode_defunct
from eth_utils import keccak


class Web3Instance:
    account: LocalAccount
    w3: Web3

    def __init__(self, keystorePath: str, keystorePassword: str):
        self.path = keystorePath
        self.password = keystorePassword

    def create_wallet(self):
        try:
            keyfile = open(self.path)
        except OSError:
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
            encryptedFile = json.load(keyfile)
            priv_key = Account.decrypt(encryptedFile, self.password)
            self.account: LocalAccount = Account.from_key(priv_key)
            logger.info(f"Using existing account: {self.account.address}")
            keyfile.close()

    def connect(self, endpointURL: str):
        w3: Web3 = Web3(Web3.HTTPProvider(endpointURL))
        w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(self.account), layer=0
        )
        self.w3 = w3

    def sign_message(self, msg: str) -> str:
        signedMessage = self.account.sign_message(encode_defunct(keccak(text=msg)))
        return signedMessage.signature.to_0x_hex()

    def verify_message(self, msg: str, signature: str) -> bool:
        result: bool = Account.recover_message(
            encode_defunct(keccak(text=msg)), signature=signature
        )
        return result

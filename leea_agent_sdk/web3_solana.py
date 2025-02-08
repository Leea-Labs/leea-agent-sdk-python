from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.signature import Signature
from solders.pubkey import Pubkey


class Web3InstanceSolana:
    client: Client
    keypair: Keypair

    def __init__(self, keypair_path: str):
        with open(keypair_path) as file:
            data = file.read()
            self.keypair = Keypair.from_json(data)
            assert self.keypair.pubkey().is_on_curve()

    def get_public_key(self) -> str:
        return self.keypair.pubkey().__str__()

    def sign_message(self, msg: bytes) -> str:
        return self.keypair.sign_message(msg).__str__()

    def verify_message(self, pub_key: str, msg: bytes, sig: str) -> bool:
        pubkey: Pubkey = Pubkey.from_string(pub_key)
        signature: Signature = Signature.from_string(sig)
        return signature.verify(pubkey, msg)

    def connect(self, url: str) -> bool:
        self.client = Client(url)
        return self.client.is_connected()

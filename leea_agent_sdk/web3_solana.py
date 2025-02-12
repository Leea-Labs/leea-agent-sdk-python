from eth_utils import keccak
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

    def get_agent_id(self) -> str:
        return self.keypair.pubkey().__str__()

    def sign_message(self, msg: str) -> str:
        return self.keypair.sign_message(keccak(text=msg)).__str__()
    
    def verify_message(self, agent_id: str, msg: str, sig: str) -> bool:
        pubkey: Pubkey = Pubkey.from_string(agent_id)
        signature: Signature = Signature.from_string(sig)
        return signature.verify(pubkey, keccak(text=msg))

    def connect(self, url: str) -> bool:
        self.client = Client(url)
        return self.client.is_connected()

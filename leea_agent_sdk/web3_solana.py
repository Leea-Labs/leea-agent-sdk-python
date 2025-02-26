from solders.keypair import Keypair
from solders.signature import Signature
from solders.pubkey import Pubkey
import subprocess
import base58


class Web3InstanceSolana:
    keypair: Keypair
    fee: str

    def __init__(self, url, keypair_path: str):
        with open(keypair_path) as file:
            data = file.read()
            self.keypair = Keypair.from_json(data)
            assert self.keypair.pubkey().is_on_curve()
        # register agent
        secret_key = base58.b58encode(self.keypair.secret())
        subprocess.run(
            ["./leea_agent_sdk/program/registry-client", self.fee, secret_key, url],
            check=True,
        )
        print("Registered!")

    def get_public_key(self) -> str:
        return self.keypair.pubkey().__str__()

    def sign_message(self, msg: bytes) -> str:
        return self.keypair.sign_message(msg).__str__()

    def verify_message(self, pub_key: str, msg: bytes, sig: str) -> bool:
        pubkey: Pubkey = Pubkey.from_string(pub_key)
        signature: Signature = Signature.from_string(sig)
        return signature.verify(pubkey, msg)

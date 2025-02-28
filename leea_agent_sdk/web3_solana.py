from solders.keypair import Keypair
from solders.signature import Signature
from solders.pubkey import Pubkey
import platform
import os
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
        secret_key = base58.b58encode(self.keypair.secret())
        subprocess.run(
            [self._get_registry_client_executable(), self.fee, secret_key, url],
            check=True,
        )
        print("Registered!")

    def _get_registry_client_executable(self):
        system = ({"Darwin": "macos"}.get(platform.system(), "linux")).lower()
        arch = {"x64": "x86_64", "arm64": "aarch64"}.get(platform.machine(), "x86_64")
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "registry-client", f"registry-client-{system}-{arch}")

    def get_public_key(self) -> str:
        return self.keypair.pubkey().__str__()

    def sign_message(self, msg: bytes) -> str:
        return self.keypair.sign_message(msg).__str__()

    def verify_message(self, pub_key: str, msg: bytes, sig: str) -> bool:
        pubkey: Pubkey = Pubkey.from_string(pub_key)
        signature: Signature = Signature.from_string(sig)
        return signature.verify(pubkey, msg)

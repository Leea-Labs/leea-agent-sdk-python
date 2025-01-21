from leea_agent_sdk.web3 import Web3Instance

inst = Web3Instance("leea_acc.json", "12345678")


def test_create_wallet():
    inst.create_wallet()
    assert inst.account.address is not None, "address cant be empty"


def test_sign_verify():
    inst.create_wallet()
    sig: str = inst.sign_message("Hello World")
    ver: bool = inst.verify_message("Hello World", sig)
    assert ver is True


def test_connect():
    connected: bool = inst.connect("https://sepolia.base.org")
    assert connected is True

def test_register_agent():
    # Leea Token at Holesky 0x8cB8AB2a22a882032d277ae29B4c70F60444f95e
    # Leea DAO at Holesky 0x153E8ea256fDC02487882aa48A009D3573C25F99
    # Leea Agent Registry 0xe61461139682822a9033A28DDc35377A50edc52e
    # Owner 0xDB7B9cd59ebF909D2F29D0278162A17a43fBBb50
    connected: bool = inst.connect("https://eth-holesky.g.alchemy.com/v2/1izUATcVfjpS7adsi0n76hyx--yUbmA1")
    assert connected is True
    ok = inst.register("0xe61461139682822a9033A28DDc35377A50edc52e", 100, "GPT")
    assert ok is True

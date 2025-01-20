import leea_agent_sdk.web3 as web3

inst = web3.Web3Instance("leea_acc.json", "12345678")


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

from leea_agent_sdk.web3_solana import Web3InstanceSolana


def test_sign_verify():
    inst = Web3InstanceSolana("tests/unit/fixtures/id.json")
    message = b"The quick brown fox jumps over the lazy dog"
    sig = inst.sign_message(message)
    agent_id = inst.get_public_key()
    ver_res = inst.verify_message(agent_id, message, sig)
    assert ver_res is True


def test_connect():
    inst = Web3InstanceSolana("tests/unit/fixtures/id.json")
    assert inst.connect("https://api.devnet.solana.com") is True

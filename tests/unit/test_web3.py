import pytest
from leea_agent_sdk.web3 import Web3Instance
from web3 import Web3

@pytest.fixture
def inst():
    return Web3Instance("leea_acc.json", "12345678")


def test_create_wallet():
    inst().create_wallet()
    assert inst().account.address is not None, "address cant be empty"


def test_sign_verify():
    inst().create_wallet()
    sig: str = inst.sign_message("Hello World")
    ver: bool = inst.verify_message("Hello World", sig)
    assert ver is True


def test_connect():
    connected: bool = inst().connect("http://127.0.0.1:8545")
    assert connected is True

@pytest.fixture
def agent_registry_contract():
    with open(
        "./contracts/contracts/artifacts/aregistry/AgentRegistry.abi", "r"
    ) as abi_file:
        abi = abi_file.read().rstrip()
    with open(
        "./contracts/contracts/artifacts/aregistry/AgentRegistry.bin", "r"
    ) as bin_file:
        bin = bin_file.read()

    testW3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    testW3.eth.default_account = testW3.eth.accounts[0]
    registry = testW3.eth.contract(abi=abi, bytecode=bin)
    tx_hash = registry.constructor(inst.account.address, "0x153E8ea256fDC02487882aa48A009D3573C25F99").transact()
    tx_receipt =  testW3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress

def test_register_agent():
    # Leea Token at Holesky 0x8cB8AB2a22a882032d277ae29B4c70F60444f95e
    # Leea DAO at Holesky 0x153E8ea256fDC02487882aa48A009D3573C25F99
    # Leea Agent Registry 0xe61461139682822a9033A28DDc35377A50edc52e
    # Owner 0xDB7B9cd59ebF909D2F29D0278162A17a43fBBb50

    # connected: bool = inst.connect("https://eth-holesky.g.alchemy.com/v2/1izUATcVfjpS7adsi0n76hyx--yUbmA1")
    # assert connected is True
    # ok = inst().register("0xe61461139682822a9033A28DDc35377A50edc52e", 100, "GPT")
    # assert ok is True
   
    connected: bool = inst().connect("http://127.0.0.1:8545")
    assert connected is True
    ok = inst().register(agent_registry_contract(), 100, "GPT")
    assert ok is True
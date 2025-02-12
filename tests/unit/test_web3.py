import pytest
from leea_agent_sdk.web3 import Web3Instance
from web3 import Web3, EthereumTesterProvider

inst = Web3Instance("leea_acc.json", "12345678")

def test_create_wallet():
    inst.create_wallet()
    assert inst.account.address is not None, "address cant be empty"


def test_sign_verify():
    inst.create_wallet()
    sig: str = inst.sign_message("Hello World")
    ver: bool = inst.verify_message("Hello World", sig)
    assert ver is True

@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()


@pytest.fixture
def eth_tester(tester_provider):
    return tester_provider.ethereum_tester


@pytest.fixture
def w3(tester_provider):
    return Web3(tester_provider)


@pytest.fixture
def agent_registry_contract_address(w3) -> str:
    with open(
        "./contracts/contracts/artifacts/aregistry/AgentRegistry.abi", "r"
    ) as abi_file:
        abi = abi_file.read().rstrip()
    with open(
        "./contracts/contracts/artifacts/aregistry/AgentRegistry.bin", "r"
    ) as bin_file:
        bin = bin_file.read()
    w3.eth.default_account = w3.eth.accounts[0]
    registry = w3.eth.contract(abi=abi, bytecode=bin)
    tx_hash = registry.constructor(
        inst.account.address, "0x153E8ea256fDC02487882aa48A009D3573C25F99"
    ).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress


def test_register_agent_local(agent_registry_contract_address, w3):
    inst.set_web3_provider(w3)
    connected: bool = inst.connected()
    assert connected is True
    fee = 100
    name = "GPT"
    tx_hash = w3.eth.send_transaction(
        {
            "from": w3.eth.accounts[0],
            "to": inst.account.address,
            "value": inst.get_gas(
                contract_address=agent_registry_contract_address, fee=fee, name=name
            ),
        }
    )
    w3.eth.wait_for_transaction_receipt(tx_hash)
    ok = inst.register(
        contract_address=agent_registry_contract_address, fee=fee, name=name
    )
    assert ok is True
    # try to register again
    ok = inst.register(
        contract_address=agent_registry_contract_address, fee=fee, name=name
    )
    assert ok is False


# def test_register_agent_Holesky():
#     # Leea Token at Holesky 0x8cB8AB2a22a882032d277ae29B4c70F60444f95e
#     # Leea DAO at Holesky 0x153E8ea256fDC02487882aa48A009D3573C25F99
#     # Leea Agent Registry 0xe61461139682822a9033A28DDc35377A50edc52e
#     # Owner 0xDB7B9cd59ebF909D2F29D0278162A17a43fBBb50
#     connected: bool = inst.connect(
#         "https://eth-holesky.g.alchemy.com/v2/1izUATcVfjpS7adsi0n76hyx--yUbmA1"
#     )
#     assert connected is True
#     ok = inst.register("0xe61461139682822a9033A28DDc35377A50edc52e", 100, "GPT")
#     assert ok is True
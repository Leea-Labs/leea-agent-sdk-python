import pytest
from leea_agent_sdk.web3_evm import Web3InstanceEVM
from web3 import Web3, EthereumTesterProvider

inst = Web3InstanceEVM("wallet.json", "12345678")


@pytest.mark.skip("Will fix later")
def test_create_wallet():
    inst.create_wallet()
    assert inst.account.address is not None, "address cant be empty"


@pytest.mark.skip("Will fix later")
def test_sign_verify():
    public_key, sig = inst.sign_message("Hello World".encode())
    ver: bool = inst.verify_message("Hello World".encode(), sig)
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


@pytest.mark.skip("Will fix later")
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

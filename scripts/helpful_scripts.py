from brownie import accounts, network, config, TokenFarm, DappToken, Contract, MockV3Aggregator, MockWETH, MockDAI, MockERC20
from web3 import Web3

FORKED_CAHINS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_DEV_CHAINS = ["ganache-loc", "development"]

initiail_price_feed_value = Web3.toWei(2000, "ether")

def get_account(index=None, id=None):
    print(f"the network you are working on is : {network.show_active()}")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_DEV_CHAINS
        or network.show_active() in FORKED_CAHINS
    ):
        print(f"your account is :{accounts[0]}")
        return accounts[0]
    else:
        account = accounts.add(config["wallets"]["from_key"])    
        # print(f"your account is :{account}")
        return account

#----------------------------------------------------------------------------------------------
# (2)
def deploy_TokenFarm(account, dapp_token):
    if len(TokenFarm) <= 0:
        token_farm = TokenFarm.deploy(
            dapp_token.address, 
            {"from": account}, 
            publish_source=config["networks"][network.show_active()].get("verify", False),
        )
    else :
        token_farm = TokenFarm[-1]
    return token_farm
# (1)
def deploy_DappToken(account):
    if len(DappToken) <= 0:
            dapp_token = DappToken.deploy(
            {"from": account}, 
            publish_source=config["networks"][network.show_active()].get("verify", False),
        )
    else:
        dapp_token = DappToken[-1]
    return dapp_token
#----------------------------------------------------------------------------------------------

contract_to_mocks = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "weth_token": MockWETH,
    "fucat_token": MockDAI,
}

def get_contract(contract_name, account=None):
    contract_needed = contract_to_mocks[contract_name]
    if network.show_active() in LOCAL_DEV_CHAINS:
        if len(contract_needed) <= 0:
            deploy_mocks()
            contract = contract_needed[-1]
        contract = contract_needed[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_needed._name, contract_address, contract_needed.abi
        )
    return contract

Mock_DAI = MockDAI
Mock_WETH = MockWETH

def deploy_mocks(initialAnswer=initiail_price_feed_value, decimals=18):
    account = get_account()
    print("deploying Mocks...")
    print("deploying MockV3Aggregator...")
    mockV3aggrirator = MockV3Aggregator.deploy(decimals, initialAnswer, {"from": account})
    print("deploying MockWETH")
    MockWETH = Mock_WETH.deploy({"from": account})
    print("deploying MockDAI")
    MockDAI = Mock_DAI.deploy({"from": account})
    print("deploying MockERC20")
    Mock_erc20 = MockERC20.deploy({"from": account})
    print("All Mocks deployed.")
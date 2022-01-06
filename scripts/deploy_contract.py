import pytest
from brownie import TokenFarm, DappToken, network, config
from toolz.itertoolz import accumulate
from scripts.helpful_scripts import (
    LOCAL_DEV_CHAINS,
    get_account,
    get_contract,
    deploy_TokenFarm,
    deploy_DappToken,
)
from web3 import Web3
import yaml 
import json
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, "ether")
#  999900_000000000000000000 <- "contract" dapp balance
#     100_000000000000000000 <- "account" dapp balance
# 1000000_000000000000000000 <- initail token balance
# when deployed to testnet have to change this to 1 to avoid making TX twice !!!!!!!!!!
tx_time = 1  # <= !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ganache-cli -> DONE!
# ganache-loc -> DONE!
# kovan testnet -> testing!
# mainnet -> ...(no eth avilable!)
amount_staked = Web3.toWei(1, "ether")

def deploy_contracts():
    account = get_account(id="mehdisaccount")
    dapp_token = deploy_DappToken(account)
    print(f"dapp token address :{dapp_token.address}")
    token_farm = deploy_TokenFarm(account, dapp_token)
    print(f"token farm address :{token_farm.address}")
    transfer_dapp_tokens(dapp_token, token_farm, account)
    # allow 3 tokens : dapp_token, weth_token, fucat_token/DAI
    weth_token = get_contract("weth_token")
    fucat_token = get_contract("fucat_token")
    dic_of_allowed_tokens = {
        weth_token: get_contract("eth_usd_price_feed"),
        fucat_token: get_contract("dai_usd_price_feed"),
        dapp_token: get_contract("dai_usd_price_feed"),
    }
    # dapp_token: get_contract("dai_usd_price_feed"),
    add_allowed_tokens(token_farm, dic_of_allowed_tokens, account)
    if network.show_active() in ["kovan", "rinkeby"]:
        update_front_end()
    # -------------------------operating---------------------------
    print(dapp_token.balanceOf(account.address))

    # -------------------complited on kovan------------------------
    # 1\ deploy: TokenFarm\DappToken - DONE!
    # 2\ transfer DappToken to TokenFarm contract - DONE!
    # 3\ add 3 Allowed Tokens to be staked - DONE!
    #
    #
    # -------------------------------------------------------------
    return token_farm, dapp_token, weth_token, fucat_token


# ---------------------------------------------------------------------------------------------------------------
def update_front_end():
    # sending the front end our config in json format (hole folder)
    copy_folders_to_front_end("./build","./front_end/src/chain-info")
    # put all "brownie-config.yaml" data in a dictionary using pyyaml (just .yaml file)
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dic = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dic, brownie_config_json)
    print("  --front end-- is UPDATED!")

def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)

def transfer_dapp_tokens(dapp_token, token_farm, account):
    if network.show_active() in ["kovan"]:
        if tx_time == 0:
            tx_transfer_dapptokens = dapp_token.transfer(
                token_farm.address,
                dapp_token.totalSupply() - KEPT_BALANCE,
                {"from": account},
            )
            tx_transfer_dapptokens.wait(1)
        else:
            print(f"already did the TX: -transfer_dapp_tokens- {network.show_active()}")
        # then add 1 to tx_time!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if network.show_active() in LOCAL_DEV_CHAINS:
        if tx_time == 0:
            tx_transfer_dapptokens = dapp_token.transfer(
                token_farm.address,
                dapp_token.totalSupply() - KEPT_BALANCE,
                {"from": account},
            )
            tx_transfer_dapptokens.wait(1)
        else:
            print(f"already did the TX: -transfer_dapp_tokens- {network.show_active()}")


def add_allowed_tokens(tokenFarm, dic_of_allowed_tokens, account):
    if network.show_active() in ["kovan"]:
        if tx_time == 0:
            for token in dic_of_allowed_tokens:
                tx = tokenFarm.addAllowedTokens(
                    token.address, dic_of_allowed_tokens[token], {"from": account}
                )
                tx.wait(1)
        else:
            print(f"already did the TX: -add_allowed_tokens- {network.show_active()}")
        # then add 1 to tx_time!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if network.show_active() in LOCAL_DEV_CHAINS:
        if tx_time == 0:
            for token in dic_of_allowed_tokens:
                tx = tokenFarm.addAllowedTokens(
                    token.address, dic_of_allowed_tokens[token], {"from": account}
                )
                tx.wait(1)
        else:
            print(f"already did the TX: -add_allowed_tokens- {network.show_active()}")


def main():
    deploy_contracts()


# -------------------------------------tests--------------------------------------------

# ---------------------------------------------------------------------------------------

from brownie import network, exceptions
import pytest
from scripts.helpful_scripts import get_account, LOCAL_DEV_CHAINS, initiail_price_feed_value
from scripts.deploy_contract import deploy_contracts, amount_staked

def arrange():
    if network.show_active() not in LOCAL_DEV_CHAINS:
        pytest.skip("only for Local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token, weth_token, fucat_token = deploy_contracts()
    return account, non_owner, token_farm, dapp_token, weth_token, fucat_token

def test_stake_issue_and_unstake():
    # test:
    # 1\ stake two tokens from two deferent accounts.
    # 2\ issue dapp tokens to the stakers.
    # 3\ test the dapp tokens arrives to the stakers accounts -> TEST!!\testing...\PASSED!
    # 4\ unstake tokens of the stakers from two deferent accounts.
    # 6\ test the account have recived the initail staked tokens -> TEST!!\testing...\PASSED!
    # arrange 
    account, non_owner, token_farm, dapp_token, weth_token, fucat_token = arrange()
    # act => working on ganache-loc => every act is saved (keep in mind)
    initial_account_balance_dapp = dapp_token.balanceOf(account.address)
    initial_account2_balance_dapp = dapp_token.balanceOf(non_owner)
    initial_account2_balance_weth = weth_token.balanceOf(non_owner)
    tx_issue_tokens = token_farm.issueTokens({"from": account})
    tx_issue_tokens.wait(1)
    tx_unstake_account = token_farm.unstakeTokens(dapp_token.address, {"from": account})
    tx_unstake_account.wait(1)
    tx_unstake_account2 = token_farm.unstakeTokens(weth_token.address, {"from": non_owner})
    tx_unstake_account2.wait(1)
    # assert 
    assert dapp_token.balanceOf(account.address) == initial_account_balance_dapp + amount_staked + initiail_price_feed_value
    assert weth_token.balanceOf(non_owner.address) == initial_account2_balance_weth + amount_staked
    assert dapp_token.balanceOf(non_owner.address) == initiail_price_feed_value
    
    
    
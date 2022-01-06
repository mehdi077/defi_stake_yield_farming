from os import link
from brownie import network, exceptions
from scripts.helpful_scripts import LOCAL_DEV_CHAINS, get_account, get_contract, initiail_price_feed_value
from scripts.deploy_contract import deploy_contracts
import pytest

def arrange():
    if network.show_active() not in LOCAL_DEV_CHAINS:
        pytest.skip("only for Local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token, weth_token, fucat_token = deploy_contracts()
    return account, non_owner, token_farm, dapp_token
    

def test_price_feed_contract():
    # arrange
    account, non_owner, token_farm, dapp_token = arrange()
    # act
    price_feed_address = get_contract("dai_usd_price_feed")
    # tx = token_farm.addAllowedTokens(dapp_token.address, price_feed_address, {"from": account})
    # tx.wait(1)
    # assert 
    assert token_farm.tokenPriceFeedAddress(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        tx_non_owner = token_farm.addAllowedTokens(dapp_token.address, price_feed_address, {"from": non_owner})
        tx_non_owner.wait(1)
    assert token_farm.allowedTokens(2) == dapp_token.address
    return account, non_owner, token_farm, dapp_token

def test_stakeTokens(amount_staked):
    # test stakingBalance of the staker will become the amount staked - (1) TEST!!\testing...\PASSED!
    # test that uinqutokensStaked of the staker will becom > 0 - (2) TEST!!\testing...\PASSED!
    # the staker is added to the stakers list  - (3) TEST!!\testing...\PASSED!
    # if we put a token that is not allowed it would revert - (4) TEST!!\testing...\PASSED!
    # if we put 0 amount it would revert (5) TEST!!\testing...\PASSED!
    # the staker is not in the stakers list twice after we stake again the same token but deferent amount - (6) TEST!!\testing...\PASSED!
    #------------------------------------------------------------------------------------------------------------------
    # arrange 
    account, non_owner, token_farm, dapp_token = test_price_feed_contract()
    # act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    # assert 
    assert token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked # 1
    assert token_farm.uinqutokensStaked(account.address) == 1 # 2
    assert token_farm.stakers(0) == account.address # 3
    # with pytest.raises(exceptions.VirtualMachineError): # 4
    #     token_farm.stakeTokens(amount_staked, weth_token.address, {"from": account})
    # with pytest.raises(exceptions.VirtualMachineError): # 5
    #     token_farm.stakeTokens(0, dapp_token.address, {"from": account})
    # dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    # token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    # with pytest.raises(exceptions.VirtualMachineError):
    #     token_farm.stakers(1) == account.address
    return account, non_owner, token_farm, dapp_token 
    

def test_issue_tokens(amount_staked):
    # tests :
    # test the staker will recive 1:1 the value of the token he staked (dappToken) on top of 
    # what he already has. - TEST!!\testing...\PASSED!
    # 
    # test the function will revert if it's not the owner who calls is. - TEST!!\testing...\PASSED!
    #-----------------------------------------------------------------
    # arrange
    account, non_owner, token_farm, dapp_token = test_stakeTokens(amount_staked)
    initial_account_balance = dapp_token.balanceOf(account.address)
    initail_contract_balance = dapp_token.balanceOf(token_farm.address)
    # act
    token_farm.issueTokens({"from": account})
    # assert 
    assert dapp_token.balanceOf(account.address) == initial_account_balance + initiail_price_feed_value
    assert dapp_token.balanceOf(token_farm.address) == initail_contract_balance - initiail_price_feed_value
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.issueTokens({"from": non_owner})
    return account, non_owner, token_farm, dapp_token

def test_unstake_token(amount_staked):
    # test:
    # 1\ when unstak the balance of the unstaked token should = 0 -> TEST!!\testing...\PASSED!
    # 2\ the amount transfered to the account should be initial balance + transfered balance -> TEST!!\testing...\PASSED!
    # 3\ uinqutokensStaked should be - 1 -> TEST!!\testing...\PASSED!
    # 4\ the unstaker should not be in stakers list -> TEST!!\testing...\PASSED!
    # 5\ test can't call removeFromStakers -> TEST!!\testing...\PASSED!
    # 6\ can't unstake if the caller doesen't have any token staked -> TEST!!\testing...\PASSED!
    #-------------------------------------------------------------------------------------------------
    # arrange
    account, non_owner, token_farm, dapp_token = test_issue_tokens(amount_staked)
    # act
    initail_account_balance = dapp_token.balanceOf(account.address)
    initial_uinqutokensStaked = token_farm.uinqutokensStaked(account.address)
    token_farm.unstakeTokens(dapp_token.address, {"from": account})
    # assert
    assert token_farm.stakingBalance(dapp_token.address, account.address) == 0
    assert dapp_token.balanceOf(account.address) == initail_account_balance + amount_staked
    assert token_farm.uinqutokensStaked(account.address) == initial_uinqutokensStaked - 1
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.stakers(0) == account.address
    # with pytest.raises(exceptions.VirtualMachineError):
    #     token_farm.removeFromStakers({"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.unstakeTokens(dapp_token.address, {"from": non_owner})
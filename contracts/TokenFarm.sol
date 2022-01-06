// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts v4.4.1 (proxy/transparent/ProxyAdmin.sol)

pragma solidity ^0.7.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.7/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    // staketoken - DONE!
    // unstaketokens - DONE!
    // issueTOkens - DONE!
    //// => eth/dai conversionrate
    // addAllowedTokens - DONE!
    // getValue - DONE!
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uinqutokensStaked;
    mapping(address => address) public tokenPriceFeedAddress;
    address[] public allowedTokens;
    address[] public stakers;
    address[] internal temp_list;
    address[] internal unstakers;
    uint256 public numberOfAllowedTokens;
    IERC20 public dappToken;
    
    //------------------------------------------Constructor-----------------------------------------------    
    constructor(address _dappTokenAddress) public {
        dappToken = IERC20(_dappTokenAddress);
    }

    //---------------------------------------add Allowed Tokens----------------------------------------------
    function addAllowedTokens(address _token, address _priceFeed)
        public
        onlyOwner
    {
        allowedTokens.push(_token);
        tokenPriceFeedAddress[_token] = _priceFeed;
        numberOfAllowedTokens = numberOfAllowedTokens + 1;
    }

    //-------------------------------------------Issue Tokens------------------------------------------
    function issueTokens() public onlyOwner {
        for (uint256 i = 0; i < stakers.length; i++) {
            address staker = stakers[i];
            uint256 userTotalValue = getUserTotalValue(staker);
            // send them a token reward based on the total value locked
            // we already have Dapp tokens in the contract
            dappToken.transfer(staker, userTotalValue);
        }
    }

    function getUserTotalValue(address _staker) public view returns (uint256) {
        uint256 totalvalue = 0;
        require(uinqutokensStaked[_staker] > 0, "you have nothing staked, get out!");
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            totalvalue =
                totalvalue +
                getUserSingleTokenValue(_staker, allowedTokens[i]);
        }
        return totalvalue;
    }

    // defently test this 
    function getUserSingleTokenValue(address _staker, address _token)
        public
        view
        returns (uint256)
    {
        if (uinqutokensStaked[_staker] <= 0) {
            return 0;
        }
        // the price of the token * uinqutokensStaked[_staker]
        (uint256 token_price, uint256 decimals) = getTokenPrice(_token);
        return (token_price * stakingBalance[_token][_staker] / (10**decimals));
    }

    function getTokenPrice(address _token) public view returns (uint256, uint256) {
        address priceFeedAddress = tokenPriceFeedAddress[_token];
        AggregatorV3Interface priceFeedI = AggregatorV3Interface(priceFeedAddress);
        (, int256 price, , , ) = priceFeedI.latestRoundData();
        uint256 decimals = uint256(priceFeedI.decimals());
        return (uint256(price), decimals);
    }

    //-----------------------------------------Stake Tokens--------------------------------------------
    function stakeTokens(uint256 _amount, address _token) public {
        require(_amount > 0, "amount should be greater than 0");
        require(tokenIsAllowed(_token), "this token cerruntly is not allowed");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        uint256 initial_amount = stakingBalance[_token][msg.sender];
        newTokenAddedToStaker(msg.sender, _token);
        stakingBalance[_token][msg.sender] =
            stakingBalance[_token][msg.sender] +
            _amount;
        if (uinqutokensStaked[msg.sender] == 1) {
            if (initial_amount == 0) {
                stakers.push(msg.sender);
            }
        }
    }

    function tokenIsAllowed(address _token) public returns (bool) {
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == _token) {
                return true;
            }
        }
        return false;
    }

    function newTokenAddedToStaker(address _staker, address _token) internal {
        if (stakingBalance[_token][_staker] <= 0) {
            uinqutokensStaked[_staker] = uinqutokensStaked[_staker] + 1;
        }
    }

    //-------------------------------------------Unstake Tokens------------------------------------------
    function unstakeTokens(address _token) public {
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "you have nothing staked here ,fuck you!");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
        uinqutokensStaked[msg.sender] = uinqutokensStaked[msg.sender] - 1;
        removeFromStakers(msg.sender);
    }

    // test this later added by me
    function removeFromStakers(address _unstaker) internal {
        for (uint256 i = 0; i < stakers.length; i++){
            if (stakers[i] == _unstaker){
                unstakers.push(_unstaker);
            }
            else {
                temp_list.push(stakers[i]);
            }
        }
        delete stakers;
        for (uint256 i = 0; i < temp_list.length; i++){
            stakers.push(temp_list[i]);
        }
    }

    

}

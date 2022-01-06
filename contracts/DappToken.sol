// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts v4.4.1 (proxy/transparent/ProxyAdmin.sol)

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {
    address owner;
    constructor() public ERC20("Dapp Token", "DAPP") {
        _mint(msg.sender, 1000000000000000000000000);
        owner = msg.sender;
    }
}
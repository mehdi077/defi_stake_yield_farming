// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts v4.4.1 (proxy/transparent/ProxyAdmin.sol)

pragma solidity ^0.7.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockWETH is ERC20 {
    address owner;
    constructor() public ERC20("MOCK WETH", "MWETH") {
        _mint(msg.sender, 1000000000000000000000000);
        owner = msg.sender;
    }
}
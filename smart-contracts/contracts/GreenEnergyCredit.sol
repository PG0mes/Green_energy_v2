// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract GreenEnergyCredit is ERC20, Ownable {
    // CORREÇÃO: Na v4 da OpenZeppelin, o construtor do Ownable é chamado sem argumentos.
    constructor(address initialOwner) ERC20("GreenEnergyCredit", "GEC") {
        // CORREÇÃO: A propriedade é então transferida para o `initialOwner` aqui dentro do construtor.
        _transferOwnership(initialOwner);
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}
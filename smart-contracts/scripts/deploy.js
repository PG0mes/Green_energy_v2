import hre from "hardhat";

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Fazendo deploy do contrato com a conta:", deployer.address);

  const GreenEnergyCredit = await hre.ethers.getContractFactory("GreenEnergyCredit");
  console.log("Iniciando o deploy do GreenEnergyCredit...");

  const gecToken = await GreenEnergyCredit.deploy(deployer.address);

  // --- CORREÇÃO AQUI ---
  // Usando o método moderno para aguardar a confirmação do deploy
  await gecToken.waitForDeployment(); 

  // O método para obter o endereço também foi atualizado
  const contractAddress = await gecToken.getAddress();
  console.log(`Contrato "GreenEnergyCredit" publicado com sucesso no endereço: ${contractAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
from web3 import Web3

INFURA_URL = os.getenv("INFURA_URL")
MetaMask_Private = os.getenv("MetaMask_Private")

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(MetaMask_Private)

print("✅ Wallet Address:", account.address)
print("💰 Balance:", w3.eth.get_balance(account.address) / 1e18, "SepoliaETH")
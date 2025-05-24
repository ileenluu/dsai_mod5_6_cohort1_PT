from web3 import Web3

INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

print("✅ Wallet Address:", account.address)
print("💰 Balance:", w3.eth.get_balance(account.address) / 1e18, "SepoliaETH")
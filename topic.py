from eth_utils import keccak, encode_hex

# Event signature as string
event_signature = "Swap(address,address,uint256,uint256,uint256,uint256)"

# Compute Keccak-256 hash
topic0 = encode_hex(keccak(text=event_signature))

print(topic0)
